#!/bin/bash

# Example script to run email filtering with common settings
# Customize the paths and options for your environment

# Configuration
MAILDIR="/home/username/Maildir"  # Change to your maildir path
RULES_FILE="filter_rules.json"    # Path to your rules file
LOG_FILE="/var/log/email_filter.log"  # Optional log file

# Run the email filter
/usr/bin/python3 email_filter.py "$MAILDIR" \
    --rules "$RULES_FILE" \
    >> "$LOG_FILE" 2>&1

# Exit with the same status as the python script
exit $?
