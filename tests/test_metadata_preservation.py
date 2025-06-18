"""Test script to verify metadata preservation through graph execution"""

import asyncio
from src.agents.permit_assistant.graph import get_graph
from langchain_core.messages import HumanMessage

async def test_metadata_preservation():
    print("🔍 Testing Metadata Preservation Through Graph")
    print("=" * 50)
    
    agent = get_graph()
    
    # Test with the exact same message
    test_message = "what else can you help me with?"
    
    state = {
        'messages': [HumanMessage(content=test_message)],
        'ui': [],
        'ui_handled': False
    }
    
    print(f"📤 Testing with message: '{test_message}'")
    print("🔄 Invoking agent...")
    
    result = await agent.ainvoke(state)
    
    print(f"📥 Result received with {len(result['messages'])} messages")
    
    # Check all messages for metadata
    for i, msg in enumerate(result['messages']):
        print(f"\n📋 Message {i}:")
        print(f"   Type: {getattr(msg, 'type', 'unknown')}")
        print(f"   Has metadata: {hasattr(msg, 'metadata')}")
        
        if hasattr(msg, 'metadata') and msg.metadata:
            print(f"   Metadata keys: {list(msg.metadata.keys())}")
            if 'followUpActions' in msg.metadata:
                actions = msg.metadata['followUpActions']
                print(f"   ✅ Follow-up actions: {len(actions)} actions")
                for j, action in enumerate(actions[:3], 1):  # Show first 3
                    print(f"      {j}. {action['label']} ({action['category']})")
                if len(actions) > 3:
                    print(f"      ... and {len(actions) - 3} more")
            else:
                print(f"   ❌ No followUpActions in metadata")
        elif hasattr(msg, 'metadata'):
            print(f"   📝 Metadata is empty/None")
        else:
            print(f"   📝 No metadata attribute")
    
    # Final check - get the last AI message specifically
    ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'type') and msg.type == 'ai']
    
    if ai_messages:
        last_ai = ai_messages[-1]
        print(f"\n🎯 Final AI Message Analysis:")
        print(f"   Content length: {len(last_ai.content)} chars")
        print(f"   Has metadata: {hasattr(last_ai, 'metadata')}")
        
        if hasattr(last_ai, 'metadata'):
            if last_ai.metadata:
                print(f"   Metadata type: {type(last_ai.metadata)}")
                print(f"   Metadata content: {last_ai.metadata}")
                
                if 'followUpActions' in last_ai.metadata:
                    print(f"   ✅ SUCCESS: Follow-up actions found!")
                else:
                    print(f"   ❌ ISSUE: No followUpActions key in metadata")
            else:
                print(f"   ❌ ISSUE: Metadata is None or empty")
        else:
            print(f"   ❌ ISSUE: No metadata attribute on AI message")
    else:
        print(f"\n❌ CRITICAL: No AI messages found in result")

if __name__ == "__main__":
    asyncio.run(test_metadata_preservation()) 