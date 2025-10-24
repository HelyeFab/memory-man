# Memory-Man Cross-Machine Sync Workflow

## Problem
The memory-man database contains sensitive information (API keys, passwords, tokens) that **cannot be committed to GitHub**. However, we need to sync memories across multiple development machines.

## Solution
We use a **sanitized export/import system**:
1. Export memories to JSON with secrets automatically redacted
2. Track the sanitized JSON in git (safe for GitHub)
3. Import the sanitized export on other machines
4. Keep the full database local (with secrets) and gitignored

## Quick Start

### Initial Setup (One Time)
```bash
# Clone the repository on your new machine
git clone https://github.com/HelyeFab/memory-man.git
cd memory-man

# Import the sanitized memories
python3 memory_sync.py import exports/memories_sanitized.json
```

### Regular Workflow

#### When you add/update memories:
```bash
# 1. Export with sanitization (this creates/updates the export)
python3 memory_sync.py export exports/memories_sanitized.json

# 2. Commit the sanitized export
git add exports/memories_sanitized.json
git commit -m "Update memories export"
git push
```

#### On another machine:
```bash
# 1. Pull the latest changes
git pull

# 2. Import the updated memories (merge mode by default)
python3 memory_sync.py import exports/memories_sanitized.json
```

## What Gets Sanitized?

The export tool automatically redacts:
- **API Keys**: Stripe, GitHub, Generic API keys
- **Tokens**: Bearer tokens, JWT tokens
- **AWS Credentials**: Access keys, Secret keys
- **Passwords**: Any password fields
- **Private Keys**: SSH/TLS private keys
- **Secrets**: Generic secret patterns

Redacted secrets are replaced with placeholders like `[STRIPE_TEST_KEY_REDACTED]`, so you can still understand the context without exposing the actual secrets.

## Commands Reference

### Export
```bash
# Export to default timestamped file
python3 memory_sync.py export

# Export to specific file
python3 memory_sync.py export exports/memories_sanitized.json
```

Output shows:
- Number of memories exported
- Number of secrets redacted
- File size

### Import
```bash
# Import (merge with existing memories, skip duplicates)
python3 memory_sync.py import exports/memories_sanitized.json

# Import (replace all memories - USE WITH CAUTION)
# Note: This functionality requires modifying the script
```

### Test Sanitization
```bash
# Test the sanitization patterns on sample data
python3 memory_sync.py sanitize-test
```

## File Structure

```
memory-man/
├── memory_man.db              # Local database (GITIGNORED - contains secrets)
├── memory_sync.py             # Export/import tool
├── exports/                   # Sanitized exports (TRACKED in git)
│   └── memories_sanitized.json
└── SYNC_WORKFLOW.md          # This file
```

## Important Notes

1. **Never commit `memory_man.db`** - It contains secrets and is gitignored
2. **Always review exports** - Check the redaction count to ensure secrets were caught
3. **Merge by default** - Imports merge with existing memories (no data loss)
4. **Backup first** - Before major changes, backup your `memory_man.db` file
5. **Regular exports** - Export and commit regularly to keep machines in sync

## Troubleshooting

### "Database not found"
Make sure you're in the memory-man directory and the database exists:
```bash
ls -lh memory_man.db
```

### "Secrets detected in push"
If GitHub blocks your push, you likely committed the raw database by mistake:
```bash
# Remove database from git
git rm --cached memory_man.db
git commit -m "Remove database from git"
git push
```

### "Import shows 0 memories"
Check the export file exists and has content:
```bash
python3 -c "import json; print(json.load(open('exports/memories_sanitized.json'))['total_memories'])"
```

## Recovery from Data Loss

If you lost the database, you can recover from the latest export:
```bash
# Remove the corrupted database
mv memory_man.db memory_man.db.corrupted

# Create a fresh database schema
python3 -m memory_man  # Start server once to create schema

# Import from the sanitized export
python3 memory_sync.py import exports/memories_sanitized.json
```

**Note**: Sanitized exports don't contain the original secrets. If critical secrets were lost, check:
1. Git history (if database was previously tracked)
2. Local backups
3. Other machines that might have the full database

## Statistics

Current database:
- **261 memories** across multiple projects
- **8 secrets redacted** in the sanitized export
- **~1MB** database size, **~540KB** sanitized export

---

**Last Updated**: 2025-10-24
**Version**: 1.0
