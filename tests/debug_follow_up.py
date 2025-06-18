"""Debug script for follow-up actions"""

import asyncio
from src.agents.permit_assistant.graph import get_graph
from langchain_core.messages import HumanMessage

async def debug_follow_up():
    print("🔍 Debugging Follow-up Actions")
    print("=" * 40)
    
    # Get the agent
    agent = get_graph()
    
    # Test with a simple message
    state = {
        "messages": [HumanMessage(content="Hello, I need help with a building permit.")],
        "ui": [],
        "ui_handled": False
    }
    
    print("📤 Sending message to agent...")
    result = await agent.ainvoke(state)
    
    # Check for AI messages
    ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'type') and msg.type == 'ai']
    
    if ai_messages:
        last_ai_msg = ai_messages[-1]
        print(f"🤖 AI Response: {last_ai_msg.content[:100]}...")
        print(f"🔍 Has metadata: {hasattr(last_ai_msg, 'metadata')}")
        
        if hasattr(last_ai_msg, 'metadata'):
            print(f"🔍 Metadata: {last_ai_msg.metadata}")
            if last_ai_msg.metadata and 'followUpActions' in last_ai_msg.metadata:
                actions = last_ai_msg.metadata['followUpActions']
                print(f"✅ Found {len(actions)} follow-up actions!")
                for i, action in enumerate(actions, 1):
                    print(f"   {i}. {action['label']} ({action['category']})")
            else:
                print("❌ No followUpActions in metadata")
        else:
            print("❌ No metadata attribute")
    else:
        print("❌ No AI messages found")

if __name__ == "__main__":
    asyncio.run(debug_follow_up()) 