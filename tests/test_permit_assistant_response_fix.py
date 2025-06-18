#!/usr/bin/env python3
"""
Test script to verify that the permit assistant always provides text responses
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_permit_assistant_responses():
    """Test that the permit assistant always provides text responses"""
    try:
        print("🧪 Testing Permit Assistant Response Fix...")
        print("=" * 60)
        
        # Import and create the agent
        from src.agents.permit_assistant.graph import create_permit_agent
        from src.agents.permit_assistant.types import AgentState
        from langchain_core.messages import HumanMessage
        
        graph = await create_permit_agent()
        print("✅ Agent created successfully")
        
        # Test cases to verify LLM always responds
        test_cases = [
            {
                "name": "Tool that should fail (workflow steps)",
                "message": "Show me workflow steps for permits in demo community",
                "expected": "Should get text response explaining the error"
            },
            {
                "name": "Tool that might show UI (get records)", 
                "message": "Show me all permit records in demo community",
                "expected": "Should get text response + possibly UI"
            },
            {
                "name": "General question (no tools)",
                "message": "What types of permits can I apply for?",
                "expected": "Should get helpful text response"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🧪 Test {i}: {test_case['name']}")
            print(f"📝 Message: {test_case['message']}")
            print(f"🎯 Expected: {test_case['expected']}")
            print("-" * 40)
            
            # Create test state
            state = AgentState(
                messages=[HumanMessage(content=test_case['message'])],
                ui_messages=[]
            )
            
            # Run the agent
            result = await graph.ainvoke(state)
            
            # Check the result
            if "messages" in result and result["messages"]:
                # Find the last AI message (should be the LLM response)
                ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'content') and not hasattr(msg, 'tool_calls')]
                
                if ai_messages:
                    last_response = ai_messages[-1]
                    response_content = getattr(last_response, 'content', 'No content')
                    
                    print(f"✅ LLM Response received:")
                    print(f"📄 Content: {response_content[:300]}...")
                    print(f"📊 Length: {len(response_content)} characters")
                    
                    if len(response_content) > 20:  # Reasonable response length
                        print("✅ PASS: LLM provided a substantial text response")
                    else:
                        print("❌ FAIL: LLM response too short or empty")
                else:
                    print("❌ FAIL: No AI response message found")
                    
                # Show all message types for debugging
                message_types = [type(msg).__name__ for msg in result["messages"]]
                print(f"🔍 All message types: {message_types}")
                
            else:
                print("❌ FAIL: No messages in result")
            
            print()
        
        print("🎉 Test completed!")
        print("\n📋 Summary:")
        print("- The agent should now ALWAYS provide text responses")
        print("- UI components should be supplementary to text responses")
        print("- Tool failures should result in helpful error messages")
        print("- No more silent responses!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_permit_assistant_responses()) 