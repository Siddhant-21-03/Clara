"""
Clara Answers Onboarding Automation Pipeline
=============================================
Configuration and constants for the pipeline.
"""

import os

# Base directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DEMO_TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "demo_transcripts")
ONBOARDING_TRANSCRIPTS_DIR = os.path.join(DATA_DIR, "onboarding_transcripts")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs", "accounts")
SCHEMAS_DIR = os.path.join(BASE_DIR, "schemas")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
CHANGELOG_DIR = os.path.join(BASE_DIR, "changelog")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# File naming conventions
ACCOUNT_ID_PREFIX = "ACC"
DEMO_FILE_PREFIX = "demo_"
ONBOARDING_FILE_PREFIX = "onboarding_"

# Extraction patterns - keywords and phrases used for rule-based extraction
EMERGENCY_KEYWORDS = [
    "emergency", "urgent", "immediate", "critical", "burst", "leak",
    "flooding", "fire", "alarm", "sparking", "outage", "failure",
    "entrapment", "gas leak", "co detector", "carbon monoxide",
    "discharge", "offline", "down", "not working", "no heat", "no ac",
    "no power", "exposed wires", "burning smell", "sewage"
]

SERVICE_KEYWORDS = {
    "fire_protection": ["fire sprinkler", "sprinkler system", "fire alarm", "fire extinguisher",
                        "fire suppression", "fire pump", "backflow testing", "fire protection"],
    "alarm": ["alarm system", "alarm monitoring", "fire alarm", "alarm panel", "smoke detector",
              "alarm installation", "security alarm"],
    "electrical": ["electrical service", "electrical contractor", "electrical work",
                   "generator", "lighting service", "panel upgrade", "electrical panel"],
    "hvac": ["hvac", "heating and cooling", "air conditioning", "heat pump",
             "ventilation system", "refrigeration service", "a/c", "furnace"],
    "plumbing": ["plumbing service", "plumber", "plumbing contractor", "sewage",
                 "drain cleaning", "water heater"],
    "general_maintenance": ["facility maintenance", "janitorial", "general repair",
                           "building maintenance", "facility management"],
    "sprinkler": ["fire sprinkler", "sprinkler head", "sprinkler system",
                  "sprinkler inspection", "sprinkler install"],
    "kitchen_hood": ["kitchen hood", "hood suppression", "kitchen suppression",
                     "restaurant hood"],
    "elevator": ["elevator service", "elevator maintenance", "elevator repair", "lift service"],
}

TIMEZONE_MAPPINGS = {
    "eastern": "America/New_York",
    "central": "America/Chicago",
    "mountain": "America/Denver",
    "mountain standard": "America/Phoenix",
    "pacific": "America/Los_Angeles",
    "mst": "America/Phoenix",
    "est": "America/New_York",
    "cst": "America/Chicago",
    "pst": "America/Los_Angeles",
}

DAYS_OF_WEEK = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Transfer defaults
DEFAULT_TRANSFER_TIMEOUT = 30
DEFAULT_MAX_RETRIES = 2
DEFAULT_CALLBACK_PROMISE = "as soon as possible"

# Logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_LEVEL = "INFO"
