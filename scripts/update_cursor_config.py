#!/usr/bin/env python3
# Generated-by: Cursor (claude-4-sonnet)
"""
Update Cursor IDE configuration for MCP server integration.

This script automatically configures Cursor to use your MCP server.
Based on the pattern from mcp-location-server.
"""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict


def find_cursor_config_path() -> Path:
    """Find the Cursor configuration directory."""
    home = Path.home()
    
    # Common Cursor config locations
    possible_paths = [
        home / ".cursor" / "mcp.json",  # Linux/macOS
        home / "Library" / "Application Support" / "Cursor" / "User" / "mcp_settings.json",  # macOS
        home / "AppData" / "Roaming" / "Cursor" / "User" / "mcp_settings.json",  # Windows
    ]
    
    for path in possible_paths:
        if path.parent.exists():
            return path
    
    # Default to the first option if none exist
    return possible_paths[0]


def update_cursor_config(python_path: str, project_path: str) -> None:
    """Update Cursor MCP configuration."""
    config_path = find_cursor_config_path()
    
    # Ensure the directory exists
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing config or create new one
    config: Dict[str, Any] = {}
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
        except (json.JSONDecodeError, IOError):
            print(f"Warning: Could not read existing config at {config_path}")
            config = {}
    
    # Ensure mcpServers section exists
    if "mcpServers" not in config:
        config["mcpServers"] = {}
    
    # Add or update the server configuration
    server_name = "template-python"
    config["mcpServers"][server_name] = {
        "command": python_path,
        "args": ["-m", "template_python.mcp_server"],
        "env": {
            "PYTHONPATH": project_path
        }
    }
    
    # Write the updated configuration
    try:
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Updated Cursor configuration at {config_path}")
        print(f"📍 Added MCP server: {server_name}")
    except IOError as e:
        print(f"❌ Failed to write configuration: {e}")
        sys.exit(1)


def main() -> None:
    """Main function."""
    if len(sys.argv) != 3:
        print("Usage: python update_cursor_config.py <python_path> <project_path>")
        print("Example: python update_cursor_config.py /path/to/venv/bin/python /path/to/project")
        sys.exit(1)
    
    python_path = sys.argv[1]
    project_path = sys.argv[2]
    
    # Validate inputs
    if not os.path.exists(python_path):
        print(f"❌ Python path does not exist: {python_path}")
        sys.exit(1)
    
    if not os.path.exists(project_path):
        print(f"❌ Project path does not exist: {project_path}")
        sys.exit(1)
    
    print(f"🔧 Configuring Cursor MCP integration...")
    print(f"   Python: {python_path}")
    print(f"   Project: {project_path}")
    
    update_cursor_config(python_path, project_path)


if __name__ == "__main__":
    main()