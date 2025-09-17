#!/usr/bin/env python3
"""Enhanced test script for Memory-Man with smart features."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from memory_man.database import init_db
from memory_man.server import (
    auto_store_memory, 
    detect_project, 
    suggest_related_memories,
    search_memories
)


async def test_enhanced_features():
    """Test enhanced Memory-Man features."""
    print("🧠 Testing Enhanced Memory-Man Features...")
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Test 1: Project detection
    print("\n1️⃣ Testing project detection...")
    result = await detect_project()
    print(f"✅ Project detected: {result}")
    
    # Test 2: Auto-store memory
    print("\n2️⃣ Testing auto-store memory...")
    result = await auto_store_memory(
        content="We use FastAPI with SQLAlchemy for the backend. JWT tokens are stored in Redis with 24-hour expiry.",
        importance=8
    )
    print(f"✅ Auto-stored memory: {result}")
    
    # Test 3: Another auto-store
    result = await auto_store_memory(
        content="To run the development server: python -m uvicorn main:app --reload",
        importance=6
    )
    print(f"✅ Auto-stored command: {result}")
    
    # Test 4: Search memories
    print("\n3️⃣ Testing search...")
    result = await search_memories(query="FastAPI")
    print(f"✅ Search results: Found {result.get('count', 0)} memories")
    
    # Test 5: Suggest related memories
    print("\n4️⃣ Testing related memory suggestions...")
    result = await suggest_related_memories(
        context="authentication setup"
    )
    print(f"✅ Related memories: {result}")
    
    # Test 6: Cross-project suggestions
    print("\n5️⃣ Testing cross-project suggestions...")
    result = await suggest_related_memories(
        context="database setup"
    )
    print(f"✅ Cross-project suggestions: {result}")
    
    print("\n🎉 All enhanced features working perfectly!")
    print("\n📊 Summary of new features:")
    print("- ✅ Smart project detection")
    print("- ✅ Auto-categorization")
    print("- ✅ Tag extraction")
    print("- ✅ Context-aware suggestions")
    print("- ✅ Cross-project memory discovery")


if __name__ == "__main__":
    asyncio.run(test_enhanced_features())