# Follow-up Actions Integration

This document explains the follow-up actions integration implemented in the permit assistant using LangGraph's `post_model_hook` feature.

## Overview

The follow-up actions system automatically generates contextually relevant action suggestions after each AI response. These actions help guide users through common next steps in permit and licensing workflows.

## Implementation

### Core Components

1. **`follow_up_actions.py`** - Contains the main implementation:
   - `FollowUpAction` - Pydantic model for action structure
   - `extract_follow_up_actions_hook` - Post-model hook function
   - `create_follow_up_hook` - Factory function for creating hooks

2. **Modified `chatbot.py`** - Integrates the hook into the chatbot node
3. **Modified `graph.py`** - Imports and configures the follow-up system

### How It Works

1. **User sends a message** → Agent processes and responds
2. **Post-model hook triggers** → Analyzes conversation context
3. **LLM generates actions** → Creates 4-6 relevant follow-up suggestions
4. **Actions added to metadata** → Attached to the AI response
5. **Client displays actions** → User can click to continue conversation

### Action Structure

Each follow-up action contains:

```json
{
  "label": "Short Action Label",
  "prompt": "Complete question or request the user would ask",
  "category": "permit|inspection|application|status|document|fee|compliance|general"
}
```

### Categories

- **permit** - General permit questions and guidance
- **inspection** - Scheduling, preparing for, or following up on inspections
- **application** - Starting new applications or continuing existing ones
- **status** - Checking status of permits, applications, or processes
- **document** - Document requirements, submissions, or reviews
- **fee** - Payment information, fee calculations, or billing questions
- **compliance** - Code compliance, regulations, or requirements
- **general** - Other helpful actions or general assistance

## Usage

### In the Agent

The follow-up actions are automatically generated and attached to AI responses. No additional code is needed in the graph - the integration is handled by the post-model hook.

### In Client Applications

Access follow-up actions from the AI message metadata:

```python
# Get the latest AI response
ai_message = result["messages"][-1]

# Extract follow-up actions
if hasattr(ai_message, 'metadata') and ai_message.metadata:
    follow_up_actions = ai_message.metadata.get('followUpActions', [])
    
    for action in follow_up_actions:
        print(f"Action: {action['label']}")
        print(f"Prompt: {action['prompt']}")
        print(f"Category: {action['category']}")
```

### Example Actions

For a conversation about building permits:

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
  }
]
```

## Testing

Run the test script to verify the integration:

```bash
python test_follow_up_actions.py
```

Run the example to see it in action:

```bash
python examples/follow_up_actions_example.py
```

## Error Handling

The system includes robust error handling:

1. **LLM Generation Fails** → Falls back to default actions
2. **Invalid JSON Response** → Uses default actions
3. **Missing Categories** → Filters out invalid actions
4. **No LLM Available** → Uses default actions

## Benefits

1. **Contextually Aware** - Actions are generated based on conversation context
2. **Dynamic** - Different actions for different conversation states
3. **Intelligent** - LLM understands nuanced situations
4. **Consistent** - Uses the same LLM as the main conversation
5. **Fallback Safe** - Always provides useful actions even if generation fails
6. **Performance Optimized** - Only generates actions for final responses (not tool calls)

## Integration with UI

The follow-up actions are designed to be displayed as clickable buttons or suggestions in the chat interface. When a user clicks an action, the `prompt` field should be sent as their next message to continue the conversation naturally.

## Configuration

The system uses the same LLM configuration as the main agent. No additional configuration is required - the post-model hook automatically uses the chat model to generate follow-up actions.

## Future Enhancements

Potential improvements:
- User preference learning for action types
- Action ranking based on conversation patterns
- Custom action templates for specific permit types
- Integration with external workflow systems 