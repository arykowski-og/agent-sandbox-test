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

# Create the agent WITHOUT checkpointer (LangGraph API handles persistence)
graph = create_react_agent(
    model=model,
    tools=[],
    prompt="You are a helpful assistant."
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