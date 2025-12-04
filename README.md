# MZEmailsFiltering

**Author:** Mathias Svensson  
**GitHub:** https://github.com/mathiassv/MZEmailsFiltering

A Python script to automatically filter and organize emails in Maildir format based on subject matching rules.

## Features

- **Multi-field filtering**: Filter emails based on subject, from, to, cc, reply-to, or sender fields
- **Subject-based filtering**: Filter emails based on subject line patterns (legacy default)
- **Multiple match types**: Support for contains, exact match, starts with, ends with, and regex patterns
- **Automatic folder creation**: Creates Maildir-compatible folders (with cur/new/tmp structure)
- **Dry run mode**: Test your rules without actually moving files
- **Case-sensitive/insensitive matching**: Configure per rule
- **First-match wins**: Applies the first matching rule to each email
- **Comprehensive logging**: Track what's happening with your emails

## Installation

1. Ensure you have Python 3.6+ installed
2. No additional dependencies required (uses Python standard library)

## Configuration

Create a `filter_rules.json` file with your filtering rules:

```json
{
  "rules": [
    {
      "name": "Work emails",
      "field": "subject",
      "pattern": "[WORK]",
      "match_type": "contains",
      "case_sensitive": false,
      "target_folder": "Work"
    },
    {
      "name": "Emails from boss",
      "field": "from",
      "pattern": "boss@company.com",
      "match_type": "contains",
      "case_sensitive": false,
      "target_folder": "Boss"
    },
    {
      "name": "Team emails",
      "field": "to",
      "pattern": "team@company.com",
      "match_type": "contains",
      "case_sensitive": false,
      "target_folder": "Team"
    }
  ]
}
```

### Rule Configuration

Each rule supports the following fields:

- **name** (optional): A descriptive name for the rule
- **field** (optional, default: "subject"): Which email header field to match against
  - `subject`: Email subject line
  - `from`: Sender email address
  - `to`: Recipient email address(es)
  - `cc`: CC'd email address(es)
  - `reply-to`: Reply-To header
  - `sender`: Sender header
- **pattern** (required): The text pattern to match
- **match_type** (required): How to match the pattern
  - `contains`: Pattern appears anywhere in the field
  - `exact`: Field exactly matches pattern
  - `starts_with`: Field starts with pattern
  - `ends_with`: Field ends with pattern
  - `regex`: Pattern is a regular expression
- **case_sensitive** (optional, default: false): Whether matching is case-sensitive
- **target_folder** (required): Folder name to move matching emails to
  - The script will automatically add a leading `.` if not present
  - Creates `.FolderName` in the maildir (e.g., `.Work`, `.Stuff`)

## Usage

### Basic Usage

```bash
python3 mzfilter.py /path/to/maildir
```

This will:
- Process emails in the `new` and `cur` folders
- Use rules from `filter_rules.json` in the current directory
- Move matching emails to appropriate folders

### Command Line Options

```bash
python3 mzfilter.py /path/to/maildir [OPTIONS]
```

**Options:**

- `--rules FILEPATH`: Specify a custom rules file (default: `filter_rules.json`)
- `--dry-run`: Test without actually moving files
- `--folders FOLDER [FOLDER ...]`: Specify which folders to process (default: `new cur`)
- `--verbose`: Enable verbose logging
- `-h, --help`: Show help message

### Examples

#### Test your rules without moving files:
```bash
python3 mzfilter.py /home/username/Maildir --dry-run
```

#### Use a custom rules file:
```bash
python3 mzfilter.py /home/username/Maildir --rules /etc/mail-filters/custom_rules.json
```

#### Process only the 'new' folder:
```bash
python3 mzfilter.py /home/username/Maildir --folders new
```

#### Verbose output:
```bash
python3 mzfilter.py /home/username/Maildir --verbose
```

## How It Works

1. The script scans emails in the specified folders (`new` and/or `cur`)
2. For each email, it extracts the relevant headers (subject, from, to, cc, etc.)
3. It checks the specified field against each rule in order
4. When a match is found, the email is moved to the target folder
5. Target folders are created with proper Maildir structure (`.FolderName/cur`, `.FolderName/new`, `.FolderName/tmp`)
6. Only the first matching rule is applied per email

## Rule Examples

### Filter by Subject
```json
{
  "name": "Invoices",
  "field": "subject",
  "pattern": "invoice|receipt",
  "match_type": "regex",
  "case_sensitive": false,
  "target_folder": "Finance"
}
```

### Filter by Sender
```json
{
  "name": "Boss emails",
  "field": "from",
  "pattern": "boss@company.com",
  "match_type": "contains",
  "case_sensitive": false,
  "target_folder": "Important"
}
```

### Filter by Recipient
```json
{
  "name": "Team mailing list",
  "field": "to",
  "pattern": "team@company.com",
  "match_type": "contains",
  "case_sensitive": false,
  "target_folder": "Team"
}
```

### Filter by Domain (using regex)
```json
{
  "name": "All newsletters",
  "field": "from",
  "pattern": "@.*newsletter\\.com$",
  "match_type": "regex",
  "case_sensitive": false,
  "target_folder": "Newsletters"
}
```

### Filter CC'd emails
```json
{
  "name": "Archive CC",
  "field": "cc",
  "pattern": "archive@",
  "match_type": "starts_with",
  "case_sensitive": false,
  "target_folder": "Archive"
}
```

## Automation

To run automatically, you can set up a cron job:

```bash
# Edit your crontab
crontab -e

# Add a line to run every 5 minutes
*/5 * * * * /usr/bin/python3 /path/to/mzfilter.py /home/username/Maildir --rules /path/to/filter_rules.json >> /var/log/email_filter.log 2>&1
```

Or use it as a mail delivery agent by integrating with your mail server configuration.

## Maildir Structure

The script expects and maintains standard Maildir structure:

```
Maildir/
├── cur/           # Current (already read) messages
├── new/           # New (unread) messages  
├── tmp/           # Temporary files
├── .Stuff/        # Custom folder
│   ├── cur/
│   ├── new/
│   └── tmp/
├── .Work/         # Another custom folder
│   ├── cur/
│   ├── new/
│   └── tmp/
└── ...
```

## Logging

The script provides detailed logging:
- **INFO**: General progress and summary
- **WARNING**: Non-critical issues
- **ERROR**: Problems that prevent processing
- **DEBUG**: Detailed debugging info (with `--verbose`)

## Troubleshooting

### Emails not being moved
- Run with `--dry-run --verbose` to see what's happening
- Check that your patterns match the actual email subjects
- Verify the rules file is valid JSON

### Permission errors
- Ensure the script has read/write access to the maildir
- Check file ownership and permissions

### Folder not created
- Check that the parent maildir path is correct
- Verify write permissions on the maildir

## Safety Features

- **Dry run mode**: Test before making changes
- **Validation**: Checks maildir structure before processing
- **Error handling**: Continues processing even if individual emails fail
- **Logging**: Complete audit trail of actions

## License

Copyright (c) 2025 Mathias Svensson

This script is provided as-is for use with Maildir-format email systems.

For more information, visit: https://github.com/mathiassv/MZEmailsFiltering
