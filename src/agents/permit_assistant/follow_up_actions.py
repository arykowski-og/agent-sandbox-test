"""Follow-up Actions Integration for Permit Assistant"""

import json
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from langchain_core.messages import BaseMessage

class FollowUpAction(BaseModel):
    """Schema for a follow-up action"""
    label: str  # Short action label (2-4 words)
    prompt: str  # Complete question/request the user would ask
    category: str  # permit|inspection|application|status|document|fee|compliance|general

class FollowUpActionsMetadata(BaseModel):
    """Container for follow-up actions metadata"""
    followUpActions: List[FollowUpAction]

async def extract_follow_up_actions_hook(response: Any, **kwargs) -> Any:
    """
    Post-model hook that extracts follow-up actions from the LLM response.
    This runs after the LLM generates its response but before returning to the user.
    """
    
    print(f"🔄 DEBUG: Follow-up hook called with response type: {type(response).__name__}")
    
    # Skip if this is a tool call response
    if hasattr(response, 'tool_calls') and response.tool_calls:
        print(f"🔄 DEBUG: Skipping follow-up generation for tool call response")
        return response
    
    # Get the conversation context from kwargs
    config = kwargs.get("config", {})
    messages = config.get("configurable", {}).get("messages", [])
    print(f"🔄 DEBUG: Found {len(messages)} messages in config")
    
    # Create a prompt for generating follow-up actions
    follow_up_prompt = f"""
Based on the conversation context and your previous response, suggest 4-6 relevant follow-up actions that the user might want to take next.

Previous response: {response.content}

Recent conversation:
{format_conversation_context(messages[-6:] if messages else [])}

Respond with ONLY a JSON array in this exact format:
[
  {{
    "label": "Short Action Label",
    "prompt": "Complete question or request the user would ask",
    "category": "permit|inspection|application|status|document|fee|compliance|general"
  }}
]

Focus on practical next steps that would be most helpful given the conversation context. Make the prompts specific and actionable for permit and licensing workflows.
Categories:
- permit: General permit questions and guidance
- inspection: Scheduling, preparing for, or following up on inspections
- application: Starting new applications or continuing existing ones
- status: Checking status of permits, applications, or processes
- document: Document requirements, submissions, or reviews
- fee: Payment information, fee calculations, or billing questions
- compliance: Code compliance, regulations, or requirements
- general: Other helpful actions or general assistance
"""

    try:
        # Create a separate, non-streaming LLM instance for follow-up generation
        from langchain_openai import ChatOpenAI
        
        # Use a separate LLM instance to avoid interfering with streaming
        follow_up_llm = ChatOpenAI(
            model="gpt-4o-mini",  # Use a faster, cheaper model for follow-up generation
            temperature=0.3,
            max_tokens=1000,
            # Ensure this doesn't stream
            streaming=False
        ).with_config(
            config={"tags": ["langsmith:nostream"]}  # Prevent streaming to UI
        )
        
        print(f"🔄 DEBUG: Generating follow-up actions with separate LLM instance")
        print(f"🔄 DEBUG: Follow-up prompt preview: {follow_up_prompt[:200]}...")
        
        # Use the separate LLM to generate follow-up actions
        from langchain_core.messages import HumanMessage
        follow_up_response = await follow_up_llm.ainvoke([HumanMessage(content=follow_up_prompt)])
        print(f"🔄 DEBUG: LLM response received: {follow_up_response.content[:100]}...")
        
        # Clean up the response content - remove any markdown formatting
        response_content = follow_up_response.content.strip()
        if response_content.startswith("```json"):
            response_content = response_content[7:]
        if response_content.endswith("```"):
            response_content = response_content[:-3]
        response_content = response_content.strip()
        
        print(f"🔄 DEBUG: Cleaned response content: {response_content[:200]}...")
        
        # Parse the JSON response
        actions_data = json.loads(response_content)
        print(f"🔄 DEBUG: Parsed {len(actions_data)} actions from LLM response")
        
        # Validate and create FollowUpAction objects
        follow_up_actions = []
        for i, action in enumerate(actions_data):
            print(f"🔄 DEBUG: Processing action {i}: {action}")
            if all(key in action for key in ["label", "prompt", "category"]):
                # Validate category
                valid_categories = ["permit", "inspection", "application", "status", "document", "fee", "compliance", "general"]
                if action["category"] in valid_categories:
                    follow_up_actions.append(FollowUpAction(**action))
                    print(f"🔄 DEBUG: Added valid action: {action['label']}")
                else:
                    print(f"🔄 DEBUG: Invalid category '{action['category']}' for action: {action['label']}")
            else:
                print(f"🔄 DEBUG: Missing required keys in action: {action}")
        
        # Add follow-up actions to the response additional_kwargs (LangChain's way of storing metadata)
        if not hasattr(response, 'additional_kwargs'):
            response.additional_kwargs = {}
        elif response.additional_kwargs is None:
            response.additional_kwargs = {}
        
        response.additional_kwargs['followUpActions'] = [action.dict() for action in follow_up_actions]
        print(f"🔄 DEBUG: Generated {len(follow_up_actions)} follow-up actions")
        
        # Log the final actions for debugging
        for action in follow_up_actions:
            print(f"🔄 DEBUG: Final action - Label: '{action.label}', Category: '{action.category}'")
        
    except json.JSONDecodeError as e:
        print(f"🔄 ERROR: JSON parsing error: {e}")
        print(f"🔄 ERROR: Raw response content: {response_content if 'response_content' in locals() else 'Not available'}")
        # Fallback to default actions if JSON parsing fails
        if not hasattr(response, 'additional_kwargs'):
            response.additional_kwargs = {}
        response.additional_kwargs['followUpActions'] = get_default_follow_up_actions()
    except Exception as e:
        print(f"🔄 ERROR: Error generating follow-up actions: {e}")
        import traceback
        traceback.print_exc()
        # Fallback to default actions if generation fails
        if not hasattr(response, 'additional_kwargs'):
            response.additional_kwargs = {}
        response.additional_kwargs['followUpActions'] = get_default_follow_up_actions()
    
    return response

def format_conversation_context(messages: List[BaseMessage]) -> str:
    """Format recent messages for context"""
    formatted = []
    for msg in messages:
        if hasattr(msg, 'type'):
            role = "User" if msg.type == "human" else "Assistant"
        else:
            role = "Message"
        
        content = msg.content if isinstance(msg.content, str) else str(msg.content)
        # Truncate very long messages
        if len(content) > 200:
            content = content[:200] + "..."
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
            "label": "Document Requirements",
            "prompt": "What documents do I need to submit for my permit application?",
            "category": "document"
        },
        {
            "label": "Calculate Fees",
            "prompt": "How much will my permit cost? Can you help me calculate the fees?",
            "category": "fee"
        },
        {
            "label": "Get Help",
            "prompt": "I need additional assistance with my permit questions.",
            "category": "general"
        }
    ]

def create_follow_up_hook(llm):
    """Create a follow-up hook with the LLM instance"""
    async def hook(response: Any, **kwargs) -> Any:
        # Add the LLM to the kwargs for the hook to use
        kwargs = kwargs.copy() if kwargs else {}
        if "config" not in kwargs:
            kwargs["config"] = {}
        kwargs["config"]["llm"] = llm
        return await extract_follow_up_actions_hook(response, **kwargs)
    
    return hook 