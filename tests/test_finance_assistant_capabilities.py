#!/usr/bin/env python3
"""
Finance Assistant Capabilities Test Suite

This script tests all GraphQL capabilities of the Finance Assistant and evaluates
the relevance and quality of responses for end users.
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import sys
import os

# Add the src directory to the path so we can import the finance assistant
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from agents.finance_assistant import get_finance_assistant

class FinanceAssistantTester:
    def __init__(self):
        self.test_results = []
        self.agent = None
        
    async def setup(self):
        """Initialize the Finance Assistant agent"""
        print("🏦 Setting up Finance Assistant for testing...")
        self.agent = await get_finance_assistant()
        print("✅ Finance Assistant ready for testing\n")
    
    async def run_test(self, test_name: str, user_query: str, expected_capabilities: List[str]) -> Dict[str, Any]:
        """Run a single test and evaluate the response"""
        print(f"🧪 Testing: {test_name}")
        print(f"📝 Query: {user_query}")
        
        start_time = time.time()
        
        try:
            # Execute the query
            result = await self.agent.ainvoke({
                "messages": [{"role": "user", "content": user_query}]
            })
            
            response = result["messages"][-1].content
            execution_time = time.time() - start_time
            
            print(f"⏱️  Response time: {execution_time:.2f}s")
            print(f"📄 Response length: {len(response)} characters")
            print(f"🤖 Response preview: {response[:200]}...")
            
            # Evaluate the response
            evaluation = self.evaluate_response(response, expected_capabilities, user_query)
            
            test_result = {
                "test_name": test_name,
                "user_query": user_query,
                "response": response,
                "execution_time": execution_time,
                "expected_capabilities": expected_capabilities,
                "evaluation": evaluation,
                "timestamp": datetime.now().isoformat()
            }
            
            self.test_results.append(test_result)
            
            print(f"📊 Relevance Score: {evaluation['relevance_score']}/10")
            print(f"✅ Capabilities Met: {evaluation['capabilities_met']}/{len(expected_capabilities)}")
            print("-" * 80)
            
            return test_result
            
        except Exception as e:
            print(f"❌ Test failed with error: {str(e)}")
            error_result = {
                "test_name": test_name,
                "user_query": user_query,
                "error": str(e),
                "execution_time": time.time() - start_time,
                "expected_capabilities": expected_capabilities,
                "evaluation": {"relevance_score": 0, "capabilities_met": 0, "issues": [f"Execution error: {str(e)}"]},
                "timestamp": datetime.now().isoformat()
            }
            self.test_results.append(error_result)
            print("-" * 80)
            return error_result
    
    def evaluate_response(self, response: str, expected_capabilities: List[str], user_query: str) -> Dict[str, Any]:
        """Evaluate the quality and relevance of a response"""
        evaluation = {
            "relevance_score": 0,
            "capabilities_met": 0,
            "strengths": [],
            "issues": [],
            "recommendations": []
        }
        
        response_lower = response.lower()
        
        # Check if expected capabilities are addressed
        capabilities_found = 0
        for capability in expected_capabilities:
            if any(keyword in response_lower for keyword in capability.lower().split()):
                capabilities_found += 1
        
        evaluation["capabilities_met"] = capabilities_found
        
        # Evaluate relevance based on various criteria
        relevance_score = 0
        
        # 1. Does it address the user's query directly? (0-3 points)
        query_keywords = user_query.lower().split()
        query_relevance = sum(1 for keyword in query_keywords if keyword in response_lower and len(keyword) > 3)
        if query_relevance >= 3:
            relevance_score += 3
            evaluation["strengths"].append("Directly addresses user query")
        elif query_relevance >= 1:
            relevance_score += 1
            evaluation["issues"].append("Partially addresses user query")
        else:
            evaluation["issues"].append("Does not clearly address user query")
        
        # 2. Does it provide actionable information? (0-2 points)
        actionable_indicators = ["can", "will", "use", "execute", "query", "analyze", "help", "provide"]
        actionable_count = sum(1 for indicator in actionable_indicators if indicator in response_lower)
        if actionable_count >= 5:
            relevance_score += 2
            evaluation["strengths"].append("Provides actionable information")
        elif actionable_count >= 2:
            relevance_score += 1
        else:
            evaluation["issues"].append("Lacks actionable information")
        
        # 3. Does it show technical competency? (0-2 points)
        technical_indicators = ["graphql", "schema", "query", "types", "data", "financial", "budget", "revenue"]
        technical_count = sum(1 for indicator in technical_indicators if indicator in response_lower)
        if technical_count >= 4:
            relevance_score += 2
            evaluation["strengths"].append("Demonstrates technical competency")
        elif technical_count >= 2:
            relevance_score += 1
        else:
            evaluation["issues"].append("Limited technical depth")
        
        # 4. Is the response appropriately detailed? (0-2 points)
        if len(response) > 500:
            relevance_score += 2
            evaluation["strengths"].append("Comprehensive response")
        elif len(response) > 200:
            relevance_score += 1
        else:
            evaluation["issues"].append("Response too brief")
        
        # 5. Does it provide specific examples or data? (0-1 point)
        if any(indicator in response for indicator in ["example", ":", "•", "-", "1.", "2."]):
            relevance_score += 1
            evaluation["strengths"].append("Includes examples or structured information")
        else:
            evaluation["issues"].append("Lacks specific examples")
        
        evaluation["relevance_score"] = relevance_score
        
        # Generate recommendations based on issues
        if "Does not clearly address user query" in evaluation["issues"]:
            evaluation["recommendations"].append("Improve query understanding and response targeting")
        
        if "Lacks actionable information" in evaluation["issues"]:
            evaluation["recommendations"].append("Include more specific next steps and actionable guidance")
        
        if "Limited technical depth" in evaluation["issues"]:
            evaluation["recommendations"].append("Enhance technical explanations and domain expertise")
        
        if "Response too brief" in evaluation["issues"]:
            evaluation["recommendations"].append("Provide more comprehensive and detailed responses")
        
        if "Lacks specific examples" in evaluation["issues"]:
            evaluation["recommendations"].append("Include concrete examples and structured data presentation")
        
        return evaluation
    
    async def run_all_tests(self):
        """Run comprehensive tests for all Finance Assistant capabilities"""
        
        test_cases = [
            {
                "name": "Schema Discovery - Initial Exploration",
                "query": "What types of financial data are available in the system?",
                "capabilities": ["schema introspection", "data types", "financial categories"]
            },
            {
                "name": "Schema Discovery - Detailed Types",
                "query": "Can you show me all the available GraphQL types and what they represent?",
                "capabilities": ["type listing", "descriptions", "categorization"]
            },
            {
                "name": "Query Operations Discovery",
                "query": "What specific financial queries can I execute? Show me the available operations.",
                "capabilities": ["query operations", "parameters", "return types"]
            },
            {
                "name": "Basic Connectivity Test",
                "query": "Test the connection to the financial system with a simple query",
                "capabilities": ["connectivity", "basic query execution", "error handling"]
            },
            {
                "name": "Budget Analysis Request",
                "query": "I need to analyze budget vs actual spending. What budget data is available and how can I query it?",
                "capabilities": ["budget analysis", "variance analysis", "spending data"]
            },
            {
                "name": "Revenue Analysis Request", 
                "query": "Help me understand revenue streams and collection patterns. What revenue data can I access?",
                "capabilities": ["revenue analysis", "collection tracking", "revenue sources"]
            },
            {
                "name": "Account Management Query",
                "query": "I want to explore the chart of accounts and account hierarchies. What account information is available?",
                "capabilities": ["account management", "chart of accounts", "hierarchies"]
            },
            {
                "name": "Expenditure Tracking Request",
                "query": "Show me how to track departmental expenses and spending patterns over time",
                "capabilities": ["expenditure tracking", "departmental analysis", "spending patterns"]
            },
            {
                "name": "Financial Reporting Guidance",
                "query": "I need to generate a comprehensive financial report. What data should I include and how do I structure the queries?",
                "capabilities": ["financial reporting", "data compilation", "query structuring"]
            },
            {
                "name": "Complex Analysis Request",
                "query": "I want to perform a complete financial analysis including budgets, actuals, variances, and trends. Guide me through the process.",
                "capabilities": ["comprehensive analysis", "multi-data integration", "trend analysis"]
            },
            {
                "name": "Error Handling Test",
                "query": "Execute a GraphQL query that might fail to test error handling: query { nonExistentField }",
                "capabilities": ["error handling", "user guidance", "troubleshooting"]
            },
            {
                "name": "Data Relationship Understanding",
                "query": "Explain how different financial data types relate to each other - accounts, budgets, transactions, etc.",
                "capabilities": ["data relationships", "system understanding", "integration guidance"]
            }
        ]
        
        print("🚀 Starting comprehensive Finance Assistant capability testing...")
        print("=" * 80)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test {i}/{len(test_cases)}")
            await self.run_test(
                test_case["name"],
                test_case["query"], 
                test_case["capabilities"]
            )
            
            # Small delay between tests
            await asyncio.sleep(1)
    
    def generate_summary_report(self) -> str:
        """Generate a comprehensive summary report of all test results"""
        
        if not self.test_results:
            return "No test results available."
        
        # Calculate overall statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if "error" not in r])
        failed_tests = total_tests - successful_tests
        
        avg_relevance = sum(r["evaluation"]["relevance_score"] for r in self.test_results) / total_tests
        avg_capabilities = sum(r["evaluation"]["capabilities_met"] for r in self.test_results) / total_tests
        avg_response_time = sum(r.get("execution_time", 0) for r in self.test_results) / total_tests
        
        # Collect all issues and recommendations
        all_issues = []
        all_recommendations = []
        all_strengths = []
        
        for result in self.test_results:
            all_issues.extend(result["evaluation"].get("issues", []))
            all_recommendations.extend(result["evaluation"].get("recommendations", []))
            all_strengths.extend(result["evaluation"].get("strengths", []))
        
        # Count frequency of issues and recommendations
        issue_counts = {}
        rec_counts = {}
        strength_counts = {}
        
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        for rec in all_recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1
            
        for strength in all_strengths:
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        
        # Generate report
        report = f"""
# Finance Assistant Capabilities Test Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary
- **Total Tests**: {total_tests}
- **Successful Tests**: {successful_tests}
- **Failed Tests**: {failed_tests}
- **Average Relevance Score**: {avg_relevance:.1f}/10
- **Average Capabilities Met**: {avg_capabilities:.1f}
- **Average Response Time**: {avg_response_time:.2f}s

## Overall Assessment
"""
        
        if avg_relevance >= 8:
            report += "🟢 **EXCELLENT** - Finance Assistant performs exceptionally well across all capabilities.\n"
        elif avg_relevance >= 6:
            report += "🟡 **GOOD** - Finance Assistant performs well with some areas for improvement.\n"
        elif avg_relevance >= 4:
            report += "🟠 **FAIR** - Finance Assistant has moderate performance with significant improvement needed.\n"
        else:
            report += "🔴 **POOR** - Finance Assistant requires major improvements to meet user needs.\n"
        
        # Top strengths
        report += "\n## Key Strengths\n"
        sorted_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)
        for strength, count in sorted_strengths[:5]:
            report += f"- **{strength}** (observed in {count} tests)\n"
        
        # Top issues
        report += "\n## Primary Issues\n"
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        for issue, count in sorted_issues[:5]:
            report += f"- **{issue}** (occurred in {count} tests)\n"
        
        # Top recommendations
        report += "\n## Priority Recommendations\n"
        sorted_recs = sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)
        for rec, count in sorted_recs[:5]:
            report += f"- **{rec}** (needed for {count} test scenarios)\n"
        
        # Detailed test results
        report += "\n## Detailed Test Results\n"
        
        for i, result in enumerate(self.test_results, 1):
            report += f"\n### Test {i}: {result['test_name']}\n"
            report += f"**Query**: {result['user_query']}\n"
            
            if "error" in result:
                report += f"**Status**: ❌ FAILED - {result['error']}\n"
            else:
                score = result['evaluation']['relevance_score']
                if score >= 8:
                    status = "🟢 EXCELLENT"
                elif score >= 6:
                    status = "🟡 GOOD"
                elif score >= 4:
                    status = "🟠 FAIR"
                else:
                    status = "🔴 POOR"
                
                report += f"**Status**: {status} (Score: {score}/10)\n"
                report += f"**Capabilities Met**: {result['evaluation']['capabilities_met']}/{len(result['expected_capabilities'])}\n"
                report += f"**Response Time**: {result['execution_time']:.2f}s\n"
                
                if result['evaluation']['strengths']:
                    report += f"**Strengths**: {', '.join(result['evaluation']['strengths'])}\n"
                
                if result['evaluation']['issues']:
                    report += f"**Issues**: {', '.join(result['evaluation']['issues'])}\n"
        
        # Action items
        report += "\n## Recommended Action Items\n"
        
        if failed_tests > 0:
            report += f"1. **Fix Critical Errors**: {failed_tests} tests failed due to execution errors\n"
        
        if avg_relevance < 6:
            report += "2. **Improve Response Relevance**: Focus on directly addressing user queries\n"
        
        if "Lacks actionable information" in [issue for issue, count in sorted_issues[:3]]:
            report += "3. **Enhance Actionability**: Provide more specific guidance and next steps\n"
        
        if "Limited technical depth" in [issue for issue, count in sorted_issues[:3]]:
            report += "4. **Increase Technical Depth**: Add more domain-specific expertise\n"
        
        if avg_response_time > 5:
            report += "5. **Optimize Performance**: Reduce response times for better user experience\n"
        
        report += "\n## Conclusion\n"
        report += f"The Finance Assistant shows {'strong' if avg_relevance >= 7 else 'moderate' if avg_relevance >= 5 else 'limited'} capability in handling financial data queries. "
        
        if avg_relevance >= 7:
            report += "Minor refinements will make it excellent for production use."
        elif avg_relevance >= 5:
            report += "Focused improvements in the identified areas will significantly enhance user experience."
        else:
            report += "Substantial improvements are needed before it can effectively serve end users."
        
        return report
    
    async def save_detailed_results(self, filename: str = "finance_assistant_test_results.json"):
        """Save detailed test results to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"📄 Detailed results saved to {filename}")

async def main():
    """Main test execution function"""
    tester = FinanceAssistantTester()
    
    try:
        await tester.setup()
        await tester.run_all_tests()
        
        # Generate and display summary report
        report = tester.generate_summary_report()
        print("\n" + "="*80)
        print("📊 FINAL ASSESSMENT REPORT")
        print("="*80)
        print(report)
        
        # Save detailed results
        await tester.save_detailed_results()
        
        # Save report to file
        with open("finance_assistant_assessment_report.md", "w") as f:
            f.write(report)
        print("📄 Assessment report saved to finance_assistant_assessment_report.md")
        
    except Exception as e:
        print(f"❌ Test suite failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 