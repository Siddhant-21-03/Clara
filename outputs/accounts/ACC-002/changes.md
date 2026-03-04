# Changelog: Guardian Alarm & Sprinkler Co.

**Account ID:** ACC-002  
**Updated:** 2026-03-04T15:52:41.677903+00:00Z  
**Version:** v1 → v2  
**Total Changes:** 13  

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
    "Friday",
    "Saturday"
  ],
  "start": "07:00",
  "end": "18:00",
  "timezone": "America/Chicago"
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
  "start": "07:00",
  "end": "18:00",
  "timezone": "America/Chicago",
  "saturday_hours": {
    "start": "07:00",
    "end": "18:00"
  },
  "notes": [
    "Sunday closed / after-hours only",
    "Saturday closed / after-hours only"
  ]
}
  ```

### Change 2: `office_address`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Not set`
- **Updated (v2):**
  `4521 West Industrial Boulevard, Chicago, Illinois, 60632`

### Change 3: `emergency_definition`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  [
  "Sprinkler leak",
  "Active fire alarm",
  "Those need immediate response, 24/7",
  "When an emergency comes in after hours, who should Clara try to reach"
]
  ```
- **Updated (v2):**
  ```json
  [
  "Active fire alarm",
  "Fire alarm sounding",
  "Kitchen hood suppression system discharge",
  "Trouble beep",
  "Trouble signal",
  "... and 1 more"
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
    "phone": "312-555-0200",
    "role": "on-call",
    "timeout_seconds": 30
  },
  "secondary_contact": {
    "name": "Angela Torres",
    "phone": "312-555-0215",
    "role": "on-call",
    "timeout_seconds": 60
  },
  "fallback": "Fallback chain: on-call (312-555-0200) -> Angela Torres (312-555-0215)",
  "callback_promise": "15 minutes",
  "transfer_timeout_seconds": 30
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
  "after_hours": "Collect caller information; Get name and callback number; Promise callback next business day; Promis..."
}
  ```

### Change 6: `integration_constraints`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  [
  "We do NOT want any sprinkler jobs created automatically in ServiceTrade"
]
  ```
- **Updated (v2):**
  ```json
  [
  "Never \u2014 and I mean never \u2014 create sprinkler jobs in ServiceTrade",
  "For fire alarm work, non-emergency requests can be auto-created in ServiceTrade"
]
  ```

### Change 7: `after_hours_flow_summary`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `1. Greet caller
2. Ask purpose of call
3. Determine if emergency or non-emergency
4. Emergency triggers: Sprinkler leak, Active fire alarm, Those need immediate response, 24/7...
5. Emergency: collect...`
- **Updated (v2):**
  `1. Greet caller
2. Ask purpose of call
3. Determine if emergency or non-emergency
4. Emergency triggers: Active fire alarm, Fire alarm sounding, Kitchen hood suppression system discharge...
5. Emergen...`

### Change 8: `office_hours_flow_summary`

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
4. Transfer to: None (312-555-0100) -> None (312-555-0120)
5. If transfer fails: take message, confirm follow-up
6. As...`

### Change 9: `special_rules`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  []
  ```
- **Updated (v2):**
  ```json
  [
  "If a caller mentions they're calling on behalf of a monitoring company \u2014 like ADT or SimpliSafe or whoever \u2014 that should always be treated as an emergency regardless of what they're describing"
]
  ```

### Change 10: `greeting`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Not set`
- **Updated (v2):**
  `Thank you for calling Guardian Alarm and Sprinkler. How can I assist you?`

### Change 11: `business_hours_routing`

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
      "phone": "312-555-0100",
      "role": null,
      "timeout_seconds": 20
    },
    {
      "priority": 2,
      "name": null,
      "phone": "312-555-0120",
      "role": null,
      "timeout_seconds": 20
    }
  ]
}
  ```

### Change 12: `notes`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Auto-extracted from demo call transcript for Guardian Alarm & Sprinkler Co.. Services: 7 identified. Emergency triggers: 4 defined. Flagged 2 unknown(s) for human review.`
- **Updated (v2):**
  `Auto-extracted from onboarding call transcript for Guardian Alarm & Sprinkler Co.. Emergency contact chain: 2 contact(s) configured. Services: 7 identified. Emergency triggers: 6 defined. Special hand...`

### Change 13: `questions_or_unknowns`

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

