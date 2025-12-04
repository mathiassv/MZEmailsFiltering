#!/usr/bin/env python3
"""
Email Filter Script for Maildir
Moves emails from 'new' or 'cur' folders to user-defined folders based on subject matching rules.
"""

import os
import sys
import re
import json
import shutil
import logging
from pathlib import Path
from email import policy
from email.parser import BytesParser
from typing import List, Dict, Tuple


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailFilter:
    """Filters emails in Maildir format based on subject matching rules."""
    
    def __init__(self, maildir_path: str, rules_file: str, dry_run: bool = False):
        """
        Initialize the email filter.
        
        Args:
            maildir_path: Path to the user's maildir (contains cur, new, tmp folders)
            rules_file: Path to the JSON rules configuration file
            dry_run: If True, don't actually move files, just log what would happen
        """
        self.maildir_path = Path(maildir_path)
        self.rules_file = rules_file
        self.dry_run = dry_run
        self.rules = []
        
        # Validate maildir structure
        self._validate_maildir()
        
        # Load filtering rules
        self._load_rules()
    
    def _validate_maildir(self):
        """Validate that the maildir has the required structure."""
        if not self.maildir_path.exists():
            raise ValueError(f"Maildir path does not exist: {self.maildir_path}")
        
        required_folders = ['cur', 'new', 'tmp']
        for folder in required_folders:
            folder_path = self.maildir_path / folder
            if not folder_path.exists():
                raise ValueError(f"Required folder missing: {folder_path}")
        
        logger.info(f"Maildir validated: {self.maildir_path}")
    
    def _load_rules(self):
        """Load filtering rules from JSON configuration file."""
        try:
            with open(self.rules_file, 'r') as f:
                config = json.load(f)
                self.rules = config.get('rules', [])
            
            if not self.rules:
                logger.warning("No rules found in configuration file")
            else:
                logger.info(f"Loaded {len(self.rules)} filtering rules")
                
        except FileNotFoundError:
            logger.error(f"Rules file not found: {self.rules_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in rules file: {e}")
            raise
    
    def _ensure_target_folder(self, folder_name: str) -> Path:
        """
        Ensure the target folder exists with proper Maildir structure.
        
        Args:
            folder_name: Name of the folder (e.g., 'Stuff', will be created as '.Stuff')
        
        Returns:
            Path to the target folder's 'cur' directory
        """
        # Add leading dot if not present
        if not folder_name.startswith('.'):
            folder_name = f'.{folder_name}'
        
        target_folder = self.maildir_path / folder_name
        
        # Create Maildir structure if it doesn't exist
        for subfolder in ['cur', 'new', 'tmp']:
            subfolder_path = target_folder / subfolder
            if not subfolder_path.exists():
                if not self.dry_run:
                    subfolder_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created folder: {subfolder_path}")
                else:
                    logger.info(f"[DRY RUN] Would create folder: {subfolder_path}")
        
        return target_folder / 'cur'
    
    def _get_email_headers(self, email_path: Path) -> Dict[str, str]:
        """
        Extract relevant headers from an email file.
        
        Args:
            email_path: Path to the email file
        
        Returns:
            Dictionary with email headers (subject, from, to, cc, etc.)
        """
        try:
            with open(email_path, 'rb') as f:
                msg = BytesParser(policy=policy.default).parse(f)
                return {
                    'subject': str(msg.get('Subject', '')),
                    'from': str(msg.get('From', '')),
                    'to': str(msg.get('To', '')),
                    'cc': str(msg.get('Cc', '')),
                    'reply-to': str(msg.get('Reply-To', '')),
                    'sender': str(msg.get('Sender', ''))
                }
        except Exception as e:
            logger.error(f"Error parsing email {email_path}: {e}")
            return {}
    
    def _match_rule(self, headers: Dict[str, str], rule: Dict) -> bool:
        """
        Check if email headers match a rule.
        
        Args:
            headers: Dictionary with email headers
            rule: Rule dictionary containing 'pattern', 'match_type', and 'field'
        
        Returns:
            True if the headers match the rule
        """
        pattern = rule.get('pattern', '')
        match_type = rule.get('match_type', 'contains')
        case_sensitive = rule.get('case_sensitive', False)
        field = rule.get('field', 'subject').lower()
        
        # Get the field value to match against
        field_value = headers.get(field, '')
        
        if not field_value:
            logger.debug(f"Field '{field}' is empty or not found")
            return False
        
        if not case_sensitive:
            field_value = field_value.lower()
            pattern = pattern.lower()
        
        if match_type == 'contains':
            return pattern in field_value
        elif match_type == 'exact':
            return field_value == pattern
        elif match_type == 'starts_with':
            return field_value.startswith(pattern)
        elif match_type == 'ends_with':
            return field_value.endswith(pattern)
        elif match_type == 'regex':
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                return bool(re.search(pattern, field_value, flags))
            except re.error as e:
                logger.error(f"Invalid regex pattern '{pattern}': {e}")
                return False
        else:
            logger.warning(f"Unknown match type: {match_type}")
            return False
    
    def _move_email(self, email_path: Path, target_folder: Path) -> bool:
        """
        Move an email to the target folder.
        
        Args:
            email_path: Path to the email file
            target_folder: Path to the target 'cur' folder
        
        Returns:
            True if successful, False otherwise
        """
        try:
            target_path = target_folder / email_path.name
            
            if not self.dry_run:
                shutil.move(str(email_path), str(target_path))
                logger.info(f"Moved: {email_path.name} -> {target_folder.parent.name}")
            else:
                logger.info(f"[DRY RUN] Would move: {email_path.name} -> {target_folder.parent.name}")
            
            return True
        except Exception as e:
            logger.error(f"Error moving email {email_path}: {e}")
            return False
    
    def process_emails(self, folders: List[str] = None) -> Tuple[int, int]:
        """
        Process emails in the specified folders.
        
        Args:
            folders: List of folders to process (default: ['new', 'cur'])
        
        Returns:
            Tuple of (processed_count, moved_count)
        """
        if folders is None:
            folders = ['new', 'cur']
        
        processed = 0
        moved = 0
        
        for folder in folders:
            folder_path = self.maildir_path / folder
            
            if not folder_path.exists():
                logger.warning(f"Folder does not exist: {folder_path}")
                continue
            
            # Get all email files in the folder
            email_files = [f for f in folder_path.iterdir() if f.is_file()]
            logger.info(f"Processing {len(email_files)} emails in '{folder}' folder")
            
            for email_file in email_files:
                processed += 1
                headers = self._get_email_headers(email_file)
                
                if not headers:
                    logger.debug(f"Skipping email with no headers: {email_file.name}")
                    continue
                
                # Check each rule
                for rule in self.rules:
                    if self._match_rule(headers, rule):
                        target_folder_name = rule.get('target_folder')
                        
                        if not target_folder_name:
                            logger.warning(f"Rule has no target_folder: {rule}")
                            continue
                        
                        target_folder = self._ensure_target_folder(target_folder_name)
                        
                        if self._move_email(email_file, target_folder):
                            moved += 1
                        
                        # Only apply first matching rule
                        break
        
        return processed, moved
    
    def run(self):
        """Run the email filtering process."""
        logger.info("=" * 60)
        logger.info("Starting email filtering")
        logger.info(f"Maildir: {self.maildir_path}")
        logger.info(f"Rules file: {self.rules_file}")
        logger.info(f"Dry run: {self.dry_run}")
        logger.info("=" * 60)
        
        processed, moved = self.process_emails()
        
        logger.info("=" * 60)
        logger.info(f"Filtering complete")
        logger.info(f"Processed: {processed} emails")
        logger.info(f"Moved: {moved} emails")
        logger.info("=" * 60)
        
        return processed, moved


def main():
    """Main entry point for the script."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Filter emails in Maildir format based on subject matching rules'
    )
    parser.add_argument(
        'maildir',
        help='Path to the maildir folder (contains cur, new, tmp)'
    )
    parser.add_argument(
        '--rules',
        default='filter_rules.json',
        help='Path to the JSON rules file (default: filter_rules.json)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        dest='dry_run',
        help='Perform a dry run without actually moving files'
    )
    parser.add_argument(
        '--folders',
        nargs='+',
        default=['new', 'cur'],
        help='Folders to process (default: new cur)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    try:
        filter_instance = EmailFilter(args.maildir, args.rules, args.dry_run)
        filter_instance.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
