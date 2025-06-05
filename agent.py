import os
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.chat_models import init_chat_model

# Load environment variables
load_dotenv()

# Create an in-memory checkpointer for persistence
checkpointer = InMemorySaver()

# Check if API key is available
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables.")
    print("Please create a .env file with your OpenAI API key.")
    print("See env.example for the required format.")

# Initialize the model with temperature configuration
model = init_chat_model(
    "openai:gpt-3.5-turbo",  # Using OpenAI GPT-3.5-turbo
    temperature=0
)

# Create the agent with memory and tools
agent = create_react_agent(
    model=model,
    tools=[],
    prompt="You are a helpful assistant.",
    checkpointer=checkpointer
)

def extract_final_message(response):
    """Extract the final message content from the agent response."""
    if 'messages' in response and response['messages']:
        final_message = response['messages'][-1]
        if hasattr(final_message, 'content'):
            return final_message.content
        elif isinstance(final_message, dict) and 'content' in final_message:
            return final_message['content']
        else:
            return str(final_message)
    return str(response)

def main():
    """Main function to demonstrate the agent."""
    if not api_key:
        print("Cannot start agent without API key. Please set OPENAI_API_KEY in your .env file.")
        return
    
    print("LangGraph Agent is running...")
    print("=" * 50)
    
    # Configuration for the conversation thread
    config = {"configurable": {"thread_id": "1"}}
    
    # First query
    print("User: Hello, how are you?")
    try:
        response1 = agent.invoke(
            {"messages": [{"role": "user", "content": "Hello, how are you?"}]},
            config
        )
        print(f"Agent: {extract_final_message(response1)}")
        print("-" * 30)
        
        # Follow-up query (should remember context)
        print("User: What can you help me with?")
        response2 = agent.invoke(
            {"messages": [{"role": "user", "content": "What can you help me with?"}]},
            config
        )
        print(f"Agent: {extract_final_message(response2)}")
        print("-" * 30)
        
        # Interactive mode
        print("\nEntering interactive mode. Type 'quit' to exit.")
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            try:
                response = agent.invoke(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config
                )
                print(f"Agent: {extract_final_message(response)}")
            except Exception as e:
                print(f"Error: {e}")
    except Exception as e:
        print(f"Failed to start agent: {e}")
        print("Make sure your OPENAI_API_KEY is correct and you have sufficient credits.")

if __name__ == "__main__":
    main() 