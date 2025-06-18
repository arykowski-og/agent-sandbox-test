# Follow-up Actions Integration with LangGraph

This document shows how to integrate intelligent follow-up actions into your LangGraph agent using a `post_model_hook`.

## Overview

Instead of parsing the AI response on the client side, we use the LLM itself to generate contextually relevant follow-up actions as part of the agent's response. This is done using a `post_model_hook` that processes the LLM's output and extracts structured follow-up actions.

## Graph Integration

### 1. Define the Follow-up Actions Schema

```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class FollowUpAction(BaseModel):
    label: str  # Short action label (2-4 words)
    prompt: str  # Complete question/request the user would ask
    category: str  # permit|inspection|application|status|document|fee|compliance|general

class FollowUpActionsMetadata(BaseModel):
    followUpActions: List[FollowUpAction]
```

### 2. Create the Post-Model Hook

```python
def extract_follow_up_actions_hook(response: Any, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post-model hook that extracts follow-up actions from the LLM response.
    This runs after the LLM generates its response but before returning to the user.
    """
    
    # Get the conversation context from the state
    messages = config.get("configurable", {}).get("messages", [])
    
    # Create a prompt for generating follow-up actions
    follow_up_prompt = f"""
Based on the conversation context and your previous response, suggest 4-6 relevant follow-up actions that the user might want to take next.

Previous response: {response.content}

Recent conversation:
{format_conversation_context(messages[-6:])}

Respond with ONLY a JSON array in this exact format:
[
  {{
    "label": "Short Action Label",
    "prompt": "Complete question or request the user would ask",
    "category": "permit|inspection|application|status|document|fee|compliance|general"
  }}
]

Focus on practical next steps that would be most helpful given the conversation context. Make the prompts specific and actionable for permit and licensing workflows.
"""

    try:
        # Use the same LLM to generate follow-up actions
        llm = config.get("llm")  # Get LLM from config
        follow_up_response = llm.invoke([{"role": "user", "content": follow_up_prompt}])
        
        # Parse the JSON response
        import json
        actions_data = json.loads(follow_up_response.content.strip())
        
        # Validate and create FollowUpAction objects
        follow_up_actions = [
            FollowUpAction(**action) for action in actions_data
            if all(key in action for key in ["label", "prompt", "category"])
        ]
        
        # Add follow-up actions to the response metadata
        if not hasattr(response, 'metadata'):
            response.metadata = {}
        
        response.metadata['followUpActions'] = [action.dict() for action in follow_up_actions]
        
    except Exception as e:
        print(f"Error generating follow-up actions: {e}")
        # Fallback to default actions if generation fails
        response.metadata = response.metadata or {}
        response.metadata['followUpActions'] = get_default_follow_up_actions()
    
    return response

def format_conversation_context(messages: List[Any]) -> str:
    """Format recent messages for context"""
    formatted = []
    for msg in messages:
        role = "User" if msg.type == "human" else "Assistant"
        content = msg.content if isinstance(msg.content, str) else str(msg.content)
        formatted.append(f"{role}: {content}")
    return "\n\n".join(formatted)

def get_default_follow_up_actions() -> List[Dict[str, str]]:
    """Fallback actions when LLM generation fails"""
    return [
        {
            "label": "Apply for Permit",
            "prompt": "I want to apply for a permit. Can you guide me through the application process?",
            "category": "application"
        },
        {
            "label": "Check Status",
            "prompt": "I need to check the status of my permit or application. How can I do this?",
            "category": "status"
        },
        {
            "label": "Schedule Inspection",
            "prompt": "I need to schedule an inspection for my permit. What are the next steps?",
            "category": "inspection"
        },
        {
            "label": "Get Help",
            "prompt": "I need additional assistance with my permit questions.",
            "category": "general"
        }
    ]
```

### 3. Integrate into Your Graph

```python
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

# Your existing graph setup
graph_builder = StateGraph(State)

# Add the post-model hook to your chatbot node
def chatbot_with_follow_ups(state: State):
    # Your existing chatbot logic
    message = llm_with_tools.invoke(state["messages"])
    
    # The post_model_hook will automatically process the response
    # and add follow-up actions to the metadata
    
    return {"messages": [message]}

# Configure the LLM with the post-model hook
llm_with_follow_ups = llm.with_config({
    "post_model_hooks": [extract_follow_up_actions_hook],
    "llm": llm  # Pass the LLM instance for follow-up generation
})

graph_builder.add_node("chatbot", chatbot_with_follow_ups)
# ... rest of your graph setup
```

### 4. Alternative: Dedicated Follow-up Node

If you prefer a separate node for generating follow-up actions:

```python
def generate_follow_ups_node(state: State):
    """Dedicated node for generating follow-up actions"""
    
    # Get the last AI message
    last_ai_message = None
    for msg in reversed(state["messages"]):
        if msg.type == "ai":
            last_ai_message = msg
            break
    
    if not last_ai_message:
        return state
    
    # Generate follow-up actions
    follow_up_prompt = f"""
Based on this conversation, suggest 4-6 relevant follow-up actions:

Last response: {last_ai_message.content}

Respond with ONLY a JSON array of follow-up actions.
"""
    
    try:
        response = llm.invoke([{"role": "user", "content": follow_up_prompt}])
        actions_data = json.loads(response.content.strip())
        
        # Add to the last AI message metadata
        if not hasattr(last_ai_message, 'metadata'):
            last_ai_message.metadata = {}
        
        last_ai_message.metadata['followUpActions'] = actions_data
        
    except Exception as e:
        print(f"Error generating follow-up actions: {e}")
    
    return state

# Add to your graph
graph_builder.add_node("generate_follow_ups", generate_follow_ups_node)
graph_builder.add_edge("chatbot", "generate_follow_ups")
graph_builder.add_edge("generate_follow_ups", END)
```

## Benefits of This Approach

1. **Contextually Aware**: The LLM generates actions based on the full conversation context
2. **Dynamic**: Actions change based on what the user is discussing
3. **Intelligent**: The LLM can understand nuanced situations and suggest appropriate next steps
4. **Consistent**: Actions are generated using the same LLM that handles the conversation
5. **Fallback Safe**: If generation fails, default actions are provided

## Example Generated Actions

For a conversation about building permits, the LLM might generate:

```json
[
  {
    "label": "Submit Plans",
    "prompt": "I have my building plans ready. How do I submit them for review?",
    "category": "document"
  },
  {
    "label": "Check Zoning",
    "prompt": "I need to verify the zoning requirements for my property before applying.",
    "category": "compliance"
  },
  {
    "label": "Calculate Fees",
    "prompt": "What are the total fees I should expect for a building permit of this size?",
    "category": "fee"
  },
  {
    "label": "Timeline Info",
    "prompt": "How long does the building permit approval process typically take?",
    "category": "general"
  }
]
```

This approach ensures that follow-up actions are always relevant, helpful, and contextually appropriate for the user's current situation. 