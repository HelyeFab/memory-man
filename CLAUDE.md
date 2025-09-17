# CLAUDE.md - Project Context for Claude

## Project Overview
**Project Name**: memory-man
**Type**: MCP (Model Context Protocol) Server
**Purpose**: Persistent memory system for Claude Code across multiple projects to overcome context window limitations

## Project Structure
```
/home/beano/DevProjects/python/memory-man/
├── CLAUDE.md (this file)
├── requirements.txt (full dependencies)
├── requirements-core.txt (minimal dependencies)
├── pyproject.toml (project config)
├── mcp_config.json (MCP server config)
├── test_server.py (test script)
├── src/
│   └── memory_man/
│       ├── __init__.py
│       ├── __main__.py
│       ├── config.py (settings)
│       ├── database.py (DB connection)
│       ├── server.py (MCP server)
│       └── models/
│           ├── __init__.py
│           └── memory.py (Memory model)
├── data/ (created automatically)
│   └── memories.db (SQLite database)
└── venv/ (Python virtual environment)
```

## Development Setup
- **Python Version**: 3.10+
- **Virtual Environment**: `source venv/bin/activate`
- **Dependencies**: 
  - Core: `pip install -r requirements-core.txt`
  - Full (with ML features): `pip install -r requirements.txt`

## Key Commands
- **Activate Environment**: `source venv/bin/activate`
- **Run Server**: `python -m memory_man`
- **Test Server**: `python test_server.py`
- **Lint Code**: `ruff check src/`
- **Format Code**: `black src/`
- **Type Check**: `mypy src/`

## MCP Tools Available

### Core Tools
1. **memory_store** - Store new memories with project context
2. **memory_search** - Search memories by query, project, or category
3. **memory_retrieve** - Get a specific memory by ID
4. **memory_update** - Update existing memories
5. **memory_delete** - Delete memories
6. **project_summary** - Get summary of a project's memories
7. **memory_list_projects** - List all projects with memories

### Smart Tools ✨ 
8. **memory_auto_store** - Auto-detect project, category, tags from content and directory
9. **project_detect** - Analyze current project and get setup suggestions
10. **memory_suggest_related** - Find relevant memories based on current context

### Advanced Tools 🔧
11. **memory_summarize_project** - Generate intelligent project summaries with analytics
12. **memory_analyze_storage** - Analyze memory usage and suggest optimizations
13. **memory_suggest_archival** - Find memories ready for archival based on age/usage
14. **memory_archive/unarchive** - Manual memory lifecycle management
15. **memory_cleanup** - Automatic cleanup with configurable criteria

## Memory Categories
- **architecture** - System design decisions
- **setup** - Project setup and configuration
- **bug_fix** - Solutions to bugs
- **todo** - Future work items
- **pattern** - Code patterns and best practices
- **command** - Useful commands and scripts

## Usage in Claude Code
### Smart Auto-Store (Recommended)
- Auto-Store: `memory_auto_store(content="We use JWT with Redis for auth")`
- Project Info: `project_detect()` 
- Context Help: `memory_suggest_related(context="setting up authentication")`

### Manual Controls
- Store: `memory_store(content="Auth uses JWT", category="architecture", project="my-app")`
- Search: `memory_search(query="authentication", project="my-app")`
- Summary: `project_summary(project="my-app")`

## Important Notes
- Database is stored in `data/memories.db` (SQLite)
- Memories are project-aware and tagged for easy retrieval
- Each memory tracks access patterns for smart retrieval
- Search includes content, tags, and categories

## COMPLETED FEATURES ✅
- [x] Basic MCP server structure with 15 tools
- [x] SQLite database with archival support
- [x] Core memory operations (store, search, retrieve, update, delete)
- [x] Smart project detection and auto-categorization
- [x] Context-aware memory suggestions and cross-project learning
- [x] Intelligent memory summarization with analytics
- [x] Complete memory lifecycle management (archive/cleanup)
- [x] Claude Code integration with global configuration
- [x] Comprehensive documentation and test suite

## FUTURE ENHANCEMENTS (Optional)
- [ ] Semantic search with embeddings for better matching
- [ ] Export/import functionality for team sharing
- [ ] Memory templates for common project patterns