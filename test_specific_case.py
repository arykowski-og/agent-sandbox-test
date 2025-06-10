"""Test script for the specific case that didn't generate follow-up actions"""

import asyncio
from src.agents.permit_assistant.graph import get_graph
from langchain_core.messages import HumanMessage

async def test_specific_case():
    print("🔍 Testing specific case: 'what else can you help me with?'")
    print("=" * 60)
    
    agent = get_graph()
    state = {
        'messages': [HumanMessage(content='what else can you help me with?')],
        'ui': [],
        'ui_handled': False
    }
    
    print("📤 Sending message to agent...")
    result = await agent.ainvoke(state)
    
    # Check for AI messages
    ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'type') and msg.type == 'ai']
    
    if ai_messages:
        last_ai_msg = ai_messages[-1]
        print(f"🤖 AI Response length: {len(last_ai_msg.content)} characters")
        print(f"🤖 Response preview: {last_ai_msg.content[:200]}...")
        print(f"🔍 Has additional_kwargs: {hasattr(last_ai_msg, 'additional_kwargs')}")
        
        if hasattr(last_ai_msg, 'additional_kwargs'):
            print(f"🔍 Additional kwargs: {last_ai_msg.additional_kwargs}")
            if last_ai_msg.additional_kwargs and 'followUpActions' in last_ai_msg.additional_kwargs:
                actions = last_ai_msg.additional_kwargs['followUpActions']
                print(f"✅ Found {len(actions)} follow-up actions!")
                for i, action in enumerate(actions, 1):
                    print(f"   {i}. {action['label']} ({action['category']})")
            else:
                print("❌ No followUpActions in additional_kwargs")
        else:
            print("❌ No additional_kwargs attribute")
    else:
        print("❌ No AI messages found")

if __name__ == "__main__":
    asyncio.run(test_specific_case()) 