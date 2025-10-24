#!/usr/bin/env python3
"""
Memory Man - Export/Import Tool with Secret Sanitization

This tool allows safe synchronization of memories across machines by:
1. Exporting memories to JSON with secrets sanitized
2. Importing memories from sanitized JSON exports
3. Version controlling the sanitized exports, not the raw database

Usage:
    python memory_sync.py export [--output FILE]
    python memory_sync.py import [--input FILE]
    python memory_sync.py sanitize-test  # Test sanitization on sample data
"""

import json
import re
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


class SecretSanitizer:
    """Sanitizes various types of secrets from text"""

    PATTERNS = {
        # API Keys and Tokens
        'stripe_key': (r'sk_test_[a-zA-Z0-9]{24,}', '[STRIPE_TEST_KEY_REDACTED]'),
        'stripe_live_key': (r'sk_live_[a-zA-Z0-9]{24,}', '[STRIPE_LIVE_KEY_REDACTED]'),
        'stripe_publish': (r'pk_(test|live)_[a-zA-Z0-9]{24,}', '[STRIPE_PUBLISH_KEY_REDACTED]'),
        'github_token': (r'gh[ps]_[a-zA-Z0-9]{36,}', '[GITHUB_TOKEN_REDACTED]'),
        'generic_api_key': (r'(?i)api[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{32,})', r'api_key: [API_KEY_REDACTED]'),
        'bearer_token': (r'Bearer\s+[a-zA-Z0-9_\-\.]{20,}', 'Bearer [TOKEN_REDACTED]'),
        'jwt': (r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', '[JWT_TOKEN_REDACTED]'),

        # AWS Credentials
        'aws_access_key': (r'AKIA[0-9A-Z]{16}', '[AWS_ACCESS_KEY_REDACTED]'),
        'aws_secret': (r'(?i)aws[_-]?secret[_-]?access[_-]?key["\']?\s*[:=]\s*["\']?([a-zA-Z0-9/+=]{40})', 'aws_secret_access_key: [AWS_SECRET_REDACTED]'),

        # Generic patterns
        'password': (r'(?i)password["\']?\s*[:=]\s*["\']?([^\s\'"]{8,})', 'password: [PASSWORD_REDACTED]'),
        'secret': (r'(?i)secret["\']?\s*[:=]\s*["\']?([a-zA-Z0-9_\-]{16,})', 'secret: [SECRET_REDACTED]'),
        'private_key_header': (r'-----BEGIN (?:RSA )?PRIVATE KEY-----', '[PRIVATE_KEY_REDACTED]'),
    }

    @classmethod
    def sanitize(cls, text: str) -> tuple[str, int]:
        """
        Sanitize secrets from text.
        Returns: (sanitized_text, redaction_count)
        """
        if not text:
            return text, 0

        sanitized = text
        redaction_count = 0

        for name, (pattern, replacement) in cls.PATTERNS.items():
            matches = re.findall(pattern, sanitized)
            if matches:
                sanitized = re.sub(pattern, replacement, sanitized)
                redaction_count += len(matches)

        return sanitized, redaction_count


class MemorySync:
    """Handles export/import of memories with sanitization"""

    def __init__(self, db_path: str = "memory_man.db"):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found: {self.db_path}")

    def export(self, output_path: str = None) -> Dict[str, Any]:
        """Export memories to sanitized JSON"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"memories_export_{timestamp}.json"

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get all memories
        cursor.execute("""
            SELECT id, project_name, category, content, tags, importance, context,
                   created_at, updated_at, accessed_at, access_count,
                   is_archived, archived_at, archived_reason
            FROM memories
            ORDER BY id
        """)

        memories = []
        total_redactions = 0

        for row in cursor.fetchall():
            memory = dict(row)

            # Sanitize the content
            original_content = memory['content']
            sanitized_content, redactions = SecretSanitizer.sanitize(original_content)
            memory['content'] = sanitized_content

            if redactions > 0:
                memory['_sanitized'] = True
                memory['_redaction_count'] = redactions
                total_redactions += redactions

            memories.append(memory)

        conn.close()

        export_data = {
            'version': '1.0',
            'exported_at': datetime.now().isoformat(),
            'database_path': str(self.db_path),
            'total_memories': len(memories),
            'total_redactions': total_redactions,
            'memories': memories
        }

        # Write to file
        output_file = Path(output_path)
        with output_file.open('w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Exported {len(memories)} memories to {output_file}")
        print(f"  - {total_redactions} secrets redacted")
        print(f"  - File size: {output_file.stat().st_size:,} bytes")

        return export_data

    def import_memories(self, input_path: str, merge: bool = True) -> int:
        """
        Import memories from JSON export.

        Args:
            input_path: Path to JSON export file
            merge: If True, merge with existing memories (skip duplicates by ID)
                   If False, clear database before import

        Returns:
            Number of memories imported
        """
        input_file = Path(input_path)
        if not input_file.exists():
            raise FileNotFoundError(f"Export file not found: {input_file}")

        with input_file.open('r', encoding='utf-8') as f:
            export_data = json.load(f)

        memories = export_data.get('memories', [])

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if not merge:
            # Clear existing memories
            cursor.execute("DELETE FROM memories")
            print("⚠ Cleared existing memories")

        imported = 0
        skipped = 0

        for memory in memories:
            if merge:
                # Check if memory already exists
                cursor.execute("SELECT id FROM memories WHERE id = ?", (memory['id'],))
                if cursor.fetchone():
                    skipped += 1
                    continue

            # Insert memory (without sanitization flags)
            cursor.execute("""
                INSERT INTO memories (
                    id, project_name, category, content, tags, importance, context,
                    created_at, updated_at, accessed_at, access_count,
                    is_archived, archived_at, archived_reason
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                memory['id'],
                memory.get('project_name'),
                memory.get('category'),
                memory['content'],
                memory.get('tags'),
                memory.get('importance', 5),
                memory.get('context'),
                memory['created_at'],
                memory['updated_at'],
                memory.get('accessed_at'),
                memory.get('access_count', 0),
                memory.get('is_archived', 0),
                memory.get('archived_at'),
                memory.get('archived_reason')
            ))
            imported += 1

        conn.commit()
        conn.close()

        print(f"✓ Imported {imported} memories from {input_file}")
        if skipped > 0:
            print(f"  - {skipped} memories skipped (already exist)")

        return imported

    def sanitize_test(self):
        """Test the sanitization on sample data"""
        test_cases = [
            "Our Stripe key is sk_test_51HxYz1234567890abcdefghijk",
            "Use this token: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.payload.signature",
            "API_KEY=abc123def456ghi789jkl012mno345pqr",
            'password: "MySecretP@ssw0rd"',
            "AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE",
            "Nothing secret here!",
        ]

        print("Sanitization Test Results:")
        print("=" * 80)

        for i, test in enumerate(test_cases, 1):
            sanitized, count = SecretSanitizer.sanitize(test)
            status = "✓ REDACTED" if count > 0 else "○ CLEAN"
            print(f"\n{status} Test {i}:")
            print(f"  Original:  {test}")
            print(f"  Sanitized: {sanitized}")
            print(f"  Redactions: {count}")


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]
    sync = MemorySync()

    if command == 'export':
        output = sys.argv[2] if len(sys.argv) > 2 else None
        sync.export(output)

    elif command == 'import':
        if len(sys.argv) < 3:
            print("Error: Import requires input file")
            print("Usage: python memory_sync.py import <file>")
            sys.exit(1)
        sync.import_memories(sys.argv[2])

    elif command == 'sanitize-test':
        sync.sanitize_test()

    else:
        print(f"Error: Unknown command '{command}'")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
