# Changelog: ComfortZone HVAC Solutions

**Account ID:** ACC-004  
**Updated:** 2026-03-04T15:52:41.845249+00:00Z  
**Version:** v1 → v2  
**Total Changes:** 14  

---

### Change 1: `business_hours`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  {
  "days": [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday"
  ],
  "start": "08:00",
  "end": "17:30",
  "timezone": "America/New_York"
}
  ```
- **Updated (v2):**
  ```json
  {
  "days": [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday"
  ],
  "start": "08:00",
  "end": "17:30",
  "timezone": "America/New_York",
  "saturday_hours": {
    "start": "08:00",
    "end": "12:00"
  },
  "notes": [
    "Saturday is half day",
    "Sunday closed / after-hours only"
  ]
}
  ```

### Change 2: `office_address`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Not set`
- **Updated (v2):**
  `2200 Peachtree Industrial Boulevard, Suite 310, Atlanta, Georgia, 30341`

### Change 3: `emergency_definition`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  [
  "No heat in winter for a commercial",
  "No ac in summer when it's affecting a critical",
  "Gas leak",
  "Co detector alarm",
  "Refrigeration failure",
  "... and 2 more"
]
  ```
- **Updated (v2):**
  ```json
  [
  "No heat in a commercial",
  "No ac when it's above 90 degrees and affecting a critical",
  "Refrigeration failure",
  "Gas leak",
  "Co detector alarm",
  "... and 2 more"
]
  ```

### Change 4: `emergency_routing_rules`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  {
  "primary_contact": {
    "name": null,
    "phone": null,
    "role": null,
    "timeout_seconds": null
  },
  "secondary_contact": {
    "name": null,
    "phone": null,
    "role": null,
    "timeout_seconds": null
  },
  "fallback": "Take message (name, number, address, issue description) and assure callback",
  "callback_promise": "as soon as possible",
  "transfer_timeout_seconds": 30
}
  ```
- **Updated (v2):**
  ```json
  {
  "primary_contact": {
    "name": null,
    "phone": "404-555-0177",
    "role": "on-call",
    "timeout_seconds": 45
  },
  "secondary_contact": {
    "name": "Rachel",
    "phone": "404-555-0133",
    "role": null,
    "timeout_seconds": 45
  },
  "additional_contacts": [
    {
      "priority": 3,
      "name": "Marcus Boyd",
      "phone": "404-555-0192",
      "role": null,
      "timeout_seconds": 30
    }
  ],
  "fallback": "Fallback chain: Marcus Boyd (404-555-0192)",
  "callback_promise": "as soon as possible",
  "transfer_timeout_seconds": 45
}
  ```

### Change 5: `non_emergency_routing_rules`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  {
  "during_hours": "Route to main office",
  "after_hours": "Collect info and promise callback next business day"
}
  ```
- **Updated (v2):**
  ```json
  {
  "during_hours": "Route to main office",
  "after_hours": "Collect caller information; Promise callback next business day; Promise callback by 9 AM"
}
  ```

### Change 6: `call_transfer_rules`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  {
  "timeout_seconds": 30,
  "max_retries": 2,
  "failure_message": "I apologize, I wasn't able to connect you. Let me take your information and someone will call you ba..."
}
  ```
- **Updated (v2):**
  ```json
  {
  "timeout_seconds": 45,
  "max_retries": 2,
  "failure_message": "I apologize, I wasn't able to connect you. Let me take your information and someone will call you ba..."
}
  ```

### Change 7: `integration_constraints`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  []
  ```
- **Updated (v2):**
  ```json
  [
  "James Wright: Also, for emergency calls, don't create ServiceTrade jobs"
]
  ```

### Change 8: `after_hours_flow_summary`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `1. Greet caller
2. Ask purpose of call
3. Determine if emergency or non-emergency
4. Emergency triggers: No heat in winter for a commercial, No ac in summer when it's affecting a critical, Gas leak......`
- **Updated (v2):**
  `1. Greet caller
2. Ask purpose of call
3. Determine if emergency or non-emergency
4. Emergency triggers: No heat in a commercial, No ac when it's above 90 degrees and affecting a critical, Refrigerati...`

### Change 9: `office_hours_flow_summary`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `1. Greet caller
2. Ask purpose of call
3. Collect caller name and callback number
4. Transfer to main office line
5. If transfer fails: take message, confirm follow-up
6. Ask 'Is there anything else I...`
- **Updated (v2):**
  `1. Greet caller
2. Ask purpose of call
3. Collect caller name and callback number
4. Transfer to: None (404-555-0100) -> None (404-555-0177)
5. If transfer fails: take message, confirm follow-up
6. As...`

### Change 10: `special_rules`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  []
  ```
- **Updated (v2):**
  ```json
  [
  "Medical facilities are always emergency",
  "But NOT for warranty work \u2014 warranty claims need to go through me manually",
  "Rachel Park: Yes \u2014 if a caller mentions they were referred by a property management company, ask which property management company and which property"
]
  ```

### Change 11: `greeting`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Not set`
- **Updated (v2):**
  `Thank you for calling ComfortZone HVAC Solutions, your heating, cooling, and refrigeration experts. This is Clara, how can I help you?`

### Change 12: `business_hours_routing`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  {}
  ```
- **Updated (v2):**
  ```json
  {
  "contacts": [
    {
      "priority": 1,
      "name": null,
      "phone": "404-555-0100",
      "role": null,
      "timeout_seconds": 20
    },
    {
      "priority": 2,
      "name": null,
      "phone": "404-555-0177",
      "role": null,
      "timeout_seconds": 20
    }
  ]
}
  ```

### Change 13: `notes`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Auto-extracted from demo call transcript for ComfortZone HVAC Solutions. Services: 1 identified. Emergency triggers: 7 defined. Flagged 2 unknown(s) for human review.`
- **Updated (v2):**
  `Auto-extracted from onboarding call transcript for ComfortZone HVAC Solutions. Emergency contact chain: 3 contact(s) configured. Services: 1 identified. Emergency triggers: 7 defined. Special handling...`

### Change 14: `questions_or_unknowns`

- **Action:** resolved
- **Reason:** Onboarding resolved previously unknown items
- **Previous (v1):**
  ```json
  [
  "Office address not provided",
  "Emergency routing phone numbers not provided"
]
  ```
- **Updated (v2):**
  ```json
  []
  ```

