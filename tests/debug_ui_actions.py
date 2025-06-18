"""Debug script to verify the message structure that the UI receives"""

import asyncio
import json
from src.agents.permit_assistant.graph import get_graph
from langchain_core.messages import HumanMessage

async def debug_ui_message_structure():
    print("🔍 Debugging UI message structure")
    print("=" * 60)
    
    agent = get_graph()
    
    # Test with two different messages
    messages = [
        "what else can you help me with?",
        "I need help with permits in demo community"
    ]
    
    conversation_history = []
    
    for i, user_message in enumerate(messages, 1):
        print(f"\n📤 Message {i}: '{user_message}'")
        
        conversation_history.append(HumanMessage(content=user_message))
        state = {
            'messages': conversation_history.copy(),
            'ui': [],
            'ui_handled': False
        }
        
        result = await agent.ainvoke(state)
        conversation_history = result["messages"]
        
        # Find the last AI message (what the UI would receive)
        ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'type') and msg.type == 'ai']
        
        if ai_messages:
            last_ai_msg = ai_messages[-1]
            
            print(f"\n🔍 AI Message {i} Structure:")
            print(f"   Type: {type(last_ai_msg).__name__}")
            print(f"   Has additional_kwargs: {hasattr(last_ai_msg, 'additional_kwargs')}")
            
            if hasattr(last_ai_msg, 'additional_kwargs'):
                print(f"   additional_kwargs keys: {list(last_ai_msg.additional_kwargs.keys()) if last_ai_msg.additional_kwargs else 'None'}")
                
                if last_ai_msg.additional_kwargs and 'followUpActions' in last_ai_msg.additional_kwargs:
                    actions = last_ai_msg.additional_kwargs['followUpActions']
                    print(f"   Follow-up actions count: {len(actions)}")
                    print(f"   First action: {actions[0] if actions else 'None'}")
                    
                    # Show what the UI component would receive
                    print(f"\n📱 What UI Component Receives:")
                    print(f"   followUpActions prop: {json.dumps(actions[:2], indent=2)}")  # Show first 2
                else:
                    print("   ❌ No followUpActions in additional_kwargs")
            
            # Also check if there are any other metadata fields
            if hasattr(last_ai_msg, 'metadata'):
                print(f"   Has metadata: {last_ai_msg.metadata}")
            
            print(f"   Content preview: {last_ai_msg.content[:100]}...")

if __name__ == "__main__":
    asyncio.run(debug_ui_message_structure()) 