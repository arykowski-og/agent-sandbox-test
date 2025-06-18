#!/usr/bin/env python3
"""
Comprehensive test script for the permit assistant agent.
Tests all available tools from the OpenGov PLC MCP server and records results.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agents.permit_assistant.graph import create_permit_agent
from src.agents.permit_assistant.types import AgentState

class PermitAssistantTester:
    """Comprehensive tester for the permit assistant agent"""
    
    def __init__(self):
        self.agent = None
        self.test_results = []
        self.test_community = "demo"  # Default test community
        
    async def initialize(self):
        """Initialize the permit assistant agent"""
        print("🚀 Initializing permit assistant agent...")
        try:
            self.agent = await create_permit_agent()
            print("✅ Agent initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            return False
    
    def record_test_result(self, test_name: str, prompt: str, response: Any, 
                          success: bool, observations: str, execution_time: float):
        """Record a test result"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "prompt": prompt,
            "response": str(response)[:2000] if response else "No response",  # Truncate long responses
            "success": success,
            "observations": observations,
            "execution_time_seconds": execution_time
        }
        self.test_results.append(result)
        
    async def run_test(self, test_name: str, prompt: str, expected_behavior: str = "") -> Dict:
        """Run a single test with the agent"""
        print(f"\n🧪 Running test: {test_name}")
        print(f"📝 Prompt: {prompt}")
        
        start_time = time.time()
        success = False
        observations = ""
        response = None
        
        try:
            # Create initial state
            state = AgentState(
                messages=[{"role": "user", "content": prompt}],
                ui_messages=[]
            )
            
            # Run the agent
            result = await self.agent.ainvoke(state)
            execution_time = time.time() - start_time
            
            # Extract response
            if result and "messages" in result and result["messages"]:
                last_message = result["messages"][-1]
                # Handle both dict and AIMessage objects
                if hasattr(last_message, 'content'):
                    response = last_message.content
                elif isinstance(last_message, dict):
                    response = last_message.get("content", "No content in response")
                else:
                    response = str(last_message)
                
                success = True
                observations = f"Agent responded successfully. Response length: {len(str(response))} chars."
                
                # Check for specific indicators of success
                if "error" in str(response).lower():
                    observations += " Response contains error indicators."
                if "failed" in str(response).lower():
                    observations += " Response contains failure indicators."
                if len(str(response)) < 50:
                    observations += " Response seems unusually short."
                    
            else:
                observations = "No valid response received from agent"
                
        except Exception as e:
            execution_time = time.time() - start_time
            observations = f"Test failed with exception: {str(e)}"
            response = f"ERROR: {str(e)}"
            
        # Record the result
        self.record_test_result(test_name, prompt, response, success, observations, execution_time)
        
        # Print summary
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {execution_time:.2f}s")
        print(f"📊 Observations: {observations}")
        
        return {
            "success": success,
            "response": response,
            "observations": observations,
            "execution_time": execution_time
        }

    async def test_basic_functionality(self):
        """Test basic agent functionality"""
        await self.run_test(
            "Basic Greeting",
            "Hello, I need help with permits. What can you do?",
            "Should introduce capabilities and available tools"
        )
        
        await self.run_test(
            "Tool Listing",
            "What tools and functions do you have available for permit management?",
            "Should list available OpenGov tools and capabilities"
        )

    async def test_record_management(self):
        """Test record-related tools"""
        
        # Test getting records
        await self.run_test(
            "Get Records - Basic",
            f"Can you show me all the permit records in the {self.test_community} community?",
            "Should attempt to fetch records using get_records tool"
        )
        
        await self.run_test(
            "Get Records - With Filters",
            f"Show me all active permit records in {self.test_community} that were created in the last month",
            "Should use get_records with status and date filters"
        )
        
        await self.run_test(
            "List Available Record IDs",
            f"What record IDs are available in the {self.test_community} community?",
            "Should use list_available_record_ids tool"
        )
        
        await self.run_test(
            "Get Specific Record",
            f"Can you get details for record ID '12345' in {self.test_community}?",
            "Should attempt to get specific record, may fail if ID doesn't exist"
        )

    async def test_record_details(self):
        """Test record detail tools"""
        
        await self.run_test(
            "Get Record Form Details",
            f"Show me the form details for any permit record in {self.test_community}",
            "Should attempt to get form details for a record"
        )
        
        await self.run_test(
            "Get Record Location",
            f"What is the primary location for permit records in {self.test_community}?",
            "Should attempt to get primary location information"
        )
        
        await self.run_test(
            "Get Record Attachments",
            f"Show me attachments for permit records in {self.test_community}",
            "Should attempt to get record attachments"
        )
        
        await self.run_test(
            "Get Record Workflow Steps",
            f"What are the workflow steps for permits in {self.test_community}?",
            "Should attempt to get workflow steps"
        )

    async def test_user_and_location_management(self):
        """Test user and location tools"""
        
        await self.run_test(
            "Get Users",
            f"Show me all users in the {self.test_community} community",
            "Should use get_users tool"
        )
        
        await self.run_test(
            "Get Locations",
            f"What locations are available in {self.test_community}?",
            "Should use get_locations tool"
        )
        
        await self.run_test(
            "Get Departments",
            f"List all departments in {self.test_community}",
            "Should use get_departments tool"
        )

    async def test_record_types_and_configuration(self):
        """Test record type and configuration tools"""
        
        await self.run_test(
            "Get Record Types",
            f"What types of permits are available in {self.test_community}?",
            "Should use get_record_types tool"
        )
        
        await self.run_test(
            "Get Record Type Details",
            f"Show me details about permit types and their forms in {self.test_community}",
            "Should attempt to get record type details including forms"
        )
        
        await self.run_test(
            "Get Projects",
            f"What projects exist in {self.test_community}?",
            "Should use get_projects tool"
        )

    async def test_inspection_tools(self):
        """Test inspection-related tools"""
        
        await self.run_test(
            "Get Inspection Steps",
            f"Show me inspection steps in {self.test_community}",
            "Should use get_inspection_steps tool"
        )
        
        await self.run_test(
            "Get Inspection Events",
            f"What inspection events are scheduled in {self.test_community}?",
            "Should use get_inspection_events tool"
        )
        
        await self.run_test(
            "Get Inspection Results",
            f"Show me recent inspection results in {self.test_community}",
            "Should use get_inspection_results tool"
        )
        
        await self.run_test(
            "Get Inspection Templates",
            f"What inspection type templates are available in {self.test_community}?",
            "Should use get_inspection_type_templates tool"
        )

    async def test_approval_and_workflow_tools(self):
        """Test approval and workflow tools"""
        
        await self.run_test(
            "Get Approval Steps",
            f"Show me approval steps in {self.test_community}",
            "Should use get_approval_steps tool"
        )
        
        await self.run_test(
            "Get Document Steps",
            f"What document generation steps exist in {self.test_community}?",
            "Should use get_document_steps tool"
        )

    async def test_payment_and_financial_tools(self):
        """Test payment and financial tools"""
        
        await self.run_test(
            "Get Payment Steps",
            f"Show me payment steps for permits in {self.test_community}",
            "Should use get_payment_steps tool"
        )
        
        await self.run_test(
            "Get Transactions",
            f"What payment transactions exist in {self.test_community}?",
            "Should use get_transactions tool"
        )
        
        await self.run_test(
            "Get Ledger Entries",
            f"Show me ledger entries in {self.test_community}",
            "Should use get_ledger_entries tool"
        )

    async def test_file_management_tools(self):
        """Test file management tools"""
        
        await self.run_test(
            "Get Files",
            f"What files are available in {self.test_community}?",
            "Should use get_files tool"
        )

    async def test_organization_tools(self):
        """Test organization tools"""
        
        await self.run_test(
            "Get Organization Info",
            f"Show me organization information for {self.test_community}",
            "Should use get_organization tool"
        )

    async def test_complex_scenarios(self):
        """Test complex multi-step scenarios"""
        
        await self.run_test(
            "Complex Permit Search",
            f"I need to find all building permits in {self.test_community} that are currently active, "
            f"show me their locations, and tell me what inspection steps are required",
            "Should use multiple tools: get_records with filters, location info, inspection steps"
        )
        
        await self.run_test(
            "Permit Application Guidance",
            f"I want to apply for a new building permit in {self.test_community}. "
            f"What types are available, what forms do I need to fill out, and what fees should I expect?",
            "Should use record types, forms, and payment information tools"
        )
        
        await self.run_test(
            "Inspection Scheduling Help",
            f"Help me understand the inspection process in {self.test_community}. "
            f"What types of inspections are there, how do I schedule them, and what should I expect?",
            "Should use inspection steps, events, and template tools"
        )

    async def test_error_handling(self):
        """Test error handling scenarios"""
        
        await self.run_test(
            "Invalid Community",
            "Show me permits for the community 'nonexistent_community_12345'",
            "Should handle invalid community gracefully"
        )
        
        await self.run_test(
            "Invalid Record ID",
            f"Get details for record ID 'invalid_record_999999' in {self.test_community}",
            "Should handle invalid record ID gracefully"
        )

    async def run_all_tests(self):
        """Run all test suites"""
        print("🎯 Starting comprehensive permit assistant testing...")
        print(f"📍 Using test community: {self.test_community}")
        print("=" * 80)
        
        test_suites = [
            ("Basic Functionality", self.test_basic_functionality),
            ("Record Management", self.test_record_management),
            ("Record Details", self.test_record_details),
            ("User & Location Management", self.test_user_and_location_management),
            ("Record Types & Configuration", self.test_record_types_and_configuration),
            ("Inspection Tools", self.test_inspection_tools),
            ("Approval & Workflow Tools", self.test_approval_and_workflow_tools),
            ("Payment & Financial Tools", self.test_payment_and_financial_tools),
            ("File Management Tools", self.test_file_management_tools),
            ("Organization Tools", self.test_organization_tools),
            ("Complex Scenarios", self.test_complex_scenarios),
            ("Error Handling", self.test_error_handling),
        ]
        
        for suite_name, suite_func in test_suites:
            print(f"\n🔍 Running test suite: {suite_name}")
            print("-" * 60)
            try:
                await suite_func()
            except Exception as e:
                print(f"❌ Test suite {suite_name} failed: {e}")
                self.record_test_result(
                    f"{suite_name} - Suite Error",
                    f"Running {suite_name} test suite",
                    f"Suite failed: {e}",
                    False,
                    f"Entire test suite failed with exception: {e}",
                    0.0
                )
        
        print("\n" + "=" * 80)
        print("🏁 All tests completed!")
        
    def save_results(self, filename: str = None):
        """Save test results to a file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"permit_assistant_test_results_{timestamp}.json"
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r["success"])
        failed_tests = total_tests - successful_tests
        avg_execution_time = sum(r["execution_time_seconds"] for r in self.test_results) / total_tests if total_tests > 0 else 0
        
        summary = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": f"{(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
                "average_execution_time": f"{avg_execution_time:.2f}s",
                "test_community": self.test_community,
                "test_timestamp": datetime.now().isoformat()
            },
            "detailed_results": self.test_results
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Test Results Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Failed: {failed_tests}")
        print(f"   Success Rate: {summary['test_summary']['success_rate']}")
        print(f"   Average Execution Time: {summary['test_summary']['average_execution_time']}")
        print(f"   Results saved to: {filename}")
        
        return filename

async def main():
    """Main test execution function"""
    print("🧪 Permit Assistant Comprehensive Test Suite")
    print("=" * 80)
    
    # Check for custom community argument
    test_community = "demo"
    if len(sys.argv) > 1:
        test_community = sys.argv[1]
        print(f"📍 Using custom test community: {test_community}")
    
    tester = PermitAssistantTester()
    tester.test_community = test_community
    
    # Initialize the agent
    if not await tester.initialize():
        print("❌ Failed to initialize agent. Exiting.")
        return
    
    # Run all tests
    await tester.run_all_tests()
    
    # Save results
    results_file = tester.save_results()
    
    print(f"\n✅ Testing complete! Results saved to {results_file}")
    print("\n💡 To analyze results:")
    print(f"   cat {results_file} | jq '.test_summary'")
    print(f"   cat {results_file} | jq '.detailed_results[] | select(.success == false)'")

if __name__ == "__main__":
    asyncio.run(main()) 