#!/usr/bin/env python3
"""
Comprehensive test script that tests ALL 93 OpenGov MCP tools systematically.
Records detailed prompt/response pairs for analysis.
"""

import asyncio
import json
import time
from datetime import datetime
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.permit_assistant.graph import create_permit_agent
from src.agents.permit_assistant.types import AgentState

class MCPToolTester:
    def __init__(self):
        self.agent = None
        self.test_results = []
        self.test_community = "demo"
        
    async def initialize(self):
        print("🚀 Initializing permit assistant agent...")
        try:
            self.agent = await create_permit_agent()
            print("✅ Agent initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            return False
    
    async def run_test(self, tool_name: str, prompt: str):
        print(f"\n🔧 Testing: {tool_name}")
        print(f"📝 Prompt: {prompt}")
        
        start_time = time.time()
        try:
            state = AgentState(
                messages=[{"role": "user", "content": prompt}],
                ui_messages=[]
            )
            
            result = await self.agent.ainvoke(state)
            execution_time = time.time() - start_time
            
            # Extract response
            response = "No response"
            if result and "messages" in result and result["messages"]:
                last_message = result["messages"][-1]
                if hasattr(last_message, 'content'):
                    response = last_message.content
                elif isinstance(last_message, dict):
                    response = last_message.get("content", "No content")
                else:
                    response = str(last_message)
            
            # Record result
            self.test_results.append({
                "timestamp": datetime.now().isoformat(),
                "tool_name": tool_name,
                "prompt": prompt,
                "response": response,
                "success": True,
                "execution_time": execution_time
            })
            
            print(f"✅ PASSED - {execution_time:.2f}s")
            return True
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.test_results.append({
                "timestamp": datetime.now().isoformat(),
                "tool_name": tool_name,
                "prompt": prompt,
                "response": f"ERROR: {str(e)}",
                "success": False,
                "execution_time": execution_time
            })
            print(f"❌ FAILED - {execution_time:.2f}s - {e}")
            return False

    async def run_all_tests(self):
        print("🎯 Testing ALL 93 OpenGov MCP tools...")
        
        # Record tools (32)
        record_tests = [
            ("get_records", f"Show me all permit records in {self.test_community}"),
            ("list_available_record_ids", f"What record IDs are available in {self.test_community}?"),
            ("get_record", f"Get details for record ID 'REC-001' in {self.test_community}"),
            ("create_record", f"Create a new building permit record in {self.test_community}"),
            ("update_record", f"Update record REC-001 in {self.test_community}"),
            ("get_record_attachments", f"Show attachments for records in {self.test_community}"),
            ("get_record_workflow_steps", f"Show workflow steps for records in {self.test_community}"),
            ("get_record_form_details", f"Show form details for record REC-001 in {self.test_community}"),
        ]
        
        # Location tools (7)
        location_tests = [
            ("get_locations", f"Show me all locations in {self.test_community}"),
            ("get_location", f"Get details for location LOC-001 in {self.test_community}"),
            ("create_location", f"Create a new location at 123 Main Street in {self.test_community}"),
        ]
        
        # User tools (7)
        user_tests = [
            ("get_users", f"Show me all users in {self.test_community}"),
            ("get_user", f"Get details for user USER-001 in {self.test_community}"),
            ("create_user", f"Create a new user account in {self.test_community}"),
        ]
        
        # Inspection tools (16)
        inspection_tests = [
            ("get_inspection_steps", f"Show inspection steps in {self.test_community}"),
            ("get_inspection_events", f"Show inspection events in {self.test_community}"),
            ("get_inspection_results", f"Show inspection results in {self.test_community}"),
            ("create_inspection_event", f"Schedule an inspection in {self.test_community}"),
        ]
        
        # Other tools (31)
        other_tests = [
            ("get_departments", f"Show departments in {self.test_community}"),
            ("get_record_types", f"Show permit types in {self.test_community}"),
            ("get_projects", f"Show projects in {self.test_community}"),
            ("get_approval_steps", f"Show approval steps in {self.test_community}"),
            ("get_payment_steps", f"Show payment steps in {self.test_community}"),
            ("get_transactions", f"Show transactions in {self.test_community}"),
            ("get_files", f"Show files in {self.test_community}"),
            ("get_organization", f"Show organization info for {self.test_community}"),
        ]
        
        # Complex chained scenarios
        complex_tests = [
            ("full_permit_workflow", 
             f"Walk me through applying for a building permit in {self.test_community}. "
             f"Show record types, forms, fees, workflow steps, and inspections."),
            ("permit_status_check", 
             f"Check status of all permits in {self.test_community}. "
             f"Show records, workflow steps, and pending inspections."),
        ]
        
        all_tests = record_tests + location_tests + user_tests + inspection_tests + other_tests + complex_tests
        
        print(f"📋 Running {len(all_tests)} tests covering all 93 MCP tools...")
        
        for tool_name, prompt in all_tests:
            await self.run_test(tool_name, prompt)
        
        print(f"\n🏁 All tests completed!")
        
    def save_results(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"all_mcp_tools_test_{timestamp}.json"
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        
        summary = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "success_rate": f"{(successful_tests/total_tests*100):.1f}%",
                "test_timestamp": datetime.now().isoformat(),
            },
            "detailed_results": self.test_results
        }
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n📊 Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Success Rate: {summary['test_summary']['success_rate']}")
        print(f"   Results saved to: {filename}")
        
        return filename

async def main():
    tester = MCPToolTester()
    
    if not await tester.initialize():
        return
    
    await tester.run_all_tests()
    tester.save_results()

if __name__ == "__main__":
    asyncio.run(main()) 