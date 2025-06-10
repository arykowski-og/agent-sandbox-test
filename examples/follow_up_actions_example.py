"""Example of using follow-up actions with the permit assistant"""

import asyncio
import json
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.permit_assistant.graph import get_graph
from langchain_core.messages import HumanMessage

async def chat_with_follow_ups():
    """Example chat session with follow-up actions"""
    
    print("🏢 Permit Assistant with Follow-up Actions")
    print("=" * 50)
    
    # Get the agent graph
    agent = get_graph()
    
    # Simulate a conversation
    conversation_state = {
        "messages": [],
        "ui": [],
        "ui_handled": False
    }
    
    # Example conversation flow
    user_inputs = [
        "Hi, I'm planning to build a deck on my house. What do I need to know?",
        "The deck will be 12x16 feet and attached to the house.",
        "What documents do I need to prepare for the permit application?"
    ]
    
    for user_input in user_inputs:
        print(f"\n👤 User: {user_input}")
        
        # Add user message to conversation
        conversation_state["messages"].append(HumanMessage(content=user_input))
        
        # Get agent response
        try:
            result = await agent.ainvoke(conversation_state)
            conversation_state = result
            
            # Find the latest AI response
            ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'type') and msg.type == 'ai']
            
            if ai_messages:
                latest_response = ai_messages[-1]
                print(f"\n🤖 Assistant: {latest_response.content}")
                
                # Display follow-up actions if available
                if hasattr(latest_response, 'metadata') and latest_response.metadata:
                    follow_up_actions = latest_response.metadata.get('followUpActions', [])
                    
                    if follow_up_actions:
                        print(f"\n💡 Suggested next steps:")
                        for i, action in enumerate(follow_up_actions, 1):
                            print(f"   {i}. {action['label']} ({action['category']})")
                            print(f"      \"{action['prompt']}\"")
                        
                        # In a real UI, these would be clickable buttons
                        print(f"\n   💬 Click any suggestion to continue the conversation!")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            break
        
        print("\n" + "-" * 60)

def demonstrate_follow_up_structure():
    """Show the structure of follow-up actions"""
    
    print("\n📋 Follow-up Actions Structure")
    print("=" * 40)
    
    example_actions = [
        {
            "label": "Submit Application",
            "prompt": "I'm ready to submit my deck permit application. Can you guide me through the submission process?",
            "category": "application"
        },
        {
            "label": "Check Requirements",
            "prompt": "What are the specific building code requirements for deck construction in my area?",
            "category": "compliance"
        },
        {
            "label": "Calculate Costs",
            "prompt": "How much will the permit fees cost for my deck project?",
            "category": "fee"
        }
    ]
    
    print("Example follow-up actions that might be generated:")
    print(json.dumps(example_actions, indent=2))
    
    print("\n🎯 Categories available:")
    categories = [
        "permit - General permit questions and guidance",
        "inspection - Scheduling, preparing for, or following up on inspections", 
        "application - Starting new applications or continuing existing ones",
        "status - Checking status of permits, applications, or processes",
        "document - Document requirements, submissions, or reviews",
        "fee - Payment information, fee calculations, or billing questions",
        "compliance - Code compliance, regulations, or requirements",
        "general - Other helpful actions or general assistance"
    ]
    
    for category in categories:
        print(f"  • {category}")

async def main():
    """Run the example"""
    demonstrate_follow_up_structure()
    
    print("\n" + "=" * 60)
    print("Starting conversation example...")
    print("=" * 60)
    
    await chat_with_follow_ups()

if __name__ == "__main__":
    asyncio.run(main()) 