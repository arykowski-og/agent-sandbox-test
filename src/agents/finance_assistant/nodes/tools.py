"""Tools node for the finance assistant"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage

# Use absolute imports for LangGraph compatibility
from src.agents.finance_assistant.config import FINANCE_TOOL_PROMPT, get_settings
from src.agents.finance_assistant.types import FinanceState

# Initialize the tool model
settings = get_settings()
tool_model = ChatOpenAI(
    model=settings.tool_model_name,
    temperature=settings.tool_temperature
)

async def tool_node(state: FinanceState, tools):
    """Tool Node: Uses o4-mini for GraphQL queries and data retrieval"""
    print(f"🔧 DEBUG: tool_node called with {len(state['messages'])} messages")
    
    messages = state["messages"]
    last_message = messages[-1]
    
    try:
        # Execute the tool calls if they exist
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            tool_messages = []
            
            for tool_call in last_message.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_call_id = tool_call["id"]
                
                print(f"🔧 DEBUG: Executing tool: {tool_name} with args: {tool_args}")
                
                # Find the matching tool
                matching_tool = None
                for tool in tools:
                    if hasattr(tool, 'name') and tool.name == tool_name:
                        matching_tool = tool
                        break
                
                if matching_tool:
                    try:
                        result = await matching_tool.ainvoke(tool_args)
                        print(f"🔧 DEBUG: Tool {tool_name} executed successfully")
                        tool_messages.append(
                            ToolMessage(
                                content=str(result),
                                tool_call_id=tool_call_id
                            )
                        )
                    except Exception as e:
                        print(f"🔧 DEBUG: Tool {tool_name} execution failed: {str(e)}")
                        tool_messages.append(
                            ToolMessage(
                                content=f"Error executing {tool_name}: {str(e)}",
                                tool_call_id=tool_call_id
                            )
                        )
                else:
                    print(f"🔧 DEBUG: Tool {tool_name} not found")
                    tool_messages.append(
                        ToolMessage(
                            content=f"Tool {tool_name} not found",
                            tool_call_id=tool_call_id
                        )
                    )
            
            return {"messages": tool_messages}
        else:
            print(f"🔧 DEBUG: No tool calls found in the last message")
            return {"messages": [AIMessage(content="No tool calls found in the last message.")]}
            
    except Exception as e:
        print(f"🔧 DEBUG: Error in tool execution: {str(e)}")
        error_message = AIMessage(content=f"Error in tool execution: {str(e)}")
        return {"messages": [error_message]} 