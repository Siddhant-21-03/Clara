"""
Clara Answers - Retell Agent Prompt Generator
=============================================
Generates Retell Agent Draft Spec (JSON) from structured account memo.
Produces a deployable system prompt following Clara's conversation hygiene rules.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List


class PromptGenerator:
    """Generates Retell AI voice agent configurations from account memos."""

    def __init__(self):
        self.voice_defaults = {
            "voice_id": "eleven_turbo_v2",
            "voice_style": "professional",
            "language": "en-US",
            "speaking_rate": 1.0
        }

    def generate_system_prompt(self, memo: Dict[str, Any]) -> str:
        """Generate the full system prompt for the Retell agent."""
        company = memo.get("company_name", "the company")
        greeting = memo.get("greeting") or f"Thank you for calling {company}. This is Clara, how may I help you today?"
        timezone = memo.get("business_hours", {}).get("timezone", "the local timezone")
        bh = memo.get("business_hours", {})
        days = bh.get("days", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
        start_time = bh.get("start", "8:00 AM")
        end_time = bh.get("end", "5:00 PM")
        sat_hours = bh.get("saturday_hours")

        # Format business hours display
        if days:
            day_range = f"{days[0]} through {days[-1]}" if len(days) > 1 else days[0]
        else:
            day_range = "Monday through Friday"

        hours_display = f"{day_range}, {start_time} to {end_time}"
        if sat_hours:
            hours_display += f" (Saturday: {sat_hours.get('start', '8:00')} to {sat_hours.get('end', '12:00')})"

        # Emergency definitions
        emergencies = memo.get("emergency_definition", [])
        emergency_list = "\n".join([f"  - {e}" for e in emergencies]) if emergencies else "  - As defined by the client"

        # Emergency routing
        emerg_routing = memo.get("emergency_routing_rules", {})
        primary = emerg_routing.get("primary_contact", {})
        secondary = emerg_routing.get("secondary_contact", {})
        additional = emerg_routing.get("additional_contacts", [])
        callback_promise = emerg_routing.get("callback_promise", "as soon as possible")
        fallback = emerg_routing.get("fallback", "Take message and assure callback")

        # Build transfer chain description
        transfer_chain = self._build_transfer_chain_text(primary, secondary, additional)

        # Business hours routing
        bh_routing = memo.get("business_hours_routing", {})
        bh_contacts = bh_routing.get("contacts", [])
        bh_transfer = self._build_bh_transfer_text(bh_contacts)

        # Non-emergency routing
        non_emerg = memo.get("non_emergency_routing_rules", {})
        non_emerg_after = non_emerg.get("after_hours") or "Collect info and promise callback next business day"

        # Integration constraints
        constraints = memo.get("integration_constraints", [])
        constraints_text = "\n".join([f"  - {c}" for c in constraints]) if constraints else "  - None specified"

        # Special rules
        special_rules = memo.get("special_rules", [])
        special_rules_text = "\n".join([f"  - {r}" for r in special_rules]) if special_rules else ""

        # Services
        services = memo.get("services_supported", [])
        services_text = ", ".join(services) if services else "services as defined by the company"

        # Build the full prompt
        prompt = f"""You are Clara, an AI-powered voice agent for {company}. You handle inbound phone calls professionally, warmly, and efficiently.

## IDENTITY
- Your name is Clara.
- You work for {company}.
- You never mention that you are an AI unless directly asked. If asked, say "I'm Clara, a virtual assistant for {company}."
- You never mention internal tools, function calls, APIs, or systems to the caller.

## GREETING
When answering a call, say: "{greeting}"

## COMPANY INFORMATION
- Company: {company}
- Services: {services_text}
- Business Hours: {hours_display}
- Timezone: {timezone}
{f'- Office Address: {memo.get("office_address")}' if memo.get("office_address") else ''}

## BUSINESS HOURS FLOW (During {hours_display})
Follow these steps in order:

1. **Greet the caller** using the standard greeting above.
2. **Ask the purpose of the call**: "How can I help you today?"
3. **Collect caller information**:
   - Full name
   - Callback phone number
   - Brief description of what they need
4. **Route or transfer the call**:
{bh_transfer}
5. **If transfer fails**:
   - Apologize: "I'm sorry, the line seems to be busy right now."
   - Take their complete message.
   - Confirm: "I've noted your information and someone from our team will get back to you shortly."
6. **Ask**: "Is there anything else I can help you with?"
7. **If no**: "Thank you for calling {company}. Have a great day!" End call.

## AFTER-HOURS FLOW (Outside {hours_display})
Follow these steps in order:

1. **Greet the caller**: "{self._make_after_hours_greeting(greeting, company)}"
2. **Ask the purpose**: "How can I help you?"
3. **Determine if this is an EMERGENCY**:

   Emergency situations include:
{emergency_list}

4. **If EMERGENCY**:
   a. Immediately collect:
      - Caller's full name
      - Callback phone number
      - Address/location of the emergency
      - Brief description of the situation
   b. Attempt transfer following this chain:
{transfer_chain}
   c. If ALL transfers fail:
      - Say: "I sincerely apologize that I wasn't able to reach our on-call team directly. I have all your information and I'm flagging this as an urgent emergency. Someone will call you back within {callback_promise}."
      - Ensure all collected information is logged.

5. **If NOT an emergency**:
   - Collect:
     - Caller's full name
     - Callback phone number
     - Description of what they need
   - Say: "{self._format_non_emergency_response(non_emerg_after, company)}"

6. **Ask**: "Is there anything else I can help you with?"
7. **If no**: "Thank you for calling {company}. Have a good evening!" End call.

## CALL TRANSFER PROTOCOL
- When transferring, say: "Let me connect you with our team. Please hold for just a moment."
- Do NOT tell the caller you are "transferring to a phone number" or mention specific numbers.
- If the transfer is taking long, say: "I'm still trying to reach someone, thank you for your patience."
- Transfer timeout: {emerg_routing.get('transfer_timeout_seconds', 30)} seconds per attempt.

## TRANSFER FAILURE PROTOCOL
If a transfer attempt fails:
- Try the next contact in the chain.
- After all attempts: "I apologize, I wasn't able to connect you right now. I've captured all your information and someone will reach out to you within {callback_promise}."
- Never leave a caller without a clear next step.

## INTEGRATION CONSTRAINTS
{constraints_text}

{f'''## SPECIAL RULES
{special_rules_text}''' if special_rules_text else ''}

## CONVERSATION RULES
- Be professional, empathetic, and concise.
- Do NOT ask too many questions. Only collect what is needed for routing and dispatch.
- Do NOT mention function calls, APIs, webhooks, or internal systems.
- Do NOT diagnose or troubleshoot technical problems.
- If a caller is distressed (emergency), prioritize speed — get their info quickly and attempt transfer immediately.
- If a caller asks a question you cannot answer, say: "That's a great question. Let me make sure our team follows up with you on that."
- Always confirm the information you've collected before ending the call.
- Always ask "Is there anything else I can help you with?" before closing.

## INFORMATION COLLECTION GUIDELINES
Always collect at minimum:
- Caller's full name
- Callback phone number

For emergencies, also collect:
- Location/address of the emergency
- Brief description of the situation

For service requests, also collect:
- Type of service needed
- Preferred scheduling (if applicable)
- Any relevant account or contract number (if offered)
"""

        return prompt.strip()

    def _make_after_hours_greeting(self, greeting: str, company: str) -> str:
        """Generate after-hours version of the greeting."""
        if not greeting:
            return f"Thank you for calling {company}. I appreciate you calling. Please note our office is currently closed."
        result = greeting
        for phrase in ['how may I help you today?', 'How can I assist you?', 'How can I help you?',
                       'how can I assist you?', 'how can I help you?', 'How may I help you today?']:
            result = result.replace(phrase, 'I appreciate you calling. Please note our office is currently closed.')
        return result

    def _build_transfer_chain_text(self, primary: Dict, secondary: Dict, additional: List) -> str:
        """Build formatted transfer chain for the prompt."""
        lines = []
        contacts = []

        if primary and primary.get("phone"):
            name = primary.get("name") or primary.get("role", "Primary on-call")
            timeout = primary.get("timeout_seconds", 30)
            contacts.append(f"      1. {name} — wait {timeout} seconds")

        if secondary and secondary.get("phone"):
            name = secondary.get("name") or secondary.get("role", "Secondary contact")
            timeout = secondary.get("timeout_seconds", 30)
            contacts.append(f"      2. {name} — wait {timeout} seconds")

        for i, contact in enumerate(additional, start=3):
            name = contact.get("name") or contact.get("role", f"Contact {i}")
            timeout = contact.get("timeout_seconds", 30)
            contacts.append(f"      {i}. {name} — wait {timeout} seconds")

        if contacts:
            return "\n".join(contacts)
        else:
            return "      1. On-call team (details to be configured)"

    def _build_bh_transfer_text(self, contacts: List[Dict]) -> str:
        """Build business hours transfer text."""
        if not contacts:
            return "   - Transfer to main office line"

        lines = []
        for i, contact in enumerate(contacts, start=1):
            name = contact.get("name") or contact.get("role") or "Main Office"
            timeout = contact.get("timeout_seconds", 30)
            lines.append(f"   - {'First, t' if i == 1 else 'If no answer, t'}ransfer to {name} (wait {timeout}s)")

        return "\n".join(lines)

    def _format_non_emergency_response(self, rule: Optional[str], company: str) -> str:
        """Format the non-emergency after-hours response."""
        if not rule:
            return f"I've noted all your information. Someone from {company} will follow up with you on the next business day."
        if "10 AM" in rule or "10 am" in rule:
            return f"I've noted all your information. Our team will reach out to you by 10 AM on the next business day."
        if "9 AM" in rule or "9 am" in rule:
            return f"I've noted all your information. Our team will reach out to you by 9 AM on the next business day."
        if "next business day" in rule.lower():
            return f"I've noted all your information. Someone from {company} will follow up with you on the next business day."
        return f"I've noted all your information. Someone from {company} will follow up with you shortly during business hours."

    def generate_agent_spec(self, memo: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete Retell Agent Draft Spec from account memo."""
        company = memo.get("company_name", "Unknown Company")
        account_id = memo.get("account_id", "ACC-000")
        version = memo.get("version", "v1")

        system_prompt = self.generate_system_prompt(memo)

        # Build transfer targets
        transfer_targets = []
        emerg_routing = memo.get("emergency_routing_rules", {})

        primary = emerg_routing.get("primary_contact", {})
        if primary.get("phone"):
            transfer_targets.append({
                "name": primary.get("name") or "Primary On-Call",
                "phone": primary["phone"],
                "priority": 1,
                "conditions": "Emergency after-hours calls"
            })

        secondary = emerg_routing.get("secondary_contact", {})
        if secondary.get("phone"):
            transfer_targets.append({
                "name": secondary.get("name") or "Secondary Contact",
                "phone": secondary["phone"],
                "priority": 2,
                "conditions": "Fallback if primary unavailable"
            })

        for contact in emerg_routing.get("additional_contacts", []):
            if contact.get("phone"):
                transfer_targets.append({
                    "name": contact.get("name") or contact.get("role", "Additional Contact"),
                    "phone": contact["phone"],
                    "priority": contact.get("priority", 3),
                    "conditions": "Additional fallback"
                })

        # Business hours contacts
        bh_contacts = memo.get("business_hours_routing", {}).get("contacts", [])
        for contact in bh_contacts:
            if contact.get("phone"):
                transfer_targets.append({
                    "name": contact.get("name") or contact.get("role", "Office"),
                    "phone": contact["phone"],
                    "priority": contact.get("priority", 1),
                    "conditions": "During business hours"
                })

        # Build tool invocations (backend only, never mentioned to caller)
        tool_invocations = [
            {
                "tool_name": "check_business_hours",
                "trigger": "On call start",
                "description": "Determine if call is during or outside business hours"
            },
            {
                "tool_name": "log_call_details",
                "trigger": "After collecting caller info",
                "description": "Store call details including name, number, purpose"
            },
            {
                "tool_name": "transfer_call",
                "trigger": "When routing to contact",
                "description": "Initiate call transfer to appropriate contact"
            },
            {
                "tool_name": "create_service_ticket",
                "trigger": "After non-emergency info collection",
                "description": "Create service ticket in management system"
            },
            {
                "tool_name": "flag_emergency",
                "trigger": "Emergency detected",
                "description": "Flag call as emergency in dispatch system"
            }
        ]

        # Determine callback promise
        callback_promise = emerg_routing.get("callback_promise", "as soon as possible")

        agent_spec = {
            "agent_name": f"Clara - {company}",
            "account_id": account_id,
            "version": version,
            "created_at": datetime.now(timezone.utc).isoformat() + "Z",
            "updated_at": datetime.now(timezone.utc).isoformat() + "Z",
            "voice_style": self.voice_defaults["voice_style"],
            "voice_config": self.voice_defaults.copy(),
            "system_prompt": system_prompt,
            "key_variables": {
                "timezone": memo.get("business_hours", {}).get("timezone"),
                "business_hours_display": self._format_hours_display(memo.get("business_hours", {})),
                "company_name": company,
                "office_address": memo.get("office_address"),
                "emergency_triggers": memo.get("emergency_definition", []),
                "services": memo.get("services_supported", []),
                "greeting": memo.get("greeting")
            },
            "call_transfer_config": {
                "enabled": True,
                "transfer_targets": transfer_targets,
                "timeout_seconds": emerg_routing.get("transfer_timeout_seconds", 30),
                "max_retries": memo.get("call_transfer_rules", {}).get("max_retries", 2)
            },
            "fallback_config": {
                "transfer_fail_message": memo.get("call_transfer_rules", {}).get("failure_message",
                    "I apologize, I wasn't able to connect you. Let me take your information and someone will call you back shortly."),
                "voicemail_enabled": False,
                "escalation_action": f"Log as urgent, promise callback within {callback_promise}"
            },
            "call_transfer_protocol": {
                "enabled": True,
                "transfer_targets": transfer_targets,
                "timeout_seconds": emerg_routing.get("transfer_timeout_seconds", 30),
                "max_retries": memo.get("call_transfer_rules", {}).get("max_retries", 2),
                "caller_message": "Let me connect you with our team. Please hold for just a moment.",
                "fail_message": "I apologize, I wasn't able to connect you right now."
            },
            "fallback_protocol": {
                "action": f"Log as urgent, promise callback within {callback_promise}",
                "message": memo.get("call_transfer_rules", {}).get("failure_message",
                    "I apologize, I wasn't able to connect you. Let me take your information and someone will call you back shortly."),
                "voicemail_enabled": False
            },
            "tool_invocations": tool_invocations,
            "metadata": {
                "generated_by": "clara-pipeline",
                "source_transcript": memo.get("_source_file", ""),
                "confidence_score": self._calculate_confidence(memo)
            }
        }

        return agent_spec

    def _format_hours_display(self, bh: Dict) -> str:
        """Format business hours for display."""
        days = bh.get("days", [])
        start = bh.get("start", "")
        end = bh.get("end", "")

        if days and start and end:
            day_range = f"{days[0]}-{days[-1]}" if len(days) > 1 else days[0]
            display = f"{day_range} {start}-{end}"
            sat = bh.get("saturday_hours")
            if sat:
                display += f", Sat {sat.get('start', '')}-{sat.get('end', '')}"
            return display
        return "Not specified"

    def _calculate_confidence(self, memo: Dict) -> float:
        """Calculate confidence score based on data completeness."""
        total_fields = 10
        filled = 0

        if memo.get("company_name"):
            filled += 1
        if memo.get("business_hours", {}).get("start"):
            filled += 1
        if memo.get("business_hours", {}).get("timezone"):
            filled += 1
        if memo.get("emergency_definition"):
            filled += 1
        if memo.get("emergency_routing_rules", {}).get("primary_contact", {}).get("phone"):
            filled += 1
        if memo.get("services_supported"):
            filled += 1
        if memo.get("office_address"):
            filled += 1
        if memo.get("integration_constraints"):
            filled += 1
        if memo.get("greeting"):
            filled += 1
        if not memo.get("questions_or_unknowns"):
            filled += 1

        return round(filled / total_fields, 2)


if __name__ == "__main__":
    # Quick test
    test_memo = {
        "company_name": "Test Fire Co",
        "account_id": "ACC-001",
        "version": "v1",
        "business_hours": {
            "days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "start": "08:00",
            "end": "17:00",
            "timezone": "America/New_York"
        },
        "services_supported": ["Fire Sprinkler", "Fire Alarm"],
        "emergency_definition": ["Sprinkler leak", "Fire alarm malfunction"],
        "emergency_routing_rules": {
            "primary_contact": {"name": "John", "phone": "555-0100", "timeout_seconds": 30},
            "secondary_contact": {"name": "Jane", "phone": "555-0200", "timeout_seconds": 30},
            "callback_promise": "30 minutes"
        },
        "non_emergency_routing_rules": {
            "after_hours": "Collect info, callback next business day"
        },
        "call_transfer_rules": {"timeout_seconds": 30, "max_retries": 2}
    }

    gen = PromptGenerator()
    spec = gen.generate_agent_spec(test_memo)
    print(json.dumps(spec, indent=2, default=str)[:2000])
    print("\n--- SYSTEM PROMPT ---\n")
    print(spec["system_prompt"][:1000])
