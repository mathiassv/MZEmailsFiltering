# Quick Reference Guide

## Available Email Fields

| Field | Description | Example Value |
|-------|-------------|---------------|
| `subject` | Email subject line | `"Invoice for March 2024"` |
| `from` | Sender's email address | `"boss@company.com"` or `"John Doe <john@example.com>"` |
| `to` | Recipient email address(es) | `"user@example.com"` |
| `cc` | CC'd email address(es) | `"manager@example.com"` |
| `reply-to` | Reply-To header | `"support@company.com"` |
| `sender` | Sender header (may differ from From) | `"noreply@company.com"` |

## Match Types

| Match Type | Description | Example |
|------------|-------------|---------|
| `contains` | Pattern appears anywhere in field | Pattern `"work"` matches `"[WORK] Task"` |
| `exact` | Field exactly matches pattern | Pattern `"Hello"` matches only `"Hello"` |
| `starts_with` | Field starts with pattern | Pattern `"Re:"` matches `"Re: Your email"` |
| `ends_with` | Field ends with pattern | Pattern `"Report"` matches `"Daily Report"` |
| `regex` | Regular expression pattern | Pattern `"@.*\.com$"` matches any .com email |

## Common Patterns

### Filter All Emails from a Domain
```json
{
  "field": "from",
  "pattern": "@company\\.com$",
  "match_type": "regex"
}
```

### Filter Mailing List Emails
```json
{
  "field": "to",
  "pattern": "list@company.com",
  "match_type": "contains"
}
```

### Filter Automated Emails
```json
{
  "field": "from",
  "pattern": "noreply@|no-reply@|donotreply@",
  "match_type": "regex"
}
```

### Filter by Multiple Keywords
```json
{
  "field": "subject",
  "pattern": "urgent|important|asap|critical",
  "match_type": "regex"
}
```

### Filter Emails You're CC'd On
```json
{
  "field": "cc",
  "pattern": "yourname@",
  "match_type": "contains"
}
```

## Rule Priority

- Rules are evaluated in order from top to bottom
- First matching rule wins
- Put more specific rules before general rules

### Example:
```json
{
  "rules": [
    {
      "name": "Boss emails (specific)",
      "field": "from",
      "pattern": "boss@company.com",
      "target_folder": "Boss"
    },
    {
      "name": "All company emails (general)",
      "field": "from",
      "pattern": "@company.com",
      "target_folder": "Company"
    }
  ]
}
```

In this example:
- Emails from boss@company.com ? `.Boss` folder
- Other emails from @company.com ? `.Company` folder

## Tips

1. **Use dry-run first**: Always test with `--dry-run` before running for real
2. **Start specific, then general**: Put specific rules first
3. **Use regex for complex patterns**: Regex is powerful for multiple conditions
4. **Case sensitivity**: Most email filtering should use `case_sensitive: false`
5. **Test incrementally**: Add one or two rules at a time and test

## Common Regex Patterns

| Pattern | Matches | Use Case |
|---------|---------|----------|
| `@domain\\.com$` | Emails ending with @domain.com | Filter by domain |
| `^.*@.*\\.com$` | Any .com email address | Filter .com emails |
| `keyword1\|keyword2` | Either keyword1 OR keyword2 | Multiple keywords |
| `^\\[.*\\]` | Subject starting with [anything] | Tags in brackets |
| `\\d{4,}` | 4 or more consecutive digits | Order numbers, IDs |

## Troubleshooting

### Rule not matching?
1. Run with `--verbose --dry-run` to see what's being matched
2. Check the actual email headers (some fields may be formatted differently)
3. Try `contains` instead of `exact` or `starts_with`
4. Ensure `case_sensitive: false` unless you need exact case

### Emails going to wrong folder?
- Check rule order - first match wins
- More specific rules should come before general ones

### No emails being filtered?
- Verify the `field` name is correct (lowercase)
- Check that the pattern exists in that field
- Use `--verbose` to see debug information
