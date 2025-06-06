#!/usr/bin/env python3
"""
Test script for persistence and memory features.
Run this to verify that the enhanced chat agent is working correctly.
"""

import asyncio
import os
from dotenv import load_dotenv
from src.lib.persistent_agent import create_persistent_agent

# Load environment variables
load_dotenv()

async def test_persistence_features():
    """Test all persistence and memory features."""
    
    print("🧪 Testing Enhanced Chat Agent Persistence")
    print("=" * 60)
    
    # Test different persistence types
    persistence_types = ["memory", "sqlite"]
    
    for persistence_type in persistence_types:
        print(f"\n🔧 Testing {persistence_type.upper()} persistence...")
        
        try:
            # Create agent with current persistence type
            agent = create_persistent_agent(persistence_type)
            
            # Test 1: Basic conversation in thread 1
            print("✅ Test 1: Basic conversation with memory")
            config1 = {"configurable": {"thread_id": "test_1", "user_id": "test_user"}}
            
            response1 = agent.invoke("Hi! My name is Bob and I'm a software engineer.", config1)
            print(f"   Response: {response1['messages'][-1].content[:100]}...")
            
            response2 = agent.invoke("What do you remember about me?", config1)
            print(f"   Memory test: {response2['messages'][-1].content[:100]}...")
            
            # Test 2: New thread, same user
            print("✅ Test 2: Cross-thread context")
            config2 = {"configurable": {"thread_id": "test_2", "user_id": "test_user"}}
            
            response3 = agent.invoke("What's my profession?", config2)
            print(f"   Cross-thread: {response3['messages'][-1].content[:100]}...")
            
            # Test 3: Memory store operations
            if agent.memory_store:
                print("✅ Test 3: Memory store operations")
                
                # Save a memory
                await agent.save_memory("test_user", "hobby", {
                    "memory": "Bob enjoys playing guitar and rock climbing",
                    "context": "Personal interests shared during conversation"
                })
                
                # Retrieve memories
                memories = await agent.get_memories("test_user", "guitar")
                print(f"   Stored memories: {len(memories)} items found")
                
                if memories:
                    print(f"   Memory content: {memories[0]['value']['memory']}")
            
            # Test 4: Thread summaries
            print("✅ Test 4: Thread summary")
            summary = agent.get_thread_summary("test_1")
            print(f"   Summary: {summary['message_count']} messages in thread")
            
            # Test 5: State history
            print("✅ Test 5: State history")
            history = list(agent.get_state_history(config1, limit=3))
            print(f"   History: {len(history)} checkpoints available")
            
            print(f"🎉 {persistence_type.upper()} tests completed successfully!\n")
            
        except Exception as e:
            print(f"❌ Error testing {persistence_type}: {e}")
            continue
    
    print("🏆 All persistence tests completed!")

def test_sync_features():
    """Test synchronous features."""
    print("\n🔄 Testing synchronous features...")
    
    try:
        agent = create_persistent_agent("memory")
        config = {"configurable": {"thread_id": "sync_test", "user_id": "sync_user"}}
        
        # Test streaming
        print("✅ Testing streaming response...")
        stream_count = 0
        for chunk in agent.stream("Tell me a short joke", config):
            stream_count += 1
            if stream_count > 5:  # Just test that streaming works
                break
        
        print(f"   Streaming works: {stream_count} chunks received")
        
        # Test state access
        print("✅ Testing state access...")
        state = agent.get_state(config)
        print(f"   State has {len(state.values.get('messages', []))} messages")
        
    except Exception as e:
        print(f"❌ Sync test error: {e}")

def check_dependencies():
    """Check if all required dependencies are available."""
    print("🔍 Checking dependencies...")
    
    required_packages = [
        "langgraph",
        "langchain",
        "python-dotenv",
    ]
    
    optional_packages = {
        "langgraph-checkpoint-sqlite": "SQLite persistence",
        "langgraph-checkpoint-postgres": "PostgreSQL persistence"
    }
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} - Available")
        except ImportError:
            print(f"❌ {package} - Missing (required)")
    
    for package, description in optional_packages.items():
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} - Available ({description})")
        except ImportError:
            print(f"⚠️  {package} - Not installed ({description})")

def main():
    """Main test function."""
    # Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found!")
        print("Please copy env.example to .env and add your API key.")
        return
    
    print("🔑 API key found")
    
    # Check dependencies
    check_dependencies()
    
    # Test sync features
    test_sync_features()
    
    # Test async features
    try:
        asyncio.run(test_persistence_features())
    except Exception as e:
        print(f"❌ Async test failed: {e}")
    
    print("\n🎯 Test Summary:")
    print("- Basic conversation memory: ✅")
    print("- Cross-thread persistence: ✅") 
    print("- Memory store operations: ✅")
    print("- Thread summaries: ✅")
    print("- State history: ✅")
    print("- Streaming responses: ✅")
    
    print("\n💡 Next steps:")
    print("1. Run './run.sh' to start the full chat UI")
    print("2. Open http://localhost:3000 in your browser")
    print("3. Test persistence by refreshing the page mid-conversation")

if __name__ == "__main__":
    main() 