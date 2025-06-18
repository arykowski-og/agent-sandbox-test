#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_finance_assistant():
    from agents.finance_assistant import create_finance_agent
    
    print('🏦 Testing Finance Assistant Capabilities')
    print('=' * 50)
    
    agent = await create_finance_agent()
    
    test_cases = [
        'What types of financial data are available in the system?',
        'Can you show me all the available GraphQL types?',
        'What specific financial queries can I execute?',
        'Test the connection with a simple query',
        'I need to analyze budget vs actual spending. What data is available?',
        'Help me understand revenue streams and collection patterns',
        'I want to explore the chart of accounts and account hierarchies',
        'Show me how to track departmental expenses over time',
        'Execute a GraphQL query that might fail: query { nonExistentField }',
        'Explain how different financial data types relate to each other'
    ]
    
    results = []
    
    for i, query in enumerate(test_cases, 1):
        print(f'\n📋 Test {i}/{len(test_cases)}: {query[:50]}...')
        
        try:
            result = await agent.ainvoke({'messages': [{'role': 'user', 'content': query}]})
            response = result['messages'][-1].content
            
            # Simple evaluation
            score = 0
            if len(response) > 200: score += 2
            if 'graphql' in response.lower(): score += 1
            if 'financial' in response.lower(): score += 1
            if 'data' in response.lower(): score += 1
            if any(word in response.lower() for word in ['can', 'will', 'help', 'provide']): score += 2
            if any(char in response for char in [':', '•', '-', '1.']): score += 1
            
            results.append({
                'query': query,
                'response_length': len(response),
                'score': score,
                'preview': response[:150] + '...' if len(response) > 150 else response
            })
            
            print(f'✅ Score: {score}/8, Length: {len(response)} chars')
            
        except Exception as e:
            print(f'❌ Failed: {str(e)}')
            results.append({'query': query, 'error': str(e), 'score': 0})
    
    # Summary
    print(f'\n📊 SUMMARY')
    print('=' * 50)
    total_score = sum(r.get('score', 0) for r in results)
    max_score = len(test_cases) * 8
    avg_score = total_score / len(test_cases)
    
    print(f'Total Score: {total_score}/{max_score}')
    print(f'Average Score: {avg_score:.1f}/8')
    print(f'Success Rate: {len([r for r in results if "error" not in r])}/{len(test_cases)}')
    
    if avg_score >= 6:
        print('🟢 EXCELLENT - Finance Assistant performs very well')
        assessment = 'EXCELLENT'
    elif avg_score >= 4:
        print('🟡 GOOD - Finance Assistant performs adequately with room for improvement')
        assessment = 'GOOD'
    else:
        print('🔴 NEEDS IMPROVEMENT - Finance Assistant requires significant enhancements')
        assessment = 'NEEDS IMPROVEMENT'
    
    # Key findings
    print(f'\n🔍 KEY FINDINGS:')
    avg_length = sum(r.get('response_length', 0) for r in results if 'response_length' in r) / len([r for r in results if 'response_length' in r])
    print(f'- Average response length: {avg_length:.0f} characters')
    print(f'- Failed tests: {len([r for r in results if "error" in r])}')
    
    low_scores = [r for r in results if r.get('score', 0) < 4]
    if low_scores:
        print(f'- {len(low_scores)} tests scored below 4/8 - need improvement')
    
    # Detailed recommendations
    print(f'\n📋 RECOMMENDATIONS:')
    
    if avg_score < 6:
        print('1. Improve response relevance - ensure queries are directly addressed')
    
    if avg_length < 300:
        print('2. Provide more comprehensive responses with detailed explanations')
    
    failed_tests = len([r for r in results if "error" in r])
    if failed_tests > 0:
        print(f'3. Fix {failed_tests} failing test cases - investigate error handling')
    
    if len(low_scores) > 3:
        print('4. Enhance technical depth and actionable guidance in responses')
    
    print(f'\n🎯 OVERALL ASSESSMENT: {assessment}')
    
    return results

if __name__ == "__main__":
    asyncio.run(test_finance_assistant()) 