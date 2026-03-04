# Changelog: FireShield Protection Services

**Account ID:** ACC-001  
**Updated:** 2026-03-04T15:52:41.586554+00:00Z  
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
  "end": "17:00",
  "timezone": "America/New_York",
  "notes": [
    "Sunday closed / after-hours only"
  ]
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
    "Friday"
  ],
  "start": "08:00",
  "end": "17:00",
  "timezone": "America/New_York",
  "notes": [
    "Sunday closed / after-hours only",
    "Saturday closed / after-hours only"
  ]
}
  ```

### Change 2: `services_supported`

- **Action:** merged
- **Reason:** Merged onboarding data with existing demo data
- **Previous (v1):**
  ```json
  [
  "Fire Protection",
  "Alarm",
  "Sprinkler",
  "Fire Sprinkler Systems",
  "Fire Alarm Systems",
  "... and 2 more"
]
  ```
- **Updated (v2):**
  ```json
  [
  "Fire Protection",
  "Alarm",
  "Sprinkler",
  "Fire Sprinkler Systems",
  "Fire Alarm Systems",
  "... and 2 more"
]
  ```

### Change 3: `emergency_definition`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  [
  "Sprinkler leak",
  "Flooding"
]
  ```
- **Updated (v2):**
  ```json
  [
  "Sprinkler head discharge",
  "Active fire alarm",
  "Fire pump failure",
  "Fire suppression system is completely offline"
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
    "name": "Danny Rivera",
    "phone": "813-555-0147",
    "role": "on-call tech",
    "timeout_seconds": 45
  },
  "secondary_contact": {
    "name": "Mike Johnson",
    "phone": "813-555-0199",
    "role": null,
    "timeout_seconds": 45
  },
  "fallback": "Fallback chain: Danny Rivera (813-555-0147) -> Mike Johnson (813-555-0199) -> Backup (813-555-0100)",
  "callback_promise": "30 minutes",
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
  "after_hours": "Collect caller information; Get name and callback number; Promise callback next business day"
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
  "Never create sprinkler jobs in ServiceTrade automatically",
  "Sarah Miller: Also, fire alarm jobs can be auto-created in ServiceTrade for non-emergency requests"
]
  ```

### Change 8: `after_hours_flow_summary`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `1. Greet caller
2. Ask purpose of call
3. Determine if emergency or non-emergency
4. Emergency triggers: Sprinkler leak, Flooding...
5. Emergency: collect name, number, address -> attempt transfer
6. ...`
- **Updated (v2):**
  `1. Greet caller
2. Ask purpose of call
3. Determine if emergency or non-emergency
4. Emergency triggers: Sprinkler head discharge, Active fire alarm, Fire pump failure...
5. Emergency: collect name, n...`

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
4. Transfer to: None (813-555-0100)
5. If transfer fails: take message, confirm follow-up
6. Ask 'Is there anything el...`

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
  "Mike Johnson: If someone mentions a fire department inspection or a fire marshal visit, flag that as high priority even if it's not an emergency"
]
  ```

### Change 11: `greeting`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Not set`
- **Updated (v2):**
  `Thank you for calling FireShield Protection Services. This is Clara, how may I help you today?`

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
      "phone": "813-555-0100",
      "role": null,
      "timeout_seconds": 30
    }
  ]
}
  ```

### Change 13: `notes`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Auto-extracted from demo call transcript for FireShield Protection Services. Services: 7 identified. Emergency triggers: 2 defined. Flagged 2 unknown(s) for human review.`
- **Updated (v2):**
  `Auto-extracted from onboarding call transcript for FireShield Protection Services. Emergency contact chain: 2 contact(s) configured. Services: 6 identified. Emergency triggers: 4 defined. Flagged 1 un...`

### Change 14: `questions_or_unknowns`

- **Action:** resolved
- **Reason:** Onboarding resolved previously unknown items
- **Previous (v1):**
  ```json
  [
  "Emergency routing phone numbers not provided"
]
  ```
- **Updated (v2):**
  ```json
  [
  "Office address not provided"
]
  ```

