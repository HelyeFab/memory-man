# Memory-Man Usage Guide 🧠

Complete guide to using Memory-Man effectively with Claude Code.

## Quick Start

### 1. Basic Memory Operations

```bash
# Store a simple memory
memory_store(
    content="This project uses PostgreSQL with connection pooling",
    category="architecture",
    project="my-app",
    tags=["database", "postgres"],
    importance=7
)

# Search for memories
memory_search(query="database", project="my-app")

# Get project overview
project_summary(project="my-app")
```

### 2. Smart Auto-Store (Recommended)

```bash
# Auto-detect everything!
memory_auto_store(
    content="We use JWT tokens with Redis for session management"
)
# Automatically detects: project, category, tags, tech stack
```

## Advanced Features

### Project Detection

Memory-Man automatically detects your project type and suggests relevant categories:

```bash
# Analyze current project
project_detect()

# Returns:
# - Project name (from directory)
# - Technology stack (Python, JavaScript, Rust, etc.)
# - Framework (Django, React, FastAPI, etc.)
# - Setup suggestions
# - Recommended memory categories
```

### Smart Context Suggestions

```bash
# Get related memories for current context
memory_suggest_related(context="authentication setup")

# Returns:
# - Relevant memories from current project
# - Similar patterns from other projects
# - Context-specific suggestions
```

## Real-World Workflows

### Starting a New Project

```bash
# 1. Detect project info
project_detect()

# 2. Store initial architecture decisions
memory_auto_store(
    content="Using Next.js 14 with TypeScript, Tailwind CSS, and Supabase backend",
    importance=9
)

# 3. Document development setup
memory_auto_store(
    content="Run 'npm run dev' for development server. Environment variables in .env.local"
)
```

### Daily Development

```bash
# Store solutions as you work
memory_auto_store(
    content="Fixed CORS issue by adding specific origins to middleware config"
)

# Search when you need help
memory_search(query="CORS", project="my-app")

# Get suggestions for current task
memory_suggest_related(context="API error handling")
```

### Debugging Sessions

```bash
# Store the problem
memory_auto_store(
    content="Database connection timeout errors during high load",
    importance=8
)

# Store the solution
memory_auto_store(
    content="Fixed by increasing connection pool size to 20 and adding retry logic"
)

# Search for similar issues across projects
memory_search(query="connection timeout")
```

### Code Reviews & Architecture

```bash
# Document decisions
memory_auto_store(
    content="Chose Redis over Memcached for session storage due to data persistence needs",
    importance=8
)

# Store patterns
memory_auto_store(
    content="Error handling pattern: try/catch with custom error classes and structured logging"
)
```

## Best Practices

### 1. Use Importance Levels Effectively

- **1-3**: Temporary notes, minor details
- **4-6**: Standard information, common patterns
- **7-8**: Important decisions, key architecture
- **9-10**: Critical system design, major breakthroughs

### 2. Strategic Tagging

```bash
# Good tagging examples
tags=["authentication", "jwt", "security", "middleware"]
tags=["database", "postgres", "migration", "performance"]
tags=["deployment", "docker", "aws", "ci-cd"]
```

### 3. Descriptive Content

```bash
# ❌ Too vague
"Fixed the bug"

# ✅ Specific and useful
"Fixed React state update bug by moving setState to useEffect with proper dependency array"
```

### 4. Regular Maintenance

```bash
# Check your memory stats
python scripts/stats.py

# Backup important memories
python scripts/backup_memories.py

# Clean up old test memories
memory_search(query="test", limit=50)  # Review and delete
```

## Power User Tips

### 1. Cross-Project Learning

```bash
# Find authentication patterns across all projects
memory_search(query="authentication")

# Compare database choices
memory_search(query="database", category="architecture")
```

### 2. Team Knowledge Sharing

```bash
# Export project memories
python scripts/backup_memories.py

# Share the JSON file with team members
# They can import relevant memories
```

### 3. Project Templates

```bash
# Create template memories for new projects
memory_store(
    content="Standard Python project setup: poetry, black, pytest, pre-commit",
    category="setup",
    project="template-python",
    importance=8
)
```

### 4. Context-Aware Searching

```bash
# Use current directory for smart suggestions
memory_suggest_related(context="setting up CI/CD")

# Get project-specific help
project_summary(project="current-project")
```

## Troubleshooting

### Memory Not Found

```bash
# Check if project name matches
memory_list_projects()

# Search broadly
memory_search(query="partial content")
```

### Poor Search Results

```bash
# Use broader terms
memory_search(query="auth")  # instead of "authentication middleware"

# Search by category
memory_search(category="architecture")

# Check all projects
memory_search(query="database")  # searches across all projects
```

### Project Detection Issues

```bash
# Manual project detection
project_detect(working_directory="/path/to/project")

# Override auto-detection
memory_store(
    content="Manual memory",
    project="custom-project-name",
    category="setup"
)
```

## Integration Examples

### With Git Workflows

```bash
# Before major refactor
memory_auto_store(
    content="Starting authentication refactor: moving from sessions to JWT tokens"
)

# After completion
memory_auto_store(
    content="Completed auth refactor. JWT tokens in httpOnly cookies, refresh token rotation implemented"
)
```

### With Documentation

```bash
# Auto-generate project docs from memories
memory_search(category="architecture", project="my-app")
# Copy results to README or wiki
```

### With Code Reviews

```bash
# Store review feedback
memory_auto_store(
    content="Code review feedback: prefer explicit error handling over silent failures"
)

# Reference in future reviews
memory_search(query="code review", category="pattern")
```

## Advanced Configuration

### Environment Variables

```bash
# Custom database location
export MEMORY_MAN_DATABASE_URL="sqlite+aiosqlite:///path/to/memories.db"

# Increase search results
export MEMORY_MAN_SEARCH_LIMIT=50

# Debug mode
export MEMORY_MAN_DEBUG=true
export MEMORY_MAN_LOG_LEVEL=DEBUG
```

### Project-Specific Configs

Create `.memory-man.json` in project root:

```json
{
  "project_name": "custom-name",
  "default_importance": 6,
  "auto_tags": ["project-specific", "custom"],
  "categories": ["architecture", "setup", "custom-category"]
}
```

## Next Steps

1. **Start Small**: Begin with storing architecture decisions and commands
2. **Build Habits**: Auto-store solutions as you work
3. **Review Regularly**: Use `memory_suggest_related()` when starting new tasks
4. **Maintain**: Clean up old memories, backup important ones
5. **Share**: Export useful memories to share with team

Memory-Man becomes more valuable as you use it. Start storing memories today and watch your development efficiency improve!