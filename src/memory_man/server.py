"""MCP Server for Memory-Man."""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    EmbeddedResource,
)
from sqlalchemy import and_, desc, func, or_, select

from .config import settings
from .database import get_db, init_db
from .models.memory import Memory
from .utils.project_detector import (
    detect_project_info,
    get_project_context,
    suggest_memory_category,
    extract_tags_from_content,
)
from .utils.summarizer import MemorySummarizer

# Set up logging - MUST use stderr for MCP servers (stdout is for JSON-RPC)
import sys
logging.basicConfig(
    level=settings.log_level,
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create MCP server instance
app = Server("memory-man")

# Initialize summarizer
summarizer = MemorySummarizer()


@app.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="memory_store",
            description="Store a new memory with project context",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content to remember"
                    },
                    "project": {
                        "type": "string",
                        "description": "Project name (defaults to current directory name)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Category: architecture, setup, bug_fix, todo, pattern, etc."
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional tags for better organization"
                    },
                    "importance": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "description": "Importance level (1-10, default 5)"
                    }
                },
                "required": ["content", "category"]
            }
        ),
        Tool(
            name="memory_search",
            description="Search memories by query, project, or category",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (searches content, tags, category)"
                    },
                    "project": {
                        "type": "string",
                        "description": "Filter by project name"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="memory_retrieve",
            description="Retrieve a specific memory by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "integer",
                        "description": "The ID of the memory to retrieve"
                    }
                },
                "required": ["memory_id"]
            }
        ),
        Tool(
            name="memory_update",
            description="Update an existing memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "integer",
                        "description": "The ID of the memory to update"
                    },
                    "content": {
                        "type": "string",
                        "description": "New content"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "New tags"
                    },
                    "importance": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "description": "New importance level"
                    }
                },
                "required": ["memory_id"]
            }
        ),
        Tool(
            name="memory_delete",
            description="Delete a memory",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "integer",
                        "description": "The ID of the memory to delete"
                    }
                },
                "required": ["memory_id"]
            }
        ),
        Tool(
            name="project_summary",
            description="Get a summary of memories for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name to summarize"
                    }
                },
                "required": ["project"]
            }
        ),
        Tool(
            name="memory_list_projects",
            description="List all projects with memories",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="memory_auto_store",
            description="Store memory with auto-detected project context and smart categorization",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content to remember"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Current working directory (optional, will detect from environment)"
                    },
                    "importance": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 10,
                        "description": "Importance level (1-10, default 5)"
                    }
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="project_detect",
            description="Detect and analyze current project information",
            inputSchema={
                "type": "object",
                "properties": {
                    "working_directory": {
                        "type": "string",
                        "description": "Directory to analyze (optional, defaults to current)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="memory_suggest_related",
            description="Find related memories based on current project context",
            inputSchema={
                "type": "object",
                "properties": {
                    "working_directory": {
                        "type": "string",
                        "description": "Current working directory"
                    },
                    "context": {
                        "type": "string",
                        "description": "Current task or problem context"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="memory_summarize_project",
            description="Generate an intelligent summary of all memories for a project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project name to summarize"
                    },
                    "include_archived": {
                        "type": "boolean",
                        "description": "Include archived memories in summary (default: false)"
                    }
                },
                "required": ["project"]
            }
        ),
        Tool(
            name="memory_analyze_storage",
            description="Analyze memory storage and suggest optimizations",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project to analyze (optional, analyzes all if not provided)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="memory_suggest_archival",
            description="Suggest memories that could be archived or cleaned up",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project to analyze (optional, analyzes all if not provided)"
                    },
                    "days_threshold": {
                        "type": "integer",
                        "description": "Consider memories older than this many days (default: 90)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="memory_archive",
            description="Archive one or more memories",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of memory IDs to archive"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for archiving (optional)"
                    }
                },
                "required": ["memory_ids"]
            }
        ),
        Tool(
            name="memory_unarchive",
            description="Unarchive one or more memories",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "List of memory IDs to unarchive"
                    }
                },
                "required": ["memory_ids"]
            }
        ),
        Tool(
            name="memory_cleanup",
            description="Automatically clean up old, unused memories based on criteria",
            inputSchema={
                "type": "object",
                "properties": {
                    "project": {
                        "type": "string",
                        "description": "Project to clean up (optional, cleans all if not provided)"
                    },
                    "days_old": {
                        "type": "integer",
                        "description": "Archive memories older than this many days (default: 180)"
                    },
                    "max_importance": {
                        "type": "integer",
                        "description": "Only archive memories with importance <= this value (default: 3)"
                    },
                    "dry_run": {
                        "type": "boolean",
                        "description": "Show what would be archived without actually doing it (default: true)"
                    }
                },
                "required": []
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    
    if name == "memory_store":
        result = await store_memory(**arguments)
    elif name == "memory_search":
        result = await search_memories(**arguments)
    elif name == "memory_retrieve":
        result = await retrieve_memory(**arguments)
    elif name == "memory_update":
        result = await update_memory(**arguments)
    elif name == "memory_delete":
        result = await delete_memory(**arguments)
    elif name == "project_summary":
        result = await get_project_summary(**arguments)
    elif name == "memory_list_projects":
        result = await list_projects()
    elif name == "memory_auto_store":
        result = await auto_store_memory(**arguments)
    elif name == "project_detect":
        result = await detect_project(**arguments)
    elif name == "memory_suggest_related":
        result = await suggest_related_memories(**arguments)
    elif name == "memory_summarize_project":
        result = await summarize_project_memories(**arguments)
    elif name == "memory_analyze_storage":
        result = await analyze_memory_storage(**arguments)
    elif name == "memory_suggest_archival":
        result = await suggest_memory_archival(**arguments)
    elif name == "memory_archive":
        result = await archive_memories(**arguments)
    elif name == "memory_unarchive":
        result = await unarchive_memories(**arguments)
    elif name == "memory_cleanup":
        result = await cleanup_memories(**arguments)
    else:
        result = {"error": f"Unknown tool: {name}"}
    
    return [TextContent(type="text", text=str(result))]


async def store_memory(
    content: str,
    category: str,
    project: Optional[str] = None,
    tags: Optional[List[str]] = None,
    importance: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """Store a new memory."""
    try:
        async with get_db() as db:
            # Create search text for better searching
            search_text = f"{content} {category} {' '.join(tags or [])}".lower()
            
            memory = Memory(
                project_name=project or settings.default_project,
                category=category,
                content=content,
                tags=tags or [],
                importance=importance,
                search_text=search_text,
                context=kwargs,  # Store any additional context
            )
            
            db.add(memory)
            await db.commit()
            await db.refresh(memory)
            
            return {
                "success": True,
                "memory_id": memory.id,
                "message": f"Memory stored successfully (ID: {memory.id})"
            }
    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        return {"success": False, "error": str(e)}


async def search_memories(
    query: Optional[str] = None,
    project: Optional[str] = None,
    category: Optional[str] = None,
    limit: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Search memories."""
    try:
        async with get_db() as db:
            # Build query
            stmt = select(Memory)
            
            conditions = [Memory.is_archived == 0]  # Exclude archived by default
            if project:
                conditions.append(Memory.project_name == project)
            if category:
                conditions.append(Memory.category == category)
            if query:
                search_pattern = f"%{query.lower()}%"
                conditions.append(
                    or_(
                        Memory.search_text.like(search_pattern),
                        Memory.content.ilike(f"%{query}%")
                    )
                )
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            # Order by importance and recency
            stmt = stmt.order_by(desc(Memory.importance), desc(Memory.created_at))
            
            # Apply limit
            if limit:
                stmt = stmt.limit(limit)
            else:
                stmt = stmt.limit(settings.search_limit)
            
            result = await db.execute(stmt)
            memories = result.scalars().all()
            
            # Update access timestamps
            for memory in memories:
                memory.accessed_at = datetime.utcnow()
                memory.access_count += 1
            await db.commit()
            
            return {
                "success": True,
                "count": len(memories),
                "memories": [m.to_dict() for m in memories]
            }
    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        return {"success": False, "error": str(e)}


async def retrieve_memory(memory_id: int) -> Dict[str, Any]:
    """Retrieve a specific memory."""
    try:
        async with get_db() as db:
            stmt = select(Memory).where(Memory.id == memory_id)
            result = await db.execute(stmt)
            memory = result.scalar_one_or_none()
            
            if not memory:
                return {"success": False, "error": "Memory not found"}
            
            # Update access info
            memory.accessed_at = datetime.utcnow()
            memory.access_count += 1
            await db.commit()
            
            return {
                "success": True,
                "memory": memory.to_dict()
            }
    except Exception as e:
        logger.error(f"Error retrieving memory: {e}")
        return {"success": False, "error": str(e)}


async def update_memory(
    memory_id: int,
    content: Optional[str] = None,
    tags: Optional[List[str]] = None,
    importance: Optional[int] = None,
    **kwargs
) -> Dict[str, Any]:
    """Update an existing memory."""
    try:
        async with get_db() as db:
            stmt = select(Memory).where(Memory.id == memory_id)
            result = await db.execute(stmt)
            memory = result.scalar_one_or_none()
            
            if not memory:
                return {"success": False, "error": "Memory not found"}
            
            # Update fields
            if content is not None:
                memory.content = content
                memory.search_text = f"{content} {memory.category} {' '.join(tags or memory.tags or [])}".lower()
            if tags is not None:
                memory.tags = tags
            if importance is not None:
                memory.importance = importance
            
            memory.updated_at = datetime.utcnow()
            await db.commit()
            
            return {
                "success": True,
                "message": "Memory updated successfully",
                "memory": memory.to_dict()
            }
    except Exception as e:
        logger.error(f"Error updating memory: {e}")
        return {"success": False, "error": str(e)}


async def delete_memory(memory_id: int) -> Dict[str, Any]:
    """Delete a memory."""
    try:
        async with get_db() as db:
            stmt = select(Memory).where(Memory.id == memory_id)
            result = await db.execute(stmt)
            memory = result.scalar_one_or_none()
            
            if not memory:
                return {"success": False, "error": "Memory not found"}
            
            await db.delete(memory)
            await db.commit()
            
            return {
                "success": True,
                "message": f"Memory {memory_id} deleted successfully"
            }
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        return {"success": False, "error": str(e)}


async def get_project_summary(project: str) -> Dict[str, Any]:
    """Get a summary of memories for a project."""
    try:
        async with get_db() as db:
            # Get category counts
            stmt = select(
                Memory.category,
                func.count(Memory.id).label("count")
            ).where(
                Memory.project_name == project
            ).group_by(Memory.category)
            
            result = await db.execute(stmt)
            categories = {row.category: row.count for row in result}
            
            # Get recent memories
            stmt = select(Memory).where(
                Memory.project_name == project
            ).order_by(desc(Memory.created_at)).limit(5)
            
            result = await db.execute(stmt)
            recent = result.scalars().all()
            
            # Get important memories
            stmt = select(Memory).where(
                and_(
                    Memory.project_name == project,
                    Memory.importance >= 8
                )
            ).order_by(desc(Memory.importance))
            
            result = await db.execute(stmt)
            important = result.scalars().all()
            
            return {
                "success": True,
                "project": project,
                "summary": {
                    "total_memories": sum(categories.values()),
                    "categories": categories,
                    "recent_memories": [m.to_dict() for m in recent],
                    "important_memories": [m.to_dict() for m in important]
                }
            }
    except Exception as e:
        logger.error(f"Error getting project summary: {e}")
        return {"success": False, "error": str(e)}


async def list_projects() -> Dict[str, Any]:
    """List all projects with memories."""
    try:
        async with get_db() as db:
            stmt = select(
                Memory.project_name,
                func.count(Memory.id).label("memory_count"),
                func.max(Memory.created_at).label("last_updated")
            ).group_by(Memory.project_name).order_by(desc("memory_count"))
            
            result = await db.execute(stmt)
            projects = []
            for row in result:
                projects.append({
                    "project": row.project_name,
                    "memory_count": row.memory_count,
                    "last_updated": row.last_updated.isoformat() if row.last_updated else None
                })
            
            return {
                "success": True,
                "projects": projects
            }
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return {"success": False, "error": str(e)}


async def auto_store_memory(
    content: str,
    working_directory: Optional[str] = None,
    importance: int = 5,
    **kwargs
) -> Dict[str, Any]:
    """Store memory with auto-detected project context."""
    try:
        # Detect project information
        project_info = detect_project_info(working_directory)
        project_context = get_project_context(working_directory)
        
        # Smart categorization
        category = suggest_memory_category(content, project_info)
        
        # Auto-extract tags
        auto_tags = extract_tags_from_content(content, project_info)
        
        # Store the memory
        result = await store_memory(
            content=content,
            category=category,
            project=project_info["name"],
            tags=auto_tags,
            importance=importance,
            **project_context
        )
        
        if result["success"]:
            result["auto_detected"] = {
                "project": project_info["name"],
                "category": category,
                "tags": auto_tags,
                "project_type": project_info["type"],
                "language": project_info["language"],
                "framework": project_info["framework"]
            }
        
        return result
    except Exception as e:
        logger.error(f"Error auto-storing memory: {e}")
        return {"success": False, "error": str(e)}


async def detect_project(working_directory: Optional[str] = None) -> Dict[str, Any]:
    """Detect and analyze current project information."""
    try:
        project_info = detect_project_info(working_directory)
        project_context = get_project_context(working_directory)
        
        # Get existing memories for this project
        async with get_db() as db:
            stmt = select(func.count(Memory.id)).where(
                Memory.project_name == project_info["name"]
            )
            result = await db.execute(stmt)
            memory_count = result.scalar()
        
        return {
            "success": True,
            "project_info": project_info,
            "project_context": project_context,
            "existing_memories": memory_count,
            "suggestions": {
                "recommended_setup": _get_setup_suggestions(project_info),
                "common_categories": _get_common_categories(project_info)
            }
        }
    except Exception as e:
        logger.error(f"Error detecting project: {e}")
        return {"success": False, "error": str(e)}


async def suggest_related_memories(
    working_directory: Optional[str] = None,
    context: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Find related memories based on current project context."""
    try:
        project_info = detect_project_info(working_directory)
        
        async with get_db() as db:
            # Search for memories from the same project
            conditions = [Memory.project_name == project_info["name"]]
            
            # If context is provided, search for related content
            if context:
                search_pattern = f"%{context.lower()}%"
                conditions.append(
                    or_(
                        Memory.search_text.like(search_pattern),
                        Memory.content.ilike(search_pattern)
                    )
                )
            
            stmt = select(Memory).where(and_(*conditions)).order_by(
                desc(Memory.importance), desc(Memory.accessed_at)
            ).limit(10)
            
            result = await db.execute(stmt)
            project_memories = result.scalars().all()
            
            # Also search for similar technologies across projects
            tech_conditions = []
            if project_info["language"] != "unknown":
                tech_conditions.append(
                    Memory.search_text.like(f"%{project_info['language']}%")
                )
            if project_info["framework"] != "unknown":
                tech_conditions.append(
                    Memory.search_text.like(f"%{project_info['framework']}%")
                )
            
            if tech_conditions:
                stmt = select(Memory).where(
                    and_(
                        Memory.project_name != project_info["name"],
                        or_(*tech_conditions)
                    )
                ).order_by(desc(Memory.importance)).limit(5)
                
                result = await db.execute(stmt)
                cross_project_memories = result.scalars().all()
            else:
                cross_project_memories = []
            
            return {
                "success": True,
                "project_memories": [m.to_dict() for m in project_memories],
                "cross_project_memories": [m.to_dict() for m in cross_project_memories],
                "project_info": project_info,
                "suggestions": _get_context_suggestions(project_info, context)
            }
    except Exception as e:
        logger.error(f"Error suggesting related memories: {e}")
        return {"success": False, "error": str(e)}


def _get_setup_suggestions(project_info: Dict[str, str]) -> List[str]:
    """Get setup suggestions based on project type."""
    suggestions = []
    
    if project_info["type"] == "python":
        suggestions.extend([
            "Document virtual environment setup",
            "Store requirements.txt dependencies",
            "Remember development commands",
            "Document environment variables"
        ])
    elif project_info["type"] == "javascript":
        suggestions.extend([
            "Document npm/yarn commands",
            "Store build configuration",
            "Remember deployment process",
            "Document environment setup"
        ])
    elif project_info["type"] == "rust":
        suggestions.extend([
            "Document cargo commands",
            "Store build configuration",
            "Remember testing setup"
        ])
    
    return suggestions


def _get_common_categories(project_info: Dict[str, str]) -> List[str]:
    """Get common categories for project type."""
    base_categories = ["architecture", "setup", "bug_fix", "todo", "command"]
    
    if project_info["type"] in ["python", "javascript", "rust"]:
        base_categories.extend(["pattern", "testing", "deployment"])
    
    return base_categories


def _get_context_suggestions(project_info: Dict[str, str], context: Optional[str]) -> List[str]:
    """Get context-specific suggestions."""
    suggestions = []
    
    if context:
        context_lower = context.lower()
        
        if "auth" in context_lower:
            suggestions.extend([
                "Look for authentication patterns",
                "Check security implementations",
                "Review token handling"
            ])
        elif "database" in context_lower:
            suggestions.extend([
                "Review database schemas",
                "Check migration patterns",
                "Look for query optimizations"
            ])
        elif "api" in context_lower:
            suggestions.extend([
                "Review API patterns",
                "Check error handling",
                "Look for validation examples"
            ])
    
    return suggestions


async def summarize_project_memories(
    project: str,
    include_archived: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """Generate an intelligent summary of project memories."""
    try:
        async with get_db() as db:
            stmt = select(Memory).where(Memory.project_name == project)
            result = await db.execute(stmt)
            memories = result.scalars().all()
            
            if not memories:
                return {
                    "success": False,
                    "error": f"No memories found for project: {project}"
                }
            
            # Generate summary
            summary_text = summarizer.create_project_summary(memories, project)
            
            # Additional analytics
            total_memories = len(memories)
            categories = summarizer.group_memories_by_category(memories)
            avg_importance = sum(m.importance for m in memories) / total_memories
            
            # Recent activity
            recent_cutoff = datetime.utcnow() - timedelta(days=7)
            recent_memories = [m for m in memories if m.created_at > recent_cutoff]
            
            return {
                "success": True,
                "project": project,
                "summary": summary_text,
                "analytics": {
                    "total_memories": total_memories,
                    "categories": list(categories.keys()),
                    "average_importance": round(avg_importance, 1),
                    "recent_activity": len(recent_memories),
                    "oldest_memory": min(m.created_at for m in memories).isoformat(),
                    "newest_memory": max(m.created_at for m in memories).isoformat()
                }
            }
    except Exception as e:
        logger.error(f"Error summarizing project memories: {e}")
        return {"success": False, "error": str(e)}


async def analyze_memory_storage(project: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Analyze memory storage and suggest optimizations."""
    try:
        async with get_db() as db:
            if project:
                stmt = select(Memory).where(Memory.project_name == project)
            else:
                stmt = select(Memory)
            
            result = await db.execute(stmt)
            memories = result.scalars().all()
            
            if not memories:
                return {
                    "success": True,
                    "analysis": "No memories found to analyze"
                }
            
            # Run optimization analysis
            optimization_results = summarizer.optimize_memory_storage(memories)
            
            # Add database-specific stats
            async_query = select(func.count(Memory.id)).group_by(Memory.project_name)
            result = await db.execute(async_query)
            project_counts = result.all()
            
            return {
                "success": True,
                "scope": f"project: {project}" if project else "all projects",
                "optimization": optimization_results,
                "database_stats": {
                    "total_projects": len(project_counts) if project_counts else 0,
                    "analyzed_memories": len(memories)
                }
            }
    except Exception as e:
        logger.error(f"Error analyzing memory storage: {e}")
        return {"success": False, "error": str(e)}


async def suggest_memory_archival(
    project: Optional[str] = None,
    days_threshold: int = 90,
    **kwargs
) -> Dict[str, Any]:
    """Suggest memories for archival or cleanup."""
    try:
        async with get_db() as db:
            if project:
                stmt = select(Memory).where(Memory.project_name == project)
            else:
                stmt = select(Memory)
            
            result = await db.execute(stmt)
            memories = result.scalars().all()
            
            if not memories:
                return {
                    "success": True,
                    "suggestions": "No memories found to analyze"
                }
            
            # Get archival candidates
            candidates = summarizer.suggest_archival_candidates(memories)
            
            # Group by reason
            reasons_map = {}
            for memory, reason in candidates:
                if reason not in reasons_map:
                    reasons_map[reason] = []
                reasons_map[reason].append({
                    "id": memory.id,
                    "content": memory.content[:80] + "..." if len(memory.content) > 80 else memory.content,
                    "created_at": memory.created_at.isoformat(),
                    "importance": memory.importance,
                    "access_count": memory.access_count,
                    "category": memory.category
                })
            
            return {
                "success": True,
                "scope": f"project: {project}" if project else "all projects",
                "total_candidates": len(candidates),
                "archival_suggestions": reasons_map,
                "summary": f"Found {len(candidates)} memories that could be archived out of {len(memories)} total"
            }
    except Exception as e:
        logger.error(f"Error suggesting memory archival: {e}")
        return {"success": False, "error": str(e)}


async def archive_memories(
    memory_ids: List[int],
    reason: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """Archive one or more memories."""
    try:
        async with get_db() as db:
            archived_count = 0
            archived_memories = []
            
            for memory_id in memory_ids:
                stmt = select(Memory).where(Memory.id == memory_id)
                result = await db.execute(stmt)
                memory = result.scalar_one_or_none()
                
                if memory:
                    memory.is_archived = 1
                    memory.archived_at = datetime.utcnow()
                    memory.archived_reason = reason or "Manual archival"
                    archived_count += 1
                    archived_memories.append({
                        "id": memory.id,
                        "content": memory.content[:50] + "..." if len(memory.content) > 50 else memory.content,
                        "project": memory.project_name
                    })
            
            await db.commit()
            
            return {
                "success": True,
                "archived_count": archived_count,
                "archived_memories": archived_memories,
                "reason": reason or "Manual archival"
            }
    except Exception as e:
        logger.error(f"Error archiving memories: {e}")
        return {"success": False, "error": str(e)}


async def unarchive_memories(memory_ids: List[int], **kwargs) -> Dict[str, Any]:
    """Unarchive one or more memories."""
    try:
        async with get_db() as db:
            unarchived_count = 0
            unarchived_memories = []
            
            for memory_id in memory_ids:
                stmt = select(Memory).where(Memory.id == memory_id)
                result = await db.execute(stmt)
                memory = result.scalar_one_or_none()
                
                if memory and memory.is_archived:
                    memory.is_archived = 0
                    memory.archived_at = None
                    memory.archived_reason = None
                    unarchived_count += 1
                    unarchived_memories.append({
                        "id": memory.id,
                        "content": memory.content[:50] + "..." if len(memory.content) > 50 else memory.content,
                        "project": memory.project_name
                    })
            
            await db.commit()
            
            return {
                "success": True,
                "unarchived_count": unarchived_count,
                "unarchived_memories": unarchived_memories
            }
    except Exception as e:
        logger.error(f"Error unarchiving memories: {e}")
        return {"success": False, "error": str(e)}


async def cleanup_memories(
    project: Optional[str] = None,
    days_old: int = 180,
    max_importance: int = 3,
    dry_run: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """Automatically clean up old, unused memories."""
    try:
        async with get_db() as db:
            # Build query for cleanup candidates
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)
            
            conditions = [
                Memory.is_archived == 0,  # Only active memories
                Memory.created_at < cutoff_date,
                Memory.importance <= max_importance
            ]
            
            if project:
                conditions.append(Memory.project_name == project)
            
            stmt = select(Memory).where(and_(*conditions))
            result = await db.execute(stmt)
            candidates = result.scalars().all()
            
            # Further filter by usage patterns
            cleanup_candidates = []
            for memory in candidates:
                should_cleanup = False
                
                # Never accessed and old
                if memory.access_count == 0:
                    should_cleanup = True
                
                # Very low access rate
                days_since_creation = (datetime.utcnow() - memory.created_at).days
                if days_since_creation > 0:
                    access_rate = memory.access_count / days_since_creation
                    if access_rate < 0.01:  # Less than 1 access per 100 days
                        should_cleanup = True
                
                # Old TODO items
                if memory.category == "todo" and days_since_creation > 365:
                    should_cleanup = True
                
                if should_cleanup:
                    cleanup_candidates.append(memory)
            
            if not dry_run and cleanup_candidates:
                # Actually archive the memories
                for memory in cleanup_candidates:
                    memory.is_archived = 1
                    memory.archived_at = datetime.utcnow()
                    memory.archived_reason = f"Automatic cleanup: {days_old}+ days old, importance <= {max_importance}"
                
                await db.commit()
            
            # Prepare summary
            cleanup_summary = []
            for memory in cleanup_candidates:
                cleanup_summary.append({
                    "id": memory.id,
                    "content": memory.content[:60] + "..." if len(memory.content) > 60 else memory.content,
                    "project": memory.project_name,
                    "category": memory.category,
                    "importance": memory.importance,
                    "access_count": memory.access_count,
                    "age_days": (datetime.utcnow() - memory.created_at).days
                })
            
            return {
                "success": True,
                "dry_run": dry_run,
                "criteria": {
                    "days_old": days_old,
                    "max_importance": max_importance,
                    "project": project or "all projects"
                },
                "total_candidates": len(cleanup_candidates),
                "cleanup_performed": not dry_run,
                "memories": cleanup_summary
            }
    except Exception as e:
        logger.error(f"Error cleaning up memories: {e}")
        return {"success": False, "error": str(e)}


async def main():
    """Run the MCP server."""
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Run the server
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Memory-Man MCP server starting...")
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())