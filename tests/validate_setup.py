#!/usr/bin/env python3
"""
Simple validation script for Permit Assistant setup

This script validates the basic file structure and configuration without
requiring all dependencies to be installed.
"""

import os
import json
import sys

def validate_files():
    """Check if required files exist"""
    files_to_check = [
        "src/agents/permit_assistant.py",
        "src/mcp/opengov_plc_mcp_server.py", 
        "langgraph.json",
        "requirements.txt"
    ]
    
    missing_files = []
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required files exist")
        return True

def validate_langgraph_config():
    """Check if permit_assistant is in langgraph.json"""
    try:
        with open('langgraph.json', 'r') as f:
            config = json.load(f)
        
        graphs = config.get('graphs', {})
        
        if 'permit_assistant' in graphs:
            path = graphs['permit_assistant']
            print(f"✅ Permit assistant configured in langgraph.json")
            print(f"   Path: {path}")
            
            # Check if the path file exists
            # Convert path like "./src/agents/permit_assistant.py:graph" to file path
            file_path = path.split(':')[0].lstrip('./')
            if os.path.exists(file_path):
                print(f"✅ Agent file exists at {file_path}")
            else:
                print(f"❌ Agent file missing at {file_path}")
                return False
            return True
        else:
            print("❌ permit_assistant not found in langgraph.json")
            return False
            
    except Exception as e:
        print(f"❌ Failed to validate langgraph.json: {e}")
        return False

def validate_mcp_server():
    """Check if MCP server has the right structure"""
    try:
        with open('src/mcp/opengov_plc_mcp_server.py', 'r') as f:
            content = f.read()
        
        # Check for key components
        checks = [
            ("FastMCP import", "from mcp.server.fastmcp import FastMCP"),
            ("MCP server initialization", "mcp = FastMCP"),
            ("OpenGov client class", "class OpenGovPLCClient"),
            ("OAuth authentication", "get_access_token"),
            ("Tool decorators", "@mcp.tool()"),
            ("Main execution", 'if __name__ == "__main__"')
        ]
        
        all_checks_passed = True
        for check_name, check_string in checks:
            if check_string in content:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_checks_passed = False
        
        return all_checks_passed
        
    except Exception as e:
        print(f"❌ Failed to validate MCP server: {e}")
        return False

def validate_permit_assistant():
    """Check if permit assistant has the right structure"""
    try:
        with open('src/agents/permit_assistant.py', 'r') as f:
            content = f.read()
        
        # Check for key components
        checks = [
            ("LangGraph imports", "from langgraph.prebuilt import create_react_agent"),
            ("MCP adapter import", "from langchain_mcp_adapters.client import MultiServerMCPClient"),
            ("MCP tools function", "async def get_permit_tools"),
            ("Agent creation", "create_react_agent"),
            ("Graph export", "graph ="),
            ("Environment checks", "OG_PLC_CLIENT_ID")
        ]
        
        all_checks_passed = True
        for check_name, check_string in checks:
            if check_string in content:
                print(f"✅ {check_name}")
            else:
                print(f"❌ {check_name}")
                all_checks_passed = False
        
        return all_checks_passed
        
    except Exception as e:
        print(f"❌ Failed to validate permit assistant: {e}")
        return False

def validate_requirements():
    """Check if requirements.txt has necessary dependencies"""
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        # Check for key dependencies
        deps = [
            "langgraph",
            "langchain-mcp-adapters", 
            "mcp",
            "aiohttp"
        ]
        
        all_deps_found = True
        for dep in deps:
            if dep in requirements:
                print(f"✅ {dep} dependency")
            else:
                print(f"❌ {dep} dependency")
                all_deps_found = False
        
        return all_deps_found
        
    except Exception as e:
        print(f"❌ Failed to validate requirements: {e}")
        return False

def main():
    """Main validation function"""
    print("Permit Assistant Setup Validation")
    print("=" * 50)
    
    validations = [
        ("File Structure", validate_files),
        ("LangGraph Configuration", validate_langgraph_config),
        ("MCP Server Structure", validate_mcp_server),
        ("Permit Assistant Structure", validate_permit_assistant),
        ("Dependencies", validate_requirements)
    ]
    
    passed = 0
    total = len(validations)
    
    for name, validation_func in validations:
        print(f"\n{name}:")
        if validation_func():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 Setup validation successful!")
        print("\nYour permit assistant is properly configured.")
        print("\nNext steps:")
        print("1. Set environment variables (OG_PLC_CLIENT_ID, OG_PLC_SECRET, OPENAI_API_KEY)")
        print("2. Install dependencies: pip install -r requirements.txt")
        print("3. Start LangGraph: langgraph dev")
        print("4. Access via: http://localhost:3000/chat?assistantId=permit_assistant&apiUrl=http://localhost:8123")
    else:
        print("⚠️  Some validation checks failed.")
        print("Please review the errors above and fix any issues.")

if __name__ == "__main__":
    main() 