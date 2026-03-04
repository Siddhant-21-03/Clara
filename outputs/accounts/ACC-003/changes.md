# Changelog: Apex Electrical Services

**Account ID:** ACC-003  
**Updated:** 2026-03-04T15:52:41.767191+00:00Z  
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
  "start": "07:00",
  "end": "16:30",
  "timezone": "America/Denver"
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
  "end": "16:30",
  "timezone": "America/Denver",
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
  `7890 East McDowell Road, Suite 102, Phoenix, Arizona, 85008`

### Change 3: `services_supported`

- **Action:** merged
- **Reason:** Merged onboarding data with existing demo data
- **Previous (v1):**
  ```json
  [
  "Electrical",
  "Generator Maintenance",
  "Lighting Services",
  "Electrical Panel Upgrades"
]
  ```
- **Updated (v2):**
  ```json
  [
  "Electrical",
  "Generator Maintenance",
  "Lighting Services",
  "Electrical Panel Upgrades"
]
  ```

### Change 4: `emergency_definition`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  [
  "Power outage",
  "Sparking",
  "Exposed wiring",
  "Generator failure",
  "Electrical fire"
]
  ```
- **Updated (v2):**
  ```json
  [
  "Complete power outage",
  "Sparking",
  "Exposed live wires",
  "Generator failure",
  "Electrical fire",
  "... and 2 more"
]
  ```

### Change 5: `emergency_routing_rules`

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
    "phone": "480-555-0300",
    "role": "on-call",
    "timeout_seconds": 30
  },
  "secondary_contact": {
    "name": "David Rodriguez",
    "phone": "480-555-0155",
    "role": null,
    "timeout_seconds": 60
  },
  "fallback": "Take message (name, number, address, issue description) and assure callback",
  "callback_promise": "20 minutes",
  "transfer_timeout_seconds": 30
}
  ```

### Change 6: `non_emergency_routing_rules`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  {
  "during_hours": "Route to main office",
  "after_hours": "Collect info and promise callback"
}
  ```
- **Updated (v2):**
  ```json
  {
  "during_hours": "Route to main office",
  "after_hours": "Collect caller information; Promise callback next business day; Promise callback by 9 AM; Do not tra..."
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
  "For now, don't create any jobs in ServiceTrade automatically"
]
  ```

### Change 8: `after_hours_flow_summary`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `1. Greet caller
2. Ask purpose of call
3. Determine if emergency or non-emergency
4. Emergency triggers: Power outage, Sparking, Exposed wiring...
5. Emergency: collect name, number, address -> attemp...`
- **Updated (v2):**
  `1. Greet caller
2. Ask purpose of call
3. Determine if emergency or non-emergency
4. Emergency triggers: Complete power outage, Sparking, Exposed live wires...
5. Emergency: collect name, number, addr...`

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
4. Transfer to: dispatch (480-555-0100) -> None (480-555-0101)
5. If transfer fails: take message, confirm follow-up
6...`

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
  "And \u2014 this is new since the demo \u2014 we also want to treat any electrical issue at a medical facility as emergency, even if it's not life-threatening",
  "David Rodriguez: Yes \u2014 if a caller mentions a permit inspection or a city inspector, route that to Jenny directly, even after hours"
]
  ```

### Change 11: `greeting`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Not set`
- **Updated (v2):**
  `Thank you for calling Apex Electrical Services, this is Clara. How can I help you?`

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
      "phone": "480-555-0100",
      "role": "dispatch",
      "timeout_seconds": 25
    },
    {
      "priority": 2,
      "name": null,
      "phone": "480-555-0101",
      "role": null,
      "timeout_seconds": 25
    }
  ]
}
  ```

### Change 13: `notes`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Auto-extracted from demo call transcript for Apex Electrical Services. Services: 4 identified. Emergency triggers: 5 defined. Flagged 2 unknown(s) for human review.`
- **Updated (v2):**
  `Auto-extracted from onboarding call transcript for Apex Electrical Services. Emergency contact chain: 2 contact(s) configured. Services: 2 identified. Emergency triggers: 7 defined. Special handling r...`

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

