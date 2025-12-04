#!/usr/bin/env python3
"""Test script to verify dry-run functionality"""

import argparse

# Test argparse handling of --dry-run
parser = argparse.ArgumentParser()
parser.add_argument('--dry-run', action='store_true')
parser.add_argument('--rules', default='filter_rules.json')

# Simulate command line
test_args = ['--dry-run', '--rules', 'test.json']
args = parser.parse_args(test_args)

print(f"args.dry_run = {args.dry_run}")
print(f"Type: {type(args.dry_run)}")
print(f"Rules: {args.rules}")

# This is what's passed to EmailFilter
print(f"\nWould pass to EmailFilter: dry_run={args.dry_run}")
