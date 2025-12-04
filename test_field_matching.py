#!/usr/bin/env python3
"""Test the new field-based matching functionality"""

import sys
import json
from pathlib import Path

# Add parent directory to path to import the module
sys.path.insert(0, str(Path(__file__).parent))

from mzfilter import EmailFilter

# Test the _match_rule method with different fields
print("Testing field-based matching...")
print("=" * 60)

# Create a mock EmailFilter instance
filter_obj = EmailFilter.__new__(EmailFilter)
filter_obj.dry_run = True

# Test headers
test_headers = {
    'subject': 'Invoice for March 2024',
    'from': 'billing@company.com',
    'to': 'user@example.com',
    'cc': 'manager@example.com',
    'reply-to': 'support@company.com',
    'sender': 'noreply@company.com'
}

# Test cases
test_rules = [
    {
        "name": "Match subject",
        "field": "subject",
        "pattern": "invoice",
        "match_type": "contains",
        "case_sensitive": False
    },
    {
        "name": "Match from",
        "field": "from",
        "pattern": "billing@",
        "match_type": "starts_with",
        "case_sensitive": False
    },
    {
        "name": "Match to",
        "field": "to",
        "pattern": "user@example.com",
        "match_type": "exact",
        "case_sensitive": False
    },
    {
        "name": "Match cc",
        "field": "cc",
        "pattern": "manager",
        "match_type": "contains",
        "case_sensitive": False
    },
    {
        "name": "No match",
        "field": "subject",
        "pattern": "payment",
        "match_type": "contains",
        "case_sensitive": False
    },
    {
        "name": "Regex from domain",
        "field": "from",
        "pattern": "@company\\.com$",
        "match_type": "regex",
        "case_sensitive": False
    },
    {
        "name": "Default to subject (no field specified)",
        "pattern": "March",
        "match_type": "contains",
        "case_sensitive": False
    }
]

for rule in test_rules:
    result = filter_obj._match_rule(test_headers, rule)
    field = rule.get('field', 'subject')
    print(f"Rule: {rule['name']}")
    print(f"  Field: {field}")
    print(f"  Pattern: {rule['pattern']}")
    print(f"  Match Type: {rule.get('match_type', 'contains')}")
    print(f"  Result: {'? MATCH' if result else '? NO MATCH'}")
    print()

print("=" * 60)
print("All tests completed successfully!")
