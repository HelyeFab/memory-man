#!/usr/bin/env python3
"""
Migrate memories from scattered project databases to the centralized database.
This script will merge all memories while preserving their data and avoiding duplicates.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Database locations
CENTRAL_DB = "/home/beano/.claude/memory_man.db"
SCATTERED_DBS = [
    "/home/beano/DevProjects/next_js/moshimoshi/data/memories.db",
    "/home/beano/DevProjects/python/MCP_SERVERS/memory-man/data/memories.db"
]

def get_db_schema(db_path: str) -> List[str]:
    """Get the schema of the memories table."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(memories)")
    columns = cursor.fetchall()
    conn.close()
    return [col[1] for col in columns]

def create_central_db_if_not_exists():
    """Create the central database with proper schema if it doesn't exist."""
    central_path = Path(CENTRAL_DB)
    central_path.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(CENTRAL_DB)
    cursor = conn.cursor()

    # Create table with the full schema
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_name VARCHAR(255) NOT NULL,
            category VARCHAR(100) NOT NULL,
            content TEXT NOT NULL,
            tags JSON,
            importance INTEGER,
            context JSON,
            created_at DATETIME NOT NULL,
            updated_at DATETIME,
            accessed_at DATETIME,
            access_count INTEGER,
            is_archived INTEGER,
            archived_at DATETIME,
            archived_reason VARCHAR(255),
            search_text TEXT
        )
    """)

    conn.commit()
    conn.close()
    print(f"✓ Central database ready at {CENTRAL_DB}")

def get_all_memories(db_path: str) -> List[Dict[str, Any]]:
    """Fetch all memories from a database."""
    if not Path(db_path).exists():
        print(f"  Database not found: {db_path}")
        return []

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM memories WHERE is_archived = 0 OR is_archived IS NULL")
    memories = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return memories

def memory_exists(conn: sqlite3.Connection, memory: Dict[str, Any]) -> bool:
    """Check if a memory already exists in the database."""
    cursor = conn.cursor()

    # Check for duplicate based on project, content, and creation time
    cursor.execute("""
        SELECT COUNT(*) FROM memories
        WHERE project_name = ? AND content = ? AND created_at = ?
    """, (memory['project_name'], memory['content'], memory['created_at']))

    count = cursor.fetchone()[0]
    return count > 0

def migrate_memory(conn: sqlite3.Connection, memory: Dict[str, Any]) -> bool:
    """Migrate a single memory to the central database."""
    if memory_exists(conn, memory):
        return False

    cursor = conn.cursor()

    # Insert the memory (excluding the id field to let it auto-increment)
    cursor.execute("""
        INSERT INTO memories (
            project_name, category, content, tags, importance, context,
            created_at, updated_at, accessed_at, access_count,
            is_archived, archived_at, archived_reason, search_text
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        memory['project_name'],
        memory['category'],
        memory['content'],
        json.dumps(memory['tags']) if memory.get('tags') and not isinstance(memory['tags'], str) else memory.get('tags'),
        memory.get('importance'),
        json.dumps(memory['context']) if memory.get('context') and not isinstance(memory['context'], str) else memory.get('context'),
        memory['created_at'],
        memory.get('updated_at'),
        memory.get('accessed_at'),
        memory.get('access_count', 0),
        memory.get('is_archived', 0),
        memory.get('archived_at'),
        memory.get('archived_reason'),
        memory.get('search_text')
    ))

    return True

def main():
    """Main migration function."""
    print("Memory Database Migration Script")
    print("=" * 50)

    # Create central database if needed
    create_central_db_if_not_exists()

    # Connect to central database
    central_conn = sqlite3.connect(CENTRAL_DB)

    total_migrated = 0
    total_skipped = 0

    # Process each scattered database
    for db_path in SCATTERED_DBS:
        print(f"\nProcessing: {db_path}")

        memories = get_all_memories(db_path)
        if not memories:
            continue

        print(f"  Found {len(memories)} memories")

        migrated = 0
        skipped = 0

        for memory in memories:
            if migrate_memory(central_conn, memory):
                migrated += 1
            else:
                skipped += 1

        central_conn.commit()

        print(f"  ✓ Migrated: {migrated}")
        print(f"  → Skipped (duplicates): {skipped}")

        total_migrated += migrated
        total_skipped += skipped

    # Get final count
    cursor = central_conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM memories")
    total_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT project_name) FROM memories")
    project_count = cursor.fetchone()[0]

    central_conn.close()

    print("\n" + "=" * 50)
    print("Migration Complete!")
    print(f"  Total memories migrated: {total_migrated}")
    print(f"  Total duplicates skipped: {total_skipped}")
    print(f"  Total memories in central DB: {total_count}")
    print(f"  Total projects: {project_count}")
    print(f"\nCentral database: {CENTRAL_DB}")

    # Suggest cleanup
    if total_migrated > 0:
        print("\n⚠️  You can now safely delete the scattered databases:")
        for db_path in SCATTERED_DBS:
            if Path(db_path).exists():
                print(f"  rm -rf {Path(db_path).parent}")

if __name__ == "__main__":
    main()