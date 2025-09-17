#!/usr/bin/env python3
"""Backup memories to JSON file."""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from memory_man.database import get_db
from memory_man.models.memory import Memory
from sqlalchemy import select


async def backup_memories():
    """Backup all memories to JSON."""
    print("📦 Backing up memories...")
    
    async with get_db() as db:
        stmt = select(Memory)
        result = await db.execute(stmt)
        memories = result.scalars().all()
        
        backup_data = {
            "created_at": datetime.now().isoformat(),
            "count": len(memories),
            "memories": [memory.to_dict() for memory in memories]
        }
        
        # Create backup file
        backup_file = Path(f"backup_memories_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        
        with open(backup_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        
        print(f"✅ Backed up {len(memories)} memories to {backup_file}")


if __name__ == "__main__":
    asyncio.run(backup_memories())