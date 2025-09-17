#!/usr/bin/env python3
"""Test script to verify Memory-Man server is working."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from memory_man.database import init_db
from memory_man.server import store_memory, search_memories, list_projects


async def test_memory_man():
    """Test basic Memory-Man functionality."""
    print("🧠 Testing Memory-Man...")
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Test storing a memory
    result = await store_memory(
        content="The authentication system uses JWT tokens stored in Redis with a 24-hour expiry",
        category="architecture",
        project="my-web-app",
        tags=["auth", "jwt", "redis"],
        importance=8
    )
    print(f"✅ Memory stored: {result}")
    
    # Test searching
    result = await search_memories(query="JWT")
    print(f"✅ Search results: {result}")
    
    # Test listing projects
    result = await list_projects()
    print(f"✅ Projects: {result}")
    
    print("\n🎉 All tests passed! Memory-Man is ready to use.")


if __name__ == "__main__":
    asyncio.run(test_memory_man())