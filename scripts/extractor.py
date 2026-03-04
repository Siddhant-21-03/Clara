"""
Clara Answers - Transcript Extraction Engine
=============================================
Rule-based NLP extraction from demo and onboarding call transcripts.
Extracts structured account data without requiring paid LLM APIs.
"""

import re
import json
import os
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any

from config import (
    EMERGENCY_KEYWORDS, SERVICE_KEYWORDS, TIMEZONE_MAPPINGS,
    DAYS_OF_WEEK, DEFAULT_TRANSFER_TIMEOUT
)

logger = logging.getLogger(__name__)


class TranscriptExtractor:
    """Rule-based extractor for demo and onboarding call transcripts."""

    def __init__(self):
        self.phone_pattern = re.compile(
            r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})'
        )
        self.time_pattern = re.compile(
            r'(?<!\d)(?<![-/])(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm|a\.m\.|p\.m\.)?)\s*(?:to|through)\s*'
            r'(\d{1,2}(?::\d{2})?\s*(?:AM|PM|am|pm|a\.m\.|p\.m\.)?)(?!\d)',
            re.IGNORECASE
        )
        self.timeout_pattern = re.compile(
            r'(\d+)\s*seconds?',
            re.IGNORECASE
        )
        self.address_pattern = re.compile(
            r'(\d+\s+(?:[A-Z][a-z]+\s+)+(?:Street|St|Avenue|Ave|Boulevard|Blvd|Road|Rd|Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl)\.?(?:\s*,\s*(?:Suite|Ste|Unit|Apt|#)\s*\w+)?'
            r'\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s*,\s*[A-Z]{2,}\s*,?\s*\d{5}(?:-\d{4})?)',
            re.IGNORECASE
        )

    def extract_company_name(self, text: str) -> Optional[str]:
        """Extract company name from transcript header or body."""
        # Check header pattern: [... - CompanyName]
        header_match = re.search(r'\[.*?-\s*(.+?)\]', text)
        if header_match:
            return header_match.group(1).strip()

        # Look for patterns like "So we're CompanyName" or "CompanyName is a..."
        patterns = [
            r'(?:we\'re|we are|this is|I\'m with|company is|called)\s+([A-Z][A-Za-z\s&.]+?)(?:\s*(?:is|and|based|\.|,|—))',
            r'([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,4})\s+(?:is an?|handles|does|provides)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                if len(name) > 3 and name not in ["The", "This", "That", "Our"]:
                    return name
        return None

    def extract_business_hours(self, text: str) -> Dict[str, Any]:
        """Extract business hours, days, and timezone."""
        hours_info = {
            "days": [],
            "start": None,
            "end": None,
            "timezone": None,
            "saturday_hours": None,
            "notes": []
        }

        # Extract timezone
        text_lower = text.lower()
        for tz_key, tz_value in TIMEZONE_MAPPINGS.items():
            if tz_key in text_lower:
                hours_info["timezone"] = tz_value
                break

        # Special handling for cities
        city_tz = {
            "tampa": "America/New_York",
            "chicago": "America/Chicago",
            "phoenix": "America/Phoenix",
            "atlanta": "America/New_York",
            "dallas": "America/Chicago",
            "houston": "America/Chicago",
            "san antonio": "America/Chicago",
            "new york": "America/New_York",
            "los angeles": "America/Los_Angeles",
        }
        for city, tz in city_tz.items():
            if city in text_lower and not hours_info["timezone"]:
                hours_info["timezone"] = tz

        # Extract time ranges
        time_matches = self.time_pattern.findall(text)
        if time_matches:
            hours_info["start"] = self._normalize_time(time_matches[0][0], is_end_time=False)
            hours_info["end"] = self._normalize_time(time_matches[0][1], is_end_time=True)

            # Check for Saturday hours (separate time range)
            if len(time_matches) > 1:
                sat_start = self._normalize_time(time_matches[1][0], is_end_time=False)
                sat_end = self._normalize_time(time_matches[1][1], is_end_time=True)
                hours_info["saturday_hours"] = {
                    "start": sat_start,
                    "end": sat_end
                }

        # Extract days
        if re.search(r'monday\s+through\s+friday|mon\s*-\s*fri|weekdays', text_lower):
            hours_info["days"] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

        if re.search(r'monday\s+through\s+saturday|mon\s*-\s*sat', text_lower):
            hours_info["days"] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        # Check for Saturday
        if re.search(r'saturday.*(?:open|hours|crew|half\s*day)', text_lower):
            if "Saturday" not in hours_info["days"]:
                hours_info["days"].append("Saturday")
                if "half day" in text_lower or "half-day" in text_lower:
                    hours_info["notes"].append("Saturday is half day")

        # Check for closed days
        if re.search(r'(?:sunday|weekends?).*(?:closed|off|no|after.?hours)', text_lower):
            hours_info["notes"].append("Sunday closed / after-hours only")

        if re.search(r'(?:saturday|weekends?).*(?:closed|off)', text_lower):
            if "Saturday" in hours_info["days"]:
                hours_info["days"].remove("Saturday")
            hours_info["notes"].append("Saturday closed / after-hours only")

        return hours_info

    def extract_services(self, text: str) -> List[str]:
        """Extract list of services offered by the company."""
        services = []
        text_lower = text.lower()

        for service_category, keywords in SERVICE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Map to cleaner service name
                    service_name = service_category.replace("_", " ").title()
                    if service_name not in services:
                        services.append(service_name)
                    break

        # Also look for specific mentions (with context to reduce false positives)
        specific_services = [
            (r'fire sprinkler|sprinkler system|sprinkler inspection|sprinkler install', "Fire Sprinkler Systems"),
            (r'fire alarm|alarm system|alarm monitoring', "Fire Alarm Systems"),
            (r'fire extinguisher', "Fire Extinguisher Service"),
            (r'backflow testing|backflow preventer|backflow certification', "Backflow Testing"),
            (r'kitchen hood|hood suppression|restaurant hood', "Kitchen Hood Suppression"),
            (r'generator\s+(?:maintenance|service|repair|install)', "Generator Maintenance"),
            (r'lighting\s+(?:service|install|retrofit|upgrade)', "Lighting Services"),
            (r'panel\s+upgrade|electrical\s+panel', "Electrical Panel Upgrades"),
            (r'refrigeration\s+(?:service|repair|unit|system)', "Refrigeration"),
            (r'plumbing\s+(?:service|contractor|repair|work)', "Plumbing"),
            (r'janitorial|cleaning\s+service', "Janitorial"),
            (r'elevator\s+(?:service|maintenance|repair)', "Elevator Service"),
            (r'roof\s+(?:maintenance|repair|inspection)', "Roof Maintenance"),
        ]

        for pattern, service_name in specific_services:
            if re.search(pattern, text_lower):
                if service_name not in services:
                    services.append(service_name)

        return services

    def extract_emergency_definitions(self, text: str) -> List[str]:
        """Extract what constitutes an emergency for this client."""
        emergencies = []
        text_lower = text.lower()

        # Look for sentences near "emergency" or emergency-related context
        sentences = re.split(r'[.!?\n]', text)
        in_emergency_context = False

        for sentence in sentences:
            sent_lower = sentence.lower().strip()

            # Check if we're in an emergency definition context
            if any(phrase in sent_lower for phrase in [
                "emergency is", "emergency would be", "constitute an emergency",
                "emergencies", "emergency triggers", "drop-everything",
                "immediate response", "treat as emergency", "emergency categories",
                "define emergenc"
            ]):
                in_emergency_context = True

            if any(phrase in sent_lower for phrase in [
                "non-emergency", "not an emergency", "can wait", "not urgent",
                "never an emergency"
            ]):
                in_emergency_context = False

            if in_emergency_context or any(kw in sent_lower for kw in [
                "burst", "leak", "discharge", "failure", "fire",
                "flooding", "outage", "sparking", "entrapment",
                "gas leak", "offline", "exposed"
            ]):
                # Extract the emergency trigger
                triggers = self._extract_emergency_triggers(sentence)
                for trigger in triggers:
                    if trigger and trigger not in emergencies and len(trigger) > 5:
                        emergencies.append(trigger)

        return emergencies

    def _extract_emergency_triggers(self, sentence: str) -> List[str]:
        """Parse individual emergency triggers from a sentence."""
        triggers = []
        sentence = sentence.strip()
        if not sentence:
            return triggers

        # Common emergency patterns
        patterns = [
            r'sprinkler (?:head )?(?:discharge|leak)',
            r'active fire alarm',
            r'fire alarm (?:panel )?(?:offline|in trouble|sounding)',
            r'fire pump failure',
            r'fire suppression system.*?offline',
            r'(?:complete |total )?power outage',
            r'sparking|arcing',
            r'exposed (?:live )?wir(?:es|ing)',
            r'generator failure',
            r'electrical fire|burning smell',
            r'burst pipe',
            r'(?:active )?flooding',
            r'sewage backup',
            r'no (?:hot )?water.*?(?:medical|restaurant)',
            r'no heat.*?(?:commercial|building)',
            r'no ac.*?(?:critical|server|medical|restaurant)',
            r'(?:total )?(?:hvac|system) failure',
            r'gas leak',
            r'co (?:detector )?alarm|carbon monoxide',
            r'refrigeration failure',
            r'elevator entrapment',
            r'roof leak.*?(?:damage|active)',
            r'kitchen hood.*?discharge',
            r'trouble (?:signal|beep)',
            r'structural damage',
            r'safety hazard',
        ]

        sent_lower = sentence.lower()
        for pattern in patterns:
            match = re.search(pattern, sent_lower)
            if match:
                trigger = match.group(0).strip()
                trigger = trigger[0].upper() + trigger[1:]
                if trigger not in triggers:
                    triggers.append(trigger)

        # If no patterns matched but sentence contains emergency keywords, use the sentence
        if not triggers and any(kw in sent_lower for kw in ["emergency", "immediate", "critical"]):
            # Filter out conversational noise / questions
            noise_phrases = [
                "what situations", "what would", "what do you consider",
                "define emergenc", "treat as emergency", "emergency or no",
                "emergency is when", "emergency would be", "emergency categories",
                "never an emergency", "not an emergency", "isn't an emergency",
                "fire extinguisher stuff", "auto-created", "servicetrade",
                "flag that as", "high priority", "someone mentions",
            ]
            if any(noise in sent_lower for noise in noise_phrases):
                return triggers
            # Clean up the sentence
            cleaned = re.sub(r'^\s*[-•●]\s*', '', sentence).strip()
            # Remove speaker prefixes like "Mike Johnson:"
            cleaned = re.sub(r'^[A-Z][a-z]+\s+[A-Z][a-z]+:\s*', '', cleaned).strip()
            if 10 < len(cleaned) < 150:
                triggers.append(cleaned)

        return triggers

    def extract_phone_numbers(self, text: str) -> List[Dict[str, str]]:
        """Extract phone numbers with associated context (who/what)."""
        phones = []
        lines = text.split('\n')

        for line in lines:
            numbers = self.phone_pattern.findall(line)
            for number in numbers:
                normalized = re.sub(r'[-.\s]', '-', number)
                context = self._get_phone_context(line, number)
                phones.append({
                    "number": normalized,
                    "context": context,
                    "raw_line": line.strip()
                })

        return phones

    def _get_phone_context(self, line: str, number: str) -> str:
        """Determine who/what a phone number belongs to."""
        line_lower = line.lower()

        if "on-call" in line_lower or "on call" in line_lower:
            return "on_call"
        if "dispatch" in line_lower:
            return "dispatch"
        if "main" in line_lower or "office" in line_lower:
            return "main_office"
        if "cell" in line_lower or "mobile" in line_lower:
            return "cell"
        if "emergency" in line_lower:
            return "emergency"
        if "plumbing" in line_lower:
            return "plumbing_on_call"
        if "hvac" in line_lower:
            return "hvac_on_call"
        if "electrical" in line_lower:
            return "electrical_on_call"
        if "elevator" in line_lower:
            return "elevator_emergency"
        if "general" in line_lower:
            return "general_dispatch"
        if "backup" in line_lower:
            return "backup"

        return "unknown"

    def extract_routing_rules(self, text: str) -> Dict[str, Any]:
        """Extract call routing rules - emergency and non-emergency."""
        routing = {
            "emergency": {
                "contacts": [],
                "fallback": None,
                "callback_promise": None
            },
            "non_emergency": {
                "during_hours": None,
                "after_hours": None
            },
            "business_hours": {
                "contacts": [],
                "fallback": None
            }
        }

        lines = text.split('\n')
        phones = self.extract_phone_numbers(text)

        # Extract transfer timeouts
        timeout_sections = re.findall(
            r'(?:give.*?|wait.*?|timeout.*?|within\s+)(\d+)\s*seconds?',
            text, re.IGNORECASE
        )

        # Build contact chain for emergency routing
        emergency_section = self._find_section(text, [
            "emergency routing", "emergency calls", "after.?hours emergency",
            "on-call", "emergency.*?who should",
            "after hours emergencies", "here'?s how it works",
            r"how should clara route", r"for\s+\w+:.*call"
        ], window=25)

        if emergency_section:
            contacts = self._extract_contact_chain(emergency_section)
            routing["emergency"]["contacts"] = contacts

            # Extract fallback chain from lines like "fall back to X, try Y"
            fallback_parts = []
            for line in emergency_section.split('\n'):
                line_lower = line.lower()
                if re.search(r'fall\s*back|if .* doesn.?t answer|if nobody', line_lower):
                    # Split line into segments around each phone to attribute names correctly
                    phones_in_line = list(self.phone_pattern.finditer(line))
                    for idx, phone_match in enumerate(phones_in_line):
                        phone = re.sub(r'[-.\s]', '-', phone_match.group(0))
                        # Use the text segment leading up to this phone for name/role
                        seg_start = phones_in_line[idx - 1].end() if idx > 0 else 0
                        segment = line[seg_start:phone_match.end()]
                        name = self._extract_name_from_line(segment)
                        role = self._extract_role_from_line(segment)
                        fallback_parts.append(f"{name or role or 'Backup'} ({phone})")
            if fallback_parts:
                routing["emergency"]["fallback"] = "Fallback chain: " + " -> ".join(fallback_parts)

        # Extract callback promise
        callback_match = re.search(
            r'(?:call\s*back|callback|respond)\s+within\s+(\d+)\s*(minutes?|hours?)',
            text, re.IGNORECASE
        )
        if callback_match:
            amount = callback_match.group(1)
            unit = callback_match.group(2)
            routing["emergency"]["callback_promise"] = f"{amount} {unit}"

        # Extract business hours routing
        bh_section = self._find_section(text, [
            "during business hours", "during hours", "business hours routing"
        ])
        if bh_section:
            contacts = self._extract_contact_chain(bh_section)
            routing["business_hours"]["contacts"] = contacts

        # Non-emergency after hours
        non_emerg_section = self._find_section(text, [
            "non-emergency", "non emergency", "not an emergency",
            "can wait", "not urgent"
        ])
        if non_emerg_section:
            routing["non_emergency"]["after_hours"] = self._summarize_non_emergency(non_emerg_section)

        return routing

    def _find_section(self, text: str, markers: List[str], window: int = 15) -> Optional[str]:
        """Find a section of text near given marker phrases.
        
        Returns the section among all marker matches that contains the most
        phone numbers, so that we don't accidentally match a conversational
        mention far from the actual routing details.
        """
        lines = text.split('\n')
        candidates = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            for marker in markers:
                if re.search(marker, line_lower):
                    start = max(0, i)
                    end = min(len(lines), i + window)
                    section = '\n'.join(lines[start:end])
                    phone_count = len(self.phone_pattern.findall(section))
                    candidates.append((phone_count, i, section))
        if not candidates:
            return None
        # Return the section with the most phone numbers; ties broken by position
        candidates.sort(key=lambda x: (-x[0], x[1]))
        return candidates[0][2]

    def _extract_contact_chain(self, text: str) -> List[Dict[str, Any]]:
        """Extract ordered list of contacts from routing description.
        
        Handles both:
        - One-contact-per-line format: "For plumbing: call X at 214-555-0301."
        - Multi-contact single line: "Try Danny at 813-555-0147. If no answer, try Mike at 813-555-0199."
        """
        contacts = []
        lines = text.split('\n')
        priority = 1
        found_first = False

        for line in lines:
            line_lower = line.lower()

            # Stop at section boundaries — new speaker topic about BH or non-emergency
            if found_first and re.search(
                r'(?:^|[.:]\s*)\s*(?:during (?:business )?hours|non-?emergency|business hours routing)',
                line_lower
            ):
                break

            all_phones = list(self.phone_pattern.finditer(line))
            if not all_phones:
                continue

            # For lines that are purely fallback instructions with no primary contact
            # (e.g. "If the trade-specific line doesn't answer, fall back to...")
            # only skip if the line STARTS with a fallback phrase and has no
            # primary contact before it
            is_pure_fallback = bool(re.match(
                r'\s*(?:if (?:the |nobody|no one|that)|fall\s*back)',
                line_lower
            ))
            if is_pure_fallback:
                continue

            # Extract each phone on the line as a contact
            for phone_match in all_phones:
                phone = re.sub(r'[-.\s]', '-', phone_match.group(0))

                # Get the text segment around this phone for name/role extraction
                # Use text from previous phone end (or line start) to this phone end
                seg_start = 0
                for prev in all_phones:
                    if prev.start() < phone_match.start():
                        seg_start = prev.end()
                segment = line[seg_start:phone_match.end() + 20]

                timeout_match = re.search(r'(\d+)\s*seconds?', segment, re.IGNORECASE)
                if not timeout_match:
                    # Also check text after this phone on the same line
                    after_phone = line[phone_match.end():phone_match.end() + 60]
                    timeout_match = re.search(r'(\d+)\s*seconds?', after_phone, re.IGNORECASE)
                timeout = int(timeout_match.group(1)) if timeout_match else DEFAULT_TRANSFER_TIMEOUT

                name = self._extract_name_from_line(segment)
                role = self._extract_role_from_line(segment)

                # Handle trade-specific lines like "For plumbing: call ..."
                trade_match = re.match(
                    r'\s*[Ff]or\s+([\w/ ]+?):\s+call',
                    line
                )
                if trade_match and not role:
                    trade = trade_match.group(1).strip().lower()
                    role = f"{trade} on-call"

                found_first = True
                contacts.append({
                    "priority": priority,
                    "name": name,
                    "phone": phone,
                    "role": role,
                    "timeout_seconds": timeout
                })
                priority += 1

        return contacts

    def _extract_name_from_line(self, line: str) -> Optional[str]:
        """Extract a person's name from a line of text."""
        # Look for patterns like "Name LastName" or single first name near phone/role words
        name_patterns = [
            r'(?:try|call|reach|contact|that\'s)\s+(?:our\s+)?(?:\w+\s+)?([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)(?:,|\s+at\s+|\s+\d)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)(?:\'s|\'s)',
            r'(?:try|reach|contact)\s+([A-Z][a-z]{2,})\s+at\s+\d',
        ]
        for pattern in name_patterns:
            match = re.search(pattern, line)
            if match:
                name = match.group(1).strip()
                # Filter out false positives
                skip_words = ["Fire", "Main", "After", "During", "Clara", "Service",
                              "Monday", "Tuesday", "Wednesday", "Thursday", "Friday",
                              "Saturday", "Sunday", "Mountain Standard"]
                if not any(name.startswith(sw) for sw in skip_words):
                    return name
        return None

    def _extract_role_from_line(self, line: str) -> Optional[str]:
        """Extract a role/title from a line.
        
        More specific roles must appear before generic ones to avoid
        early matching (e.g. 'plumbing on-call' before 'on-call').
        """
        line_lower = line.lower()
        # Ordered: specific first, generic last
        roles = [
            ("plumbing on-call", ["plumbing on-call", "plumbing on call", "plumbing on-call"]),
            ("hvac on-call", ["hvac on-call", "hvac on call"]),
            ("electrical on-call", ["electrical on-call", "electrical on call"]),
            ("elevator emergency", ["elevator entrapment", "elevator emergency"]),
            ("general dispatch", ["general dispatch", "general/other"]),
            ("on-call tech", ["on-call tech", "on call tech", "on-call technician"]),
            ("on-call", ["on-call", "on call"]),
            ("dispatch manager", ["dispatch manager"]),
            ("dispatch", ["dispatch"]),
            ("owner", ["owner"]),
            ("office manager", ["office manager"]),
            ("lead technician", ["lead tech"]),
            ("general manager", ["general manager"]),
            ("operations manager", ["operations manager"]),
        ]
        for role, keywords in roles:
            for kw in keywords:
                if kw in line_lower:
                    return role
        return None

    def _summarize_non_emergency(self, text: str) -> str:
        """Create summary of non-emergency handling."""
        text_lower = text.lower()
        parts = []

        if "collect" in text_lower:
            parts.append("Collect caller information")
        if "name" in text_lower and "number" in text_lower:
            parts.append("Get name and callback number")
        if "next business day" in text_lower:
            parts.append("Promise callback next business day")
        if re.search(r'by\s+\d+\s*(?:am|pm)', text_lower):
            time_match = re.search(r'by\s+(\d+\s*(?:AM|PM|am|pm))', text)
            if time_match:
                parts.append(f"Promise callback by {time_match.group(1)}")
        if "don't transfer" in text_lower or "no transfer" in text_lower:
            parts.append("Do not transfer after hours")

        return "; ".join(parts) if parts else "Collect info and promise callback"

    def extract_integration_constraints(self, text: str) -> List[str]:
        """Extract ServiceTrade and other integration rules."""
        constraints = []
        text_lower = text.lower()

        # Look for ServiceTrade rules
        if "servicetrade" in text_lower:
            sentences = re.split(r'[.!?\n]', text)
            for sentence in sentences:
                sent_lower = sentence.lower().strip()
                if "servicetrade" in sent_lower:
                    # Check for "never" / "don't" / "do not" rules
                    if any(neg in sent_lower for neg in ["never", "don't", "do not", "not"]):
                        constraint = sentence.strip()
                        constraint = re.sub(r'^\s*[-•●]\s*', '', constraint).strip()
                        if constraint and len(constraint) > 10:
                            constraints.append(constraint)
                    elif any(pos in sent_lower for pos in ["can be", "auto-create", "auto create", "automatically"]):
                        constraint = sentence.strip()
                        constraint = re.sub(r'^\s*[-•●]\s*', '', constraint).strip()
                        if constraint and len(constraint) > 10:
                            constraints.append(constraint)

        return constraints

    def extract_special_rules(self, text: str) -> List[str]:
        """Extract special handling rules and constraints."""
        rules = []
        text_lower = text.lower()

        # Look for special rule patterns
        special_patterns = [
            (r'if.*?(?:monitoring company|ADT|SimpliSafe).*?(?:always|emergency|treat)', "Monitoring company calls"),
            (r'if.*?(?:fire department|fire marshal|inspector).*?(?:flag|priority|urgent)', "Fire department/inspector calls"),
            (r'if.*?(?:permit|inspection|city inspector).*?(?:route|flag|direct)', "Permit/inspection handling"),
            (r'if.*?(?:property manag|lease|penalty|SLA).*?(?:flag|priority|urgent)', "Property management priority"),
            (r'if.*?(?:referred by|referr).*?(?:ask|property management)', "Referral handling"),
            (r'(?:warranty|warrant).*?(?:manual|not auto|don\'t create)', "Warranty work handling"),
            (r'(?:medical|hospital).*?(?:always|emergency|treat)', "Medical facility priority"),
        ]

        sentences = re.split(r'[.!?\n]', text)
        for sentence in sentences:
            sent_lower = sentence.lower().strip()
            for pattern, label in special_patterns:
                if re.search(pattern, sent_lower):
                    rule = sentence.strip()
                    rule = re.sub(r'^\s*[-•●]\s*', '', rule).strip()
                    if rule and len(rule) > 10:
                        rules.append(rule)
                    break

        return rules

    def extract_greeting(self, text: str) -> Optional[str]:
        """Extract custom greeting from transcript."""
        # Look for quoted greeting
        greeting_match = re.search(
            r'["\u201c]([^"\u201d]*?(?:thank you for calling|hello|welcome)[^"\u201d]*?)["\u201d]',
            text, re.IGNORECASE
        )
        if greeting_match:
            return greeting_match.group(1).strip()

        # Look for "greeting should be" pattern
        greeting_match = re.search(
            r'greeting.*?(?:should be|is|:)\s*["\u201c](.+?)["\u201d]',
            text, re.IGNORECASE
        )
        if greeting_match:
            return greeting_match.group(1).strip()

        return None

    def extract_address(self, text: str) -> Optional[str]:
        """Extract office address."""
        match = self.address_pattern.search(text)
        if match:
            return match.group(0).strip()

        # Broader pattern
        addr_match = re.search(
            r'(?:address|located|office).*?(\d+\s+.+?,\s*\w+.+?,\s*\w+.+?\d{5})',
            text, re.IGNORECASE
        )
        if addr_match:
            return addr_match.group(1).strip()

        return None

    def extract_questions_or_unknowns(self, memo: Dict) -> List[str]:
        """Identify missing or unclear data fields."""
        unknowns = []

        if not memo.get("business_hours", {}).get("start"):
            unknowns.append("Exact business hours start time not specified")
        if not memo.get("business_hours", {}).get("end"):
            unknowns.append("Exact business hours end time not specified")
        if not memo.get("business_hours", {}).get("timezone"):
            unknowns.append("Timezone not confirmed")
        if not memo.get("business_hours", {}).get("days"):
            unknowns.append("Business days not specified")
        if not memo.get("office_address"):
            unknowns.append("Office address not provided")
        if not memo.get("emergency_definition"):
            unknowns.append("Emergency definitions not clearly stated")
        if not memo.get("emergency_routing_rules", {}).get("primary_contact", {}).get("phone"):
            unknowns.append("Emergency routing phone numbers not provided")
        if not memo.get("services_supported"):
            unknowns.append("Services list not detailed")

        return unknowns

    def _normalize_time(self, time_str: str, is_end_time: bool = False) -> str:
        """Normalize time string to HH:MM format.
        
        Args:
            time_str: Raw time string like "8", "5 PM", "8:00AM"
            is_end_time: If True and no AM/PM specified, assume PM for values 1-7
        """
        time_str = time_str.strip().upper()
        time_str = time_str.replace('.', '').replace(' ', '')

        # Handle formats like "8AM", "5PM", "8:00AM"
        match = re.match(r'(\d{1,2}):?(\d{2})?(AM|PM)?', time_str)
        if match:
            hour = int(match.group(1))
            minutes = match.group(2) or "00"
            ampm = match.group(3)

            # Infer AM/PM when not specified
            if not ampm:
                if is_end_time and 1 <= hour <= 7:
                    ampm = "PM"  # "5" as end time is almost certainly 5 PM
                elif not is_end_time and 6 <= hour <= 11:
                    ampm = "AM"  # "8" as start time is almost certainly 8 AM

            if ampm == "PM" and hour != 12:
                hour += 12
            elif ampm == "AM" and hour == 12:
                hour = 0

            return f"{hour:02d}:{minutes}"

        return time_str

    def extract_all(self, text: str, source: str = "demo_call") -> Dict[str, Any]:
        """Run all extraction methods and produce structured account memo."""
        company_name = self.extract_company_name(text)
        business_hours = self.extract_business_hours(text)
        services = self.extract_services(text)
        emergencies = self.extract_emergency_definitions(text)
        routing = self.extract_routing_rules(text)
        constraints = self.extract_integration_constraints(text)
        special_rules = self.extract_special_rules(text)
        greeting = self.extract_greeting(text)
        address = self.extract_address(text)

        # Build emergency routing structure
        emergency_contacts = routing["emergency"]["contacts"]
        primary_contact = emergency_contacts[0] if len(emergency_contacts) > 0 else {}
        secondary_contact = emergency_contacts[1] if len(emergency_contacts) > 1 else {}

        memo = {
            "company_name": company_name,
            "version": "v1" if source == "demo_call" else "v2",
            "source": source,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "updated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "business_hours": {
                "days": business_hours.get("days", []),
                "start": business_hours.get("start"),
                "end": business_hours.get("end"),
                "timezone": business_hours.get("timezone"),
                "saturday_hours": business_hours.get("saturday_hours"),
                "notes": business_hours.get("notes", [])
            },
            "office_address": address,
            "services_supported": services,
            "emergency_definition": emergencies,
            "emergency_routing_rules": {
                "primary_contact": {
                    "name": primary_contact.get("name"),
                    "phone": primary_contact.get("phone"),
                    "role": primary_contact.get("role"),
                    "timeout_seconds": primary_contact.get("timeout_seconds")
                },
                "secondary_contact": {
                    "name": secondary_contact.get("name"),
                    "phone": secondary_contact.get("phone"),
                    "role": secondary_contact.get("role"),
                    "timeout_seconds": secondary_contact.get("timeout_seconds")
                },
                "additional_contacts": emergency_contacts[2:] if len(emergency_contacts) > 2 else [],
                "fallback": routing["emergency"].get("fallback")
                    or "Take message (name, number, address, issue description) and assure callback",
                "callback_promise": routing["emergency"].get("callback_promise") or "as soon as possible",
                "transfer_timeout_seconds": primary_contact.get("timeout_seconds", DEFAULT_TRANSFER_TIMEOUT)
            },
            "non_emergency_routing_rules": {
                "during_hours": routing["non_emergency"].get("during_hours")
                    or "Route to main office",
                "after_hours": routing["non_emergency"].get("after_hours")
                    or "Collect info and promise callback next business day"
            },
            "call_transfer_rules": {
                "timeout_seconds": primary_contact.get("timeout_seconds", DEFAULT_TRANSFER_TIMEOUT),
                "max_retries": 2,
                "failure_message": "I apologize, I wasn't able to connect you. Let me take your information and someone will call you back shortly."
            },
            "business_hours_routing": {
                "contacts": routing["business_hours"]["contacts"]
            },
            "integration_constraints": constraints,
            "special_rules": special_rules,
            "greeting": greeting,
            "after_hours_flow_summary": self._generate_after_hours_summary(routing, emergencies),
            "office_hours_flow_summary": self._generate_office_hours_summary(routing),
            "questions_or_unknowns": [],
            "notes": None
        }

        # Identify unknowns
        memo["questions_or_unknowns"] = self.extract_questions_or_unknowns(memo)

        # Generate notes
        memo["notes"] = self._generate_notes(memo, source)

        return memo

    def _generate_notes(self, memo: Dict[str, Any], source: str) -> str:
        """Generate notes summarizing extraction highlights and caveats."""
        notes_parts = []

        source_label = "demo call" if source == "demo_call" else "onboarding call"
        company = memo.get("company_name") or "Unknown Company"
        notes_parts.append(f"Auto-extracted from {source_label} transcript for {company}.")

        # Count emergency contacts
        er = memo.get("emergency_routing_rules", {})
        total_contacts = 0
        if er.get("primary_contact", {}).get("phone"):
            total_contacts += 1
        if er.get("secondary_contact", {}).get("phone"):
            total_contacts += 1
        total_contacts += len(er.get("additional_contacts", []))
        if total_contacts > 0:
            notes_parts.append(f"Emergency contact chain: {total_contacts} contact(s) configured.")

        # Services count
        services = memo.get("services_supported", [])
        if services:
            notes_parts.append(f"Services: {len(services)} identified.")

        # Emergency definitions
        emergencies = memo.get("emergency_definition", [])
        if emergencies:
            notes_parts.append(f"Emergency triggers: {len(emergencies)} defined.")

        # Unknowns count
        unknowns = memo.get("questions_or_unknowns", [])
        if unknowns:
            notes_parts.append(f"Flagged {len(unknowns)} unknown(s) for human review.")

        # Special rules
        special = memo.get("special_rules", [])
        if special:
            notes_parts.append(f"Special handling rules: {len(special)} captured.")

        # Business hours completeness
        bh = memo.get("business_hours", {})
        if not bh.get("start") or not bh.get("end"):
            notes_parts.append("Business hours incomplete — verify with client.")

        return " ".join(notes_parts)

    def _generate_after_hours_summary(self, routing: Dict, emergencies: List[str]) -> str:
        """Generate after-hours flow summary."""
        parts = [
            "1. Greet caller",
            "2. Ask purpose of call",
            "3. Determine if emergency or non-emergency",
        ]

        if emergencies:
            parts.append(f"4. Emergency triggers: {', '.join(emergencies[:3])}...")
        else:
            parts.append("4. Emergency determination based on client definitions")

        contacts = routing["emergency"]["contacts"]
        if contacts:
            contact_chain = " -> ".join([
                f"{c.get('name') or c.get('role', 'Contact')} ({c.get('phone', 'TBD')})"
                for c in contacts
            ])
            parts.append(f"5. Emergency: collect name, number, address -> transfer chain: {contact_chain}")
        else:
            parts.append("5. Emergency: collect name, number, address -> attempt transfer")

        parts.extend([
            "6. If transfer fails: take message, assure callback",
            "7. Non-emergency: collect info, promise callback next business day",
            "8. Ask 'Is there anything else I can help with?'",
            "9. Close call"
        ])

        return "\n".join(parts)

    def _generate_office_hours_summary(self, routing: Dict) -> str:
        """Generate office-hours flow summary."""
        parts = [
            "1. Greet caller",
            "2. Ask purpose of call",
            "3. Collect caller name and callback number",
        ]

        contacts = routing["business_hours"]["contacts"]
        if contacts:
            contact_chain = " -> ".join([
                f"{c.get('name') or c.get('role', 'Office')} ({c.get('phone', 'TBD')})"
                for c in contacts
            ])
            parts.append(f"4. Transfer to: {contact_chain}")
        else:
            parts.append("4. Transfer to main office line")

        parts.extend([
            "5. If transfer fails: take message, confirm follow-up",
            "6. Ask 'Is there anything else I can help with?'",
            "7. Close call"
        ])

        return "\n".join(parts)


if __name__ == "__main__":
    # Quick test
    extractor = TranscriptExtractor()
    test_text = """
    [Demo Call - TestCo Fire Services]
    We're open Monday through Friday, 8 AM to 5 PM Eastern.
    Emergencies are sprinkler leaks and fire alarm malfunctions.
    """
    result = extractor.extract_all(test_text, "demo_call")
    print(json.dumps(result, indent=2))
