#!/usr/bin/env python3
"""Test script to verify follow-up actions hook is working"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.permit_assistant.follow_up_actions import extract_follow_up_actions_hook
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage

async def test_hook():
    print("🧪 Testing follow-up actions hook...")
    
    # Create a mock response
    response = AIMessage(content='I can help you with permits. Here are some options for building permits in your area.')
    
    # Create a mock LLM
    llm = ChatOpenAI(model='gpt-4o-mini', temperature=0)
    
    # Test the hook
    config = {
        'llm': llm,
        'configurable': {
            'messages': []
        }
    }
    
    try:
        result = await extract_follow_up_actions_hook(response, config=config)
        
        if hasattr(result, 'additional_kwargs') and 'followUpActions' in result.additional_kwargs:
            actions = result.additional_kwargs['followUpActions']
            print(f'✅ Generated {len(actions)} follow-up actions:')
            for action in actions:
                print(f'  - {action["label"]}: {action["prompt"][:50]}...')
            
            # Check if these are dynamic (not default) actions
            default_labels = ["Apply for Permit", "Check Status", "Schedule Inspection", "Document Requirements", "Calculate Fees", "Get Help"]
            generated_labels = [action["label"] for action in actions]
            
            if any(label not in default_labels for label in generated_labels):
                print("🎉 SUCCESS: Generated dynamic follow-up actions!")
            else:
                print("⚠️  WARNING: Generated actions match default actions")
        else:
            print('❌ No follow-up actions generated')
            
    except Exception as e:
        print(f'❌ Error testing hook: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_hook()) 