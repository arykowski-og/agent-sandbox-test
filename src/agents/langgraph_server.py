import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langgraph.utils.config import RunnableConfig
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
# Load environment variables
load_dotenv()

# Check if API key is available
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables.")
    print("Please create a .env file with your OpenAI API key.")
    print("See env.example for the required format.")

# Initialize the model with temperature configuration
model = init_chat_model(
    "openai:gpt-3.5-turbo",
    temperature=0
)

# Enhanced prompt with memory capabilities
enhanced_prompt = """You are a helpful AI assistant with persistent memory capabilities.

Key features:
- You can remember our conversation history within this thread
- You can maintain context across multiple messages
- You provide helpful, accurate, and contextual responses
- You can reference previous parts of our conversation when relevant

Always be helpful, informative, and maintain a friendly conversational tone."""

# Create the agent WITHOUT checkpointer AND without custom store
# When using LangGraph API, persistence is handled automatically by the platform
# The store configuration in langgraph.json will be used instead
graph = create_react_agent(
    model=model,
    tools=[],
    prompt=enhanced_prompt
)

if __name__ == "__main__":
    # For testing the server locally
    print("LangGraph Server Agent is ready!")
    print("Use 'langgraph dev' to start the development server")
    
    # Test the agent
    config = {"configurable": {"thread_id": "test"}}
    result = graph.invoke(
        {"messages": [{"role": "user", "content": "Hello, how are you?"}]},
        config
    )
    print("Test result:", result) 