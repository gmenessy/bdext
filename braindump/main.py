# 🧠 BrainDump (v3) - Interactive Pilot CLI
import os
import sys
from brain_vfs import BrainVFS
from retriever import BrainRetriever
from tool_router import ToolRouter
from agent_runtime import AgentRuntime
from dream_engine import DreamEngine
from decision_memory import DecisionMemory
from entity_resolver import EntityResolver
from policy_engine import PolicyEngine
from llm_client import LLMClient

def setup_llm():
    """Interactive setup for the pilot session if environment variables are missing."""
    provider = os.getenv("BRAINDUMP_LLM_PROVIDER")
    api_key = os.getenv("BRAINDUMP_API_KEY")
    
    if not provider:
        print("\n⚙️  Configure LLM Provider:")
        print(" [1] Mock (No API key needed)")
        print(" [2] OpenAI (requires API Key)")
        print(" [3] OpenAI-Compatible (Ollama, Groq, etc.)")
        print(" [4] Google Gemini (requires API Key)")
        
        choice = input("Select [1-4]: ").strip()
        if choice == "2": provider = "openai"
        elif choice == "3": 
            provider = "openai-compatible"
            os.environ["BRAINDUMP_LLM_BASE_URL"] = input("Base URL (e.g. http://localhost:11434/v1): ").strip()
            os.environ["BRAINDUMP_LLM_MODEL"] = input("Model name (e.g. llama3): ").strip()
        elif choice == "4": provider = "gemini"
        else: provider = "mock"
        
        os.environ["BRAINDUMP_LLM_PROVIDER"] = provider
        
    if provider in ["openai", "gemini", "openai-compatible"] and not api_key:
        api_key = input(f"🔑 Enter API Key for {provider}: ").strip()
        os.environ["BRAINDUMP_API_KEY"] = api_key
    
    return LLMClient()

def main():
    print("🧠 BrainDump (v3) - Cognitive Memory System")
    print("------------------------------------------")
    
    # 1. Initialization
    root_dir = "data"
    os.makedirs(root_dir, exist_ok=True)
    
    # Setup LLM Client (Interactive)
    llm_client = setup_llm()
    
    from vector_service import VectorService
    vector_service = VectorService(os.path.join(root_dir, "vector_index.json"))
...
    
    agent = AgentRuntime(
        retriever, vfs, tool_router, 
        policy_engine=policy_engine, 
        decision_memory=decision_memory,
        dream_engine=dream_engine
    )
    
    # 2. Command Loop
    while True:
        try:
            user_input = input("\n👤 > ").strip()
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("🧠 Goodbye. Memory persisted.")
                break
                
            if not user_input:
                continue
                
            if user_input.startswith("/"):
                # Handle Meta Commands
                cmd = user_input[1:].split()[0]
                if cmd == "wiki":
                    print(f"📚 Wiki Search: {user_input[5:]}")
                    ctx = retriever.retrieve(user_input[5:])
                    for entry in ctx.wiki:
                        print(f" - [{entry['id']}] {entry['summary']}")
                elif cmd == "dream":
                    print("🌙 Triggering Nightdream (Consolidation)...")
                    result = dream_engine.run_nightdream()
                    print(f" ✅ {result['merged']} entries merged.")
                continue

            # 3. Agent Execution Loop
            print("🤖 Processing Task...")
            result = agent.run_task(user_input)
            
            print(f"🤖 Output: {result.get('output', 'No response')}")
            print(f"🔧 Tool Used: {result.get('tool', 'None')}")
            
        except KeyboardInterrupt:
            print("\n🧠 Goodbye.")
            break
        except Exception as e:
            print(f"⚠️ Error: {e}")

if __name__ == "__main__":
    main()
