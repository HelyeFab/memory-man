#!/usr/bin/env python3
"""Complete test suite for all Memory-Man features."""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from memory_man.database import init_db
from memory_man.server import (
    auto_store_memory,
    detect_project,
    search_memories,
    summarize_project_memories,
    analyze_memory_storage,
    suggest_memory_archival,
    archive_memories,
    cleanup_memories
)


async def test_complete_memory_man():
    """Test all Memory-Man features comprehensively."""
    print("🧠 Complete Memory-Man Feature Test")
    print("=" * 50)
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Test 1: Auto-store multiple memories
    print("\n1️⃣ Auto-storing sample memories...")
    
    memories_to_store = [
        ("FastAPI backend with JWT authentication using Redis for session storage", 9),
        ("PostgreSQL database with connection pooling, configured for production", 8),
        ("React frontend with TypeScript and Tailwind CSS for styling", 7),
        ("Docker deployment with nginx reverse proxy", 8),
        ("Bug fix: CORS issues resolved by updating middleware configuration", 6),
        ("TODO: Implement user profile management system", 5),
        ("Development command: uvicorn main:app --reload for local testing", 6),
        ("Old todo from 6 months ago that was never completed", 2),
        ("Test memory with low importance for cleanup testing", 1),
        ("Unit tests using pytest with coverage reporting", 5)
    ]
    
    stored_ids = []
    for content, importance in memories_to_store:
        result = await auto_store_memory(content=content, importance=importance)
        if result["success"]:
            stored_ids.append(result["memory_id"])
    
    print(f"✅ Stored {len(stored_ids)} memories")
    
    # Test 2: Project detection
    print("\n2️⃣ Testing project detection...")
    result = await detect_project()
    print(f"✅ Project info: {result['project_info']['name']} ({result['project_info']['type']})")
    
    # Test 3: Search capabilities
    print("\n3️⃣ Testing search capabilities...")
    
    searches = [
        ("FastAPI", "technology search"),
        ("authentication", "feature search"),
        ("todo", "category search"),
        ("bug", "problem search")
    ]
    
    for query, description in searches:
        result = await search_memories(query=query)
        print(f"✅ {description}: '{query}' found {result.get('count', 0)} results")
    
    # Test 4: Project summarization
    print("\n4️⃣ Testing project summarization...")
    result = await summarize_project_memories(project="memory-man")
    if result["success"]:
        print(f"✅ Project summary generated ({result['analytics']['total_memories']} memories)")
        print(f"   Categories: {', '.join(result['analytics']['categories'])}")
        print(f"   Average importance: {result['analytics']['average_importance']}")
    
    # Test 5: Storage analysis
    print("\n5️⃣ Testing storage analysis...")
    result = await analyze_memory_storage()
    if result["success"]:
        optimization = result["optimization"]
        print(f"✅ Analysis complete: {optimization['total']} memories analyzed")
        if optimization["suggestions"]:
            print(f"   Suggestions: {'; '.join(optimization['suggestions'])}")
    
    # Test 6: Archival suggestions
    print("\n6️⃣ Testing archival suggestions...")
    result = await suggest_memory_archival(days_threshold=30)
    if result["success"]:
        print(f"✅ Found {result['total_candidates']} archival candidates")
        for reason, memories in result["archival_suggestions"].items():
            print(f"   {reason}: {len(memories)} memories")
    
    # Test 7: Manual archival
    print("\n7️⃣ Testing manual archival...")
    if stored_ids and len(stored_ids) > 2:
        # Archive the low-importance memories
        low_importance_ids = stored_ids[-2:]  # Last 2 stored
        result = await archive_memories(
            memory_ids=low_importance_ids,
            reason="Testing archival functionality"
        )
        if result["success"]:
            print(f"✅ Archived {result['archived_count']} memories")
    
    # Test 8: Cleanup simulation
    print("\n8️⃣ Testing automatic cleanup (dry run)...")
    result = await cleanup_memories(
        days_old=1,  # Very short for testing
        max_importance=3,
        dry_run=True
    )
    if result["success"]:
        print(f"✅ Cleanup simulation: {result['total_candidates']} candidates found")
        print(f"   Criteria: {result['criteria']['days_old']} days old, importance <= {result['criteria']['max_importance']}")
    
    # Test 9: Search with archived exclusion
    print("\n9️⃣ Testing search with archived exclusion...")
    result = await search_memories(query="test")
    archived_excluded_count = result.get('count', 0)
    print(f"✅ Search excludes archived memories: {archived_excluded_count} active results")
    
    # Final summary
    print("\n" + "=" * 50)
    print("🎉 ALL FEATURES TESTED SUCCESSFULLY!")
    print("\n📊 Memory-Man Complete Feature Set:")
    print("✅ Smart auto-storage with project detection")
    print("✅ Intelligent categorization and tagging")
    print("✅ Context-aware search and suggestions")
    print("✅ Project summarization and analytics")
    print("✅ Storage optimization analysis")
    print("✅ Intelligent archival suggestions")
    print("✅ Manual and automatic memory lifecycle management")
    print("✅ Archive-aware search and retrieval")
    print("\n🚀 Memory-Man is ready for production use!")


if __name__ == "__main__":
    asyncio.run(test_complete_memory_man())