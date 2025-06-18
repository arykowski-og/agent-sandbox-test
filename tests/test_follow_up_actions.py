"""Test script for follow-up actions integration"""

import asyncio
import json
from src.agents.permit_assistant.graph import create_permit_agent
from langchain_core.messages import HumanMessage

async def test_follow_up_actions():
    """Test the follow-up actions integration"""
    
    print("🧪 Testing Follow-up Actions Integration")
    print("=" * 50)
    
    # Create the agent
    print("📝 Creating permit assistant agent...")
    agent = await create_permit_agent()
    
    # Test conversation
    test_messages = [
        "Hello, I need help with getting a building permit for my home renovation.",
        "I want to add a deck to my house. What permits do I need?",
        "How long does the permit approval process usually take?"
    ]
    
    for i, user_message in enumerate(test_messages, 1):
        print(f"\n🗣️  Test {i}: {user_message}")
        print("-" * 40)
        
        # Create initial state
        state = {
            "messages": [HumanMessage(content=user_message)],
            "ui": [],
            "ui_handled": False
        }
        
        # Run the agent
        try:
            result = await agent.ainvoke(state)
            
            # Check the last AI message for follow-up actions
            ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'type') and msg.type == 'ai']
            
            if ai_messages:
                last_ai_message = ai_messages[-1]
                print(f"🤖 AI Response: {last_ai_message.content[:200]}...")
                
                # Check for follow-up actions in metadata
                if hasattr(last_ai_message, 'metadata') and last_ai_message.metadata:
                    follow_up_actions = last_ai_message.metadata.get('followUpActions', [])
                    
                    if follow_up_actions:
                        print(f"✅ Follow-up actions generated: {len(follow_up_actions)} actions")
                        for j, action in enumerate(follow_up_actions, 1):
                            print(f"   {j}. {action['label']} ({action['category']})")
                            print(f"      → {action['prompt']}")
                    else:
                        print("❌ No follow-up actions found in metadata")
                else:
                    print("❌ No metadata found in AI response")
            else:
                print("❌ No AI messages found in response")
                
        except Exception as e:
            print(f"❌ Error during test: {e}")
            import traceback
            traceback.print_exc()

def test_follow_up_actions_sync():
    """Synchronous wrapper for the test"""
    return asyncio.run(test_follow_up_actions())

if __name__ == "__main__":
    test_follow_up_actions_sync() 