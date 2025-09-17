#!/usr/bin/env python3
"""
Wrapper for memory-man server to properly handle MCP protocol.
This fixes the tools/list issue with the MCP library.
"""

import asyncio
import json
import sys
import logging
from typing import Any, Dict

# Configure logging to stderr only
logging.basicConfig(
    level=logging.WARNING,
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import the original server
from memory_man.server import app, init_db

async def run_server():
    """Run the wrapped MCP server."""
    # Initialize database
    await init_db()
    
    # Main message loop
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
                
            request = json.loads(line)
            method = request.get("method")
            request_id = request.get("id")
            
            if method == "initialize":
                # Handle initialization
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "memory-man",
                            "version": "1.1.2"
                        }
                    }
                }
                
            elif method == "tools/list":
                # Import the list_tools function directly
                from memory_man.server import list_tools
                
                # Get tools from the function
                tools_list = await list_tools()
                
                # Convert Tool objects to dictionaries
                tools_dict = []
                for tool in tools_list:
                    tool_dict = {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema  # Use correct field name
                    }
                    tools_dict.append(tool_dict)
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools_dict
                    }
                }
                
            elif method == "tools/call":
                # Handle tool calls
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                try:
                    # Call the tool through the app
                    result = await app.call_tool(tool_name, arguments)
                    
                    # Format the response
                    content = []
                    for item in result:
                        if hasattr(item, 'text'):
                            content.append({
                                "type": "text",
                                "text": item.text
                            })
                        else:
                            content.append({
                                "type": "text",
                                "text": str(item)
                            })
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": content
                        }
                    }
                except Exception as e:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": f"Tool execution failed: {str(e)}"
                        }
                    }
                    
            else:
                # Unknown method
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            # Send response
            print(json.dumps(response), flush=True)
            
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            if request_id:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)

if __name__ == "__main__":
    asyncio.run(run_server())