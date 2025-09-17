# Lessons Learned: MCP Server Integration with Claude Code

## Executive Summary
This document captures the complete journey of debugging and fixing the memory-man MCP server integration with Claude Code. What initially appeared as a simple connection issue revealed multiple layers of complexity involving Python environments, MCP protocol implementation, configuration scopes, and library version compatibility.

## Timeline of Issues and Resolutions

### Phase 1: Initial Connection Failures
**Problem**: MCP server showing "Failed to connect" despite correct configuration

**Root Causes Discovered**:
1. **Python Environment Mismatch**: System Python vs Virtual Environment
   - The MCP config was using `python` or `python3` (system Python)
   - The `mcp` module was only installed in the virtual environment
   - **Solution**: Use full path to venv Python: `/home/beano/DevProjects/python/MCP_SERVERS/memory-man/venv/bin/python`

2. **Logging to stdout Interference**
   - Server logs were being written to stdout, corrupting JSON-RPC communication
   - MCP protocol requires clean JSON-RPC on stdout
   - **Solution**: Redirect all logging to stderr:
   ```python
   logging.basicConfig(
       level=settings.log_level,
       stream=sys.stderr,
       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   ```

### Phase 2: Configuration Scope Confusion
**Problem**: Multiple overlapping configurations causing inconsistent behavior

**Configuration Hierarchy Discovered**:
1. **Project-level** (`.mcp.json` in project root) - Highest priority
2. **Project-specific in .claude directory** (`project/.claude/mcp.json`)
3. **Project entry in global config** (`~/.claude.json` under projects key)
4. **User-level global** (`~/.claude/mcp_servers.json` or mcpServers in `~/.claude.json`)

**Key Findings**:
- Claude Code checks configurations in order of specificity
- Project configs override global configs
- The `.claude.json` file can grow to 60+ MB due to conversation history with embedded images
- Configuration display in `claude mcp list` can be misleading (showed wrong args)

**Solution**:
- Remove conflicting project-level configs
- Establish single source of truth at user level
- Clean up bloated `.claude.json` by removing history

### Phase 3: Missing PYTHONPATH Environment Variable
**Problem**: Server failed to import modules even with correct Python interpreter

**Root Cause**:
- The PYTHONPATH environment variable was missing or empty in some configurations
- Different config locations had inconsistent environment settings

**Solution**:
```json
"env": {
    "PYTHONPATH": "/home/beano/DevProjects/python/MCP_SERVERS/memory-man/src"
}
```

### Phase 4: MCP Library Version Incompatibility
**Problem**: Server showed as "Connected" but tools weren't available to Claude

**Investigation Results**:
1. Initial version: MCP 1.1.2 (what the server was written for)
2. Attempted upgrade to MCP 1.13.1 introduced breaking changes
3. The `tools/list` method returned errors about "initialization not complete"

**Key Discovery**: Version 1.13.1 changed the initialization flow and validation requirements

### Phase 5: Field Name Mismatch (Snake Case vs Camel Case)
**Problem**: Tool definitions failing validation

**Root Cause**:
- Code used `input_schema` (snake_case)
- MCP library expects `inputSchema` (camelCase)
- This is a Pydantic validation requirement

**Solution**:
```python
# Wrong
Tool(name="test", input_schema={...})

# Correct  
Tool(name="test", inputSchema={...})
```

### Phase 6: MCP Protocol Implementation Issues
**Problem**: Even after all fixes, tools still weren't exposed to Claude

**Root Cause Analysis**:
- The MCP library's decorators (`@app.list_tools()`) weren't properly handling the protocol
- The server would initialize successfully but fail to respond to `tools/list` requests
- The library's internal message handling wasn't working as expected

**Solution**: Created a protocol wrapper that manually handles JSON-RPC messages

## The Final Solution: Protocol Wrapper

### Why the Wrapper Was Necessary
1. The MCP library's automatic protocol handling was failing silently
2. The decorators weren't properly registering or exposing tools
3. Direct protocol implementation gave us full control over the message flow

### Wrapper Implementation Key Points
```python
# Key aspects of the wrapper solution:

1. Direct JSON-RPC message handling
2. Manual initialization response
3. Explicit tools/list implementation
4. Proper async handling
5. Clean separation of concerns
```

## Critical Success Factors

### 1. Proper Testing Methodology
- Test each component in isolation
- Use direct protocol testing before integration
- Verify responses with actual JSON parsing
- Check stderr for hidden error messages

### 2. Configuration Management
- Use absolute paths everywhere
- Maintain single source of truth for configs
- Understand configuration precedence
- Document which config is active and why

### 3. Environment Consistency
- Always use virtual environment Python
- Explicitly set PYTHONPATH
- Ensure all dependencies are in venv
- Test from different working directories

### 4. Protocol Compliance
- MCP requires strict JSON-RPC 2.0 compliance
- stdout must be reserved for protocol only
- All logging must go to stderr
- Responses must match expected schema exactly

## Common Pitfalls to Avoid

### 1. Don't Assume Connection Means Working
- "✓ Connected" only means the server responded to initialization
- Tools availability is a separate concern
- Always verify tools are actually accessible

### 2. Don't Mix Configuration Scopes
- Project configs override global configs unexpectedly
- Hidden configs in `.claude/` directories cause confusion
- The display in `claude mcp list` may not show actual command

### 3. Don't Trust Library Abstractions Blindly
- High-level decorators can hide protocol issues
- When in doubt, implement the protocol directly
- Test the actual JSON-RPC messages being exchanged

### 4. Don't Ignore Version Compatibility
- MCP library versions have breaking changes
- Upgrading isn't always the solution
- Match the version the code was written for

## Best Practices for MCP Server Development

### 1. Development Setup
```bash
# Always use virtual environment
python3 -m venv venv
source venv/bin/activate
pip install mcp==<specific_version>
```

### 2. Testing Strategy
```python
# Test protocol directly
echo '{"jsonrpc": "2.0", "method": "initialize", ...}' | python server.py

# Test tools listing
echo '{"jsonrpc": "2.0", "method": "tools/list", ...}' | python server.py

# Verify JSON responses
... | jq '.result.tools | length'
```

### 3. Configuration Template
```json
{
  "mcpServers": {
    "server-name": {
      "type": "stdio",
      "command": "/absolute/path/to/venv/bin/python",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "PYTHONPATH": "/absolute/path/to/src"
      }
    }
  }
}
```

### 4. Debugging Checklist
- [ ] Is the server using the correct Python interpreter?
- [ ] Is PYTHONPATH set correctly?
- [ ] Are logs going to stderr only?
- [ ] Does initialization return successfully?
- [ ] Does tools/list return the expected tools?
- [ ] Are field names in correct case (camelCase vs snake_case)?
- [ ] Is there a conflicting project-level config?
- [ ] Has Claude Code been restarted after config changes?

## Implementation Artifacts

### Files Created/Modified
1. `/home/beano/DevProjects/python/MCP_SERVERS/memory-man/src/memory_man/server.py`
   - Fixed logging to stderr
   - Changed `input_schema` to `inputSchema`

2. `/home/beano/DevProjects/python/MCP_SERVERS/memory-man/src/memory_man/server_wrapper.py`
   - Created new protocol wrapper
   - Implements direct JSON-RPC handling
   - Properly exposes all 16 tools

3. `~/.claude.json`
   - Cleaned 66MB down to 34KB by removing history
   - Fixed project-specific MCP configurations

4. Various `.mcp.json` and `.claude/mcp.json` files
   - Removed or fixed conflicting configurations

### Final Working Configuration
```json
{
  "type": "stdio",
  "command": "/home/beano/DevProjects/python/MCP_SERVERS/memory-man/venv/bin/python",
  "args": ["/home/beano/DevProjects/python/MCP_SERVERS/memory-man/src/memory_man/server_wrapper.py"],
  "env": {
    "PYTHONPATH": "/home/beano/DevProjects/python/MCP_SERVERS/memory-man/src"
  }
}
```

## Metrics
- **Total debugging time**: ~2 hours
- **Configuration attempts**: 15+
- **Files modified**: 7
- **Root causes identified**: 6
- **Final solution components**: 3 (wrapper + config + field fix)
- **Tools successfully exposed**: 16

## Future Recommendations

### For MCP Server Developers
1. Start with a minimal protocol implementation
2. Test JSON-RPC messages directly before using libraries
3. Maintain compatibility with specific MCP versions
4. Document all configuration requirements explicitly
5. Provide diagnostic scripts for troubleshooting

### For Claude Code Users
1. Understand the configuration hierarchy
2. Use global (user-level) configs when possible
3. Regularly clean `.claude.json` to prevent bloat
4. Always restart Claude after configuration changes
5. Verify tool availability, not just connection status

### For the Memory-Man Project
1. Pin the MCP library version in requirements
2. Include the wrapper as the primary entry point
3. Add diagnostic mode for troubleshooting
4. Document the exact configuration needed
5. Consider implementing a setup script

## Conclusion

What started as a simple "Failed to connect" error revealed a complex interplay of:
- Python environment management
- Configuration scope precedence  
- Protocol implementation details
- Library version compatibility
- Field naming conventions

The key lesson is that MCP integration requires attention to every layer of the stack. When high-level abstractions fail, understanding and implementing the underlying protocol directly can be the most reliable solution.

The creation of a protocol wrapper, while seemingly redundant given the MCP library's decorators, proved to be the critical piece that made everything work. Sometimes, the best abstraction is no abstraction.

## Appendix: Quick Troubleshooting Guide

### Symptom: "Failed to connect"
1. Check Python path uses venv
2. Verify PYTHONPATH is set
3. Ensure mcp module is installed in venv

### Symptom: "Connected" but no tools available
1. Check field names (inputSchema not input_schema)
2. Verify tools/list returns tools
3. Consider using protocol wrapper
4. Restart Claude Code

### Symptom: Works in one project but not another
1. Check for project-level configs
2. Look for `.claude/mcp.json`
3. Check project entry in `~/.claude.json`
4. Use global config instead

### Symptom: Inconsistent behavior
1. Remove all project configs
2. Use only user-level configuration
3. Restart Claude Code completely
4. Test with `claude mcp list` from home directory

---

*Document created: 2025-09-11*
*Based on: memory-man MCP server debugging session*
*Environment: Ubuntu Linux, Claude Code, Python 3.13*