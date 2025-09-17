# Memory-Man 🧠

A persistent memory system for Claude Code that solves the context window problem by storing and retrieving project knowledge across sessions.

## What is Memory-Man?

Memory-Man is an MCP (Model Context Protocol) server that acts as Claude's long-term memory. Instead of losing context when the conversation window fills up, Claude can now:

- **Store** important information about your projects
- **Search** through past conversations and decisions
- **Retrieve** relevant context when working on similar problems
- **Track** patterns across multiple projects

## Features

- 🗂️ **Project-Aware Storage** - Memories are organized by project
- 🔍 **Smart Search** - Find relevant memories by content, tags, or category
- 📊 **Usage Analytics** - Track which memories are most valuable
- 🏷️ **Intelligent Tagging** - Categorize memories for easy retrieval
- ⚡ **Fast SQLite Backend** - Efficient local storage
- 🔧 **Easy Integration** - Works with Claude Code out of the box

## Quick Start

1. **Install Dependencies**:
   ```bash
   source venv/bin/activate
   pip install -r requirements-core.txt
   ```

2. **Test the Server**:
   ```bash
   python test_server.py
   ```

3. **Configure Claude Code** (see Integration Guide below)

## Memory Categories

- **architecture** - System design decisions and patterns
- **setup** - Project configuration and environment
- **bug_fix** - Solutions to bugs and issues
- **todo** - Future work and planned features
- **pattern** - Reusable code patterns and best practices
- **command** - Useful commands and scripts

## Integration with Claude Code

### Method 1: Global MCP Configuration

Add to your global Claude Code config (`~/.claude/mcp_servers.json`):

```json
{
  "mcpServers": {
    "memory-man": {
      "command": "python",
      "args": ["-m", "memory_man"],
      "env": {
        "PYTHONPATH": "/home/beano/DevProjects/python/memory-man/src"
      }
    }
  }
}
```

### Method 2: Project-Specific Configuration

Add `mcp_config.json` to any project:

```json
{
  "mcpServers": {
    "memory-man": {
      "command": "python",
      "args": ["-m", "memory_man"],
      "env": {
        "PYTHONPATH": "/home/beano/DevProjects/python/memory-man/src"
      }
    }
  }
}
```

## Usage Examples

### 🚀 Smart Auto-Store (Recommended)

```python
# Just provide the content - everything else is auto-detected!
memory_auto_store(
    content="We use JWT tokens with Redis for session management. Tokens expire after 24 hours."
)

# Auto-detects:
# - Project: current directory name
# - Category: architecture (based on content)  
# - Tags: ["jwt", "redis", "auth", "database"]
# - Framework: detected from project files
```

### 🔍 Smart Project Detection

```python
# Analyze your current project
project_detect()

# Returns project info + suggestions:
# - Technology stack (Python, JavaScript, etc.)
# - Framework (Django, React, FastAPI, etc.) 
# - Recommended memory categories
# - Setup suggestions
```

### 🧠 Context-Aware Suggestions

```python
# Get relevant memories for current work
memory_suggest_related(context="authentication setup")

# Returns:
# - Related memories from current project
# - Similar patterns from other projects
# - Smart suggestions based on context
```

### 📝 Manual Storage (When You Need Control)

```python
# Store architecture decision manually
memory_store(
    content="We use Redis for session storage with 24-hour TTL",
    category="architecture", 
    project="my-web-app",
    tags=["redis", "sessions", "auth"],
    importance=8
)

# Search memories
memory_search(query="authentication", project="my-web-app")

# Get project overview
project_summary(project="my-web-app")
```

## Available Tools

### Core Tools
| Tool | Description |
|------|-------------|
| `memory_store` | Store new memories with project context |
| `memory_search` | Search memories by query, project, or category |
| `memory_retrieve` | Get a specific memory by ID |
| `memory_update` | Update existing memories |
| `memory_delete` | Delete memories |
| `project_summary` | Get summary of a project's memories |
| `memory_list_projects` | List all projects with memories |

### Smart Tools ✨
| Tool | Description |
|------|-------------|
| `memory_auto_store` | **Auto-detect project, category, and tags** |
| `project_detect` | **Analyze current project and get suggestions** |
| `memory_suggest_related` | **Find relevant memories for current context** |

### Advanced Tools 🔧
| Tool | Description |
|------|-------------|
| `memory_summarize_project` | **Generate intelligent project summaries** |
| `memory_analyze_storage` | **Analyze and optimize memory usage** |
| `memory_suggest_archival` | **Find memories ready for archival** |
| `memory_archive` | **Archive memories manually** |
| `memory_unarchive` | **Restore archived memories** |
| `memory_cleanup` | **Automatic memory lifecycle management** |

## Configuration

Environment variables (optional):

```bash
# Database location
MEMORY_MAN_DATABASE_URL=sqlite+aiosqlite:///./data/memories.db

# Storage directory
MEMORY_MAN_DATA_DIR=./data

# Search settings
MEMORY_MAN_SEARCH_LIMIT=20
MEMORY_MAN_MAX_MEMORY_SIZE=10000

# Logging
MEMORY_MAN_LOG_LEVEL=INFO
MEMORY_MAN_DEBUG=false
```

## Development

### Running Tests
```bash
python test_server.py
```

### Code Quality
```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

### Adding New Features

1. **Models**: Add to `src/memory_man/models/`
2. **Tools**: Add to `src/memory_man/server.py`
3. **Config**: Update `src/memory_man/config.py`

## Troubleshooting

### Server Won't Start
- Check Python path in MCP configuration
- Ensure virtual environment is properly set up
- Verify all dependencies are installed

### Memory Search Issues
- Check if database exists in `data/memories.db`
- Verify project names match exactly
- Try broader search terms

### Performance Issues
- Database will be created automatically on first run
- Consider adding indexes for large datasets
- Use importance levels to prioritize memories

## Contributing

This is designed as a personal tool for your Claude Code workflow. Feel free to modify:

- Add new memory categories
- Implement semantic search
- Add memory expiration
- Create backup/sync features

## License

MIT License - Feel free to use and modify as needed.