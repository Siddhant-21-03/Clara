# Changelog: Summit Facility Maintenance

**Account ID:** ACC-005  
**Updated:** 2026-03-04T15:52:41.948826+00:00Z  
**Version:** v1 → v2  
**Total Changes:** 15  

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
  "start": "06:00",
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
  "start": "06:00",
  "end": "18:00",
  "timezone": "America/Chicago",
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
  `1500 Commerce Street, Suite 400, Dallas, Texas, 75201`

### Change 3: `services_supported`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  [
  "Hvac",
  "General Maintenance",
  "Janitorial"
]
  ```
- **Updated (v2):**
  ```json
  [
  "Electrical",
  "Hvac",
  "Plumbing",
  "General Maintenance",
  "Janitorial"
]
  ```

### Change 4: `emergency_definition`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  [
  "Burst pipe",
  "Flooding",
  "What are your clear emergency triggers",
  "Roof leak in an active",
  "Power outage",
  "... and 4 more"
]
  ```
- **Updated (v2):**
  ```json
  [
  "On holidays, treat it like Sunday \u2014 after-hours with emergency coverage only",
  "Burst pipe",
  "Active flooding",
  "Sewage backup",
  "No hot water in a medical",
  "... and 11 more"
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
    "phone": "214-555-0301",
    "role": "plumbing on-call",
    "timeout_seconds": 45
  },
  "secondary_contact": {
    "name": null,
    "phone": "214-555-0302",
    "role": "hvac on-call",
    "timeout_seconds": 45
  },
  "additional_contacts": [
    {
      "priority": 3,
      "name": null,
      "phone": "214-555-0303",
      "role": "electrical on-call",
      "timeout_seconds": 45
    },
    {
      "priority": 4,
      "name": null,
      "phone": "214-555-0300",
      "role": "general dispatch",
      "timeout_seconds": 45
    },
    {
      "priority": 5,
      "name": null,
      "phone": "214-555-0309",
      "role": "elevator emergency",
      "timeout_seconds": 30
    }
  ],
  "fallback": "Fallback chain: general dispatch (214-555-0300) -> Tom (214-555-0199)",
  "callback_promise": "15 minutes",
  "transfer_timeout_seconds": 45
}
  ```

### Change 6: `non_emergency_routing_rules`

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

### Change 7: `call_transfer_rules`

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

### Change 8: `integration_constraints`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  []
  ```
- **Updated (v2):**
  ```json
  [
  "Emergency calls should NOT create ServiceTrade jobs \u2014 our dispatch handles those",
  "Never auto-create janitorial requests in ServiceTrade"
]
  ```

### Change 9: `after_hours_flow_summary`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `1. Greet caller
2. Ask purpose of call
3. Determine if emergency or non-emergency
4. Emergency triggers: Burst pipe, Flooding, What are your clear emergency triggers...
5. Emergency: collect name, num...`
- **Updated (v2):**
  `1. Greet caller
2. Ask purpose of call
3. Determine if emergency or non-emergency
4. Emergency triggers: On holidays, treat it like Sunday — after-hours with emergency coverage only, Burst pipe, Activ...`

### Change 10: `office_hours_flow_summary`

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
4. Transfer to: dispatch (214-555-0100) -> None (214-555-0101)
5. If transfer fails: take message, confirm follow-up
6...`

### Change 11: `special_rules`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  ```json
  []
  ```
- **Updated (v2):**
  ```json
  [
  "Tom Bradley: Also, important \u2014 if someone mentions a lease obligation or a penalty clause, flag it as high priority even if it's not a physical emergency"
]
  ```

### Change 12: `greeting`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Not set`
- **Updated (v2):**
  `Thank you for calling Summit Facility Maintenance. This is Clara. How can I help you today?`

### Change 13: `business_hours_routing`

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
      "phone": "214-555-0100",
      "role": "dispatch",
      "timeout_seconds": 20
    },
    {
      "priority": 2,
      "name": null,
      "phone": "214-555-0101",
      "role": null,
      "timeout_seconds": 20
    }
  ]
}
  ```

### Change 14: `notes`

- **Action:** updated
- **Reason:** Onboarding provided confirmed/more detailed data
- **Previous (v1):**
  `Auto-extracted from demo call transcript for Summit Facility Maintenance. Services: 3 identified. Emergency triggers: 9 defined. Flagged 2 unknown(s) for human review.`
- **Updated (v2):**
  `Auto-extracted from onboarding call transcript for Summit Facility Maintenance. Emergency contact chain: 5 contact(s) configured. Services: 5 identified. Emergency triggers: 16 defined. Special handli...`

### Change 15: `questions_or_unknowns`

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

