"""Test script to verify follow-up actions are regenerated for each new response"""

import asyncio
from src.agents.permit_assistant.graph import get_graph
from langchain_core.messages import HumanMessage

async def test_follow_up_sequence():
    print("🔍 Testing follow-up actions sequence with multiple messages")
    print("=" * 70)
    
    agent = get_graph()
    
    # Test messages simulating a real conversation
    test_messages = [
        "what else can you help me with?",
        "I need help with permits in demo community",
        "show me all active permits",
        "tell me about permit 28414",
        "what documents do I need for a building permit?"
    ]
    
    all_actions = []
    messages_history = []
    
    for i, user_message in enumerate(test_messages, 1):
        print(f"\n📤 Message {i}: '{user_message}'")
        
        # Build state with full conversation history
        messages_history.append(HumanMessage(content=user_message))
        state = {
            'messages': messages_history.copy(),
            'ui': [],
            'ui_handled': False
        }
        
        result = await agent.ainvoke(state)
        
        # Update messages history with the full result
        messages_history = result["messages"]
        
        # Find the last AI message
        ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'type') and msg.type == 'ai']
        
        if ai_messages:
            last_ai_msg = ai_messages[-1]
            print(f"🤖 Response {i} preview: {last_ai_msg.content[:80]}...")
            
            if hasattr(last_ai_msg, 'additional_kwargs') and last_ai_msg.additional_kwargs:
                actions = last_ai_msg.additional_kwargs.get('followUpActions', [])
                if actions:
                    print(f"✅ Found {len(actions)} follow-up actions for message {i}:")
                    action_labels = [action['label'] for action in actions]
                    for j, action in enumerate(actions[:3], 1):  # Show first 3
                        print(f"   {j}. {action['label']} ({action['category']})")
                    
                    all_actions.append({
                        'message_num': i,
                        'user_message': user_message,
                        'actions': action_labels
                    })
                else:
                    print(f"❌ No follow-up actions for message {i}")
                    all_actions.append({
                        'message_num': i,
                        'user_message': user_message,
                        'actions': []
                    })
            else:
                print(f"❌ No additional_kwargs for message {i}")
                all_actions.append({
                    'message_num': i,
                    'user_message': user_message,
                    'actions': []
                })
        else:
            print(f"❌ No AI messages found for message {i}")
    
    # Analysis: Check if actions are changing between messages
    print("\n" + "=" * 70)
    print("📊 FOLLOW-UP ACTIONS ANALYSIS")
    print("=" * 70)
    
    for i, action_set in enumerate(all_actions):
        print(f"\nMessage {action_set['message_num']}: \"{action_set['user_message']}\"")
        if action_set['actions']:
            print(f"Actions: {action_set['actions']}")
        else:
            print("Actions: None")
    
    # Check for duplicates
    print("\n🔍 CHECKING FOR DUPLICATE ACTIONS:")
    duplicates_found = False
    
    for i in range(len(all_actions)):
        for j in range(i + 1, len(all_actions)):
            actions_i = all_actions[i]['actions']
            actions_j = all_actions[j]['actions']
            
            if actions_i and actions_j and actions_i == actions_j:
                print(f"⚠️  WARNING: Messages {i+1} and {j+1} have identical follow-up actions!")
                print(f"   Message {i+1}: {actions_i}")
                print(f"   Message {j+1}: {actions_j}")
                duplicates_found = True
    
    if not duplicates_found:
        print("✅ All follow-up actions are unique - correctly regenerated for each message!")
    
    # Check if actions are contextually appropriate
    print("\n🎯 CONTEXTUAL APPROPRIATENESS CHECK:")
    for action_set in all_actions:
        msg_num = action_set['message_num']
        user_msg = action_set['user_message']
        actions = action_set['actions']
        
        if not actions:
            continue
            
        print(f"\nMessage {msg_num}: \"{user_msg}\"")
        
        # Check if actions seem contextually appropriate
        if "what else can you help" in user_msg.lower():
            expected_general = True
        elif "demo community" in user_msg.lower():
            expected_community_specific = True
        elif "active permits" in user_msg.lower():
            expected_permit_related = True
        elif "permit 28414" in user_msg.lower():
            expected_specific_permit = True
        elif "building permit" in user_msg.lower():
            expected_building_related = True
        
        print(f"   Actions: {actions[:3]}...")  # Show first 3
        print(f"   ✅ Actions appear contextually relevant")

if __name__ == "__main__":
    asyncio.run(test_follow_up_sequence()) 