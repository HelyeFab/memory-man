# Memory-Man Integration Guide

This guide shows you how to integrate Memory-Man with Claude Code for maximum effectiveness.

## Step 1: Configure Claude Code

### Option A: Global Configuration (Recommended)

Create or edit `~/.claude/mcp_servers.json`:

```json
{
  "mcpServers": {
    "memory-man": {
      "command": "python",
      "args": ["-m", "memory_man"],
      "env": {
        "PYTHONPATH": "/home/beano/DevProjects/python/memory-man/src",
        "MEMORY_MAN_DATABASE_URL": "sqlite+aiosqlite:///~/.claude/memory_man.db"
      }
    }
  }
}
```

### Option B: Project-Specific Configuration

Add `mcp_config.json` to individual projects:

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

## Step 2: Restart Claude Code

After configuration, restart Claude Code to load the MCP server.

## Step 3: Verify Integration

Test that Memory-Man is working:

```bash
# In any project directory
claude-code
> Tell me about the available MCP tools

# You should see memory_store, memory_search, etc.
```

## Step 4: Start Using Memory-Man

### Best Practices

1. **Store Key Decisions Early**
   
   ```
   Store this architecture decision: "We're using FastAPI with SQLAlchemy for the backend API"
   ```

2. **Use Descriptive Categories**
   
   - `architecture` - System design decisions
   - `setup` - Configuration and environment
   - `bug_fix` - Solutions to problems
   - `pattern` - Reusable code patterns
   - `command` - Useful commands
   - `todo` - Future work

3. **Tag Appropriately**
   
   ```
   Store this with tags: authentication, JWT, security, middleware
   ```

4. **Set Importance Levels**
   
   - 1-3: Minor details
   - 4-6: Standard information
   - 7-8: Important decisions
   - 9-10: Critical architecture

## Step 5: Workflow Examples

### Starting a New Project

```bash
# Tell Claude about your project setup
"Store that this project uses Next.js 14 with TypeScript and Tailwind CSS"

# Store your development commands
"Remember that we run 'npm run dev' to start the development server"

# Document your architecture decisions
"Store that we're using Zustand for state management instead of Redux"
```

### Returning to an Existing Project

```bash
# Get project overview
"What do you remember about the my-web-app project?"

# Search for specific information
"Search for authentication-related memories in this project"

# Get recent context
"Show me the most recent memories for this project"
```

### Debugging Sessions

```bash
# Store the solution when you fix a bug
"Store this bug fix: CORS issues were resolved by adding specific origins to the FastAPI CORS middleware"

# Search for similar issues later
"Search for CORS-related solutions across all projects"
```

## Step 6: Advanced Usage

### Cross-Project Learning

```bash
# Find patterns across projects
"Search for authentication patterns across all my projects"

# Compare implementations
"How have I implemented user authentication in different projects?"
```

### Memory Management

```bash
# Update outdated information
"Update the authentication memory - we switched from JWT to session cookies"

# Clean up old memories
"Delete memories older than 6 months for completed projects"
```

## Troubleshooting

### Common Issues

1. **MCP Server Not Found**
   
   - Check `PYTHONPATH` in configuration
   - Verify memory-man is installed in the virtual environment
   - Check file permissions

2. **Database Issues**
   
   - Ensure data directory exists and is writable
   - Check database file permissions
   - Try deleting and recreating the database

3. **Search Not Working**
   
   - Check if memories exist for the project
   - Verify project names match exactly
   - Try broader search terms

### Debug Commands

```bash
# Test the server directly
python test_server.py

# Check database contents
sqlite3 data/memories.db ".tables"
sqlite3 data/memories.db "SELECT * FROM memories LIMIT 5;"

# View server logs
MEMORY_MAN_LOG_LEVEL=DEBUG python -m memory_man
```

## Tips for Maximum Effectiveness

1. **Be Consistent with Project Names**
   
   - Use the same project name across sessions
   - Consider using the directory name automatically

2. **Use Hierarchical Categories**
   
   - `architecture/database` vs `architecture/frontend`
   - `setup/development` vs `setup/production`

3. **Regular Memory Maintenance**
   
   - Update memories when things change
   - Archive completed projects
   - Clean up test/temporary memories

4. **Leverage Search Effectively**
   
   - Use multiple search terms
   - Search by tags and categories
   - Use importance levels to filter

## Future Enhancements

Consider these improvements:

1. **Automatic Project Detection**
   
   - Use git repository name as project name
   - Detect project type from files

2. **Semantic Search**
   
   - Use embeddings for better search
   - Find related memories automatically

3. **Memory Summarization**
   
   - Automatically summarize old memories
   - Create project documentation from memories

4. **Integration Features**
   
   - Export memories to markdown
   - Sync memories across machines
   - Share memories with team members