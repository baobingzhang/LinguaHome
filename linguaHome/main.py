#!/usr/bin/env python3
"""
LinguaHome Main Entry Point

Supports:
- Interactive CLI mode
- Single query mode
- Test mode
"""

import sys
import os
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from linguaHome.agent.loop import AgentLoop


def run_interactive(agent: AgentLoop):
    """
    Run in interactive mode.
    """
    print("\n" + "=" * 60)
    print("🏠 LinguaHome - Interactive Mode")
    print("=" * 60)
    print("Type your commands in natural language.")
    print("Type 'quit' or 'exit' to exit.")
    print("Type 'clear' to reset conversation.")
    print("=" * 60 + "\n")
    
    while True:
        try:
            user_input = input("👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("\n👋 Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                agent.reset_conversation()
                print("🔄 Conversation cleared.\n")
                continue
            
            # Process the message
            response = agent.process(user_input)
            
            print(f"\n🤖 LinguaHome: {response.message}")
            
            if response.code_generated:
                print(f"\n💻 [Code executed: {'✅' if response.code_executed else '❌'}]\n")
            else:
                print()
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except EOFError:
            print("\n\n👋 Goodbye!")
            break


def run_single_query(agent: AgentLoop, query: str):
    """
    Run a single query.
    """
    print(f"👤 Query: {query}")
    response = agent.process(query)
    print(f"🤖 Response: {response.message}")
    return response.success


def run_test_mode(agent: AgentLoop):
    """
    Run in test mode with sample queries.
    """
    print("\n" + "=" * 60)
    print("🧪 LinguaHome - Test Mode")
    print("=" * 60 + "\n")
    
    test_queries = [
        "Robot Corner 温度多少？",
        "哪个房间最热？",
        "关掉入口的插座",
        "列出所有传感器",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n--- Test {i}: {query} ---")
        response = agent.process(query)
        print(f"Response: {response.message[:200]}...")
        print(f"Success: {'✅' if response.success else '❌'}")
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="LinguaHome - Language-Driven Smart Home Automation"
    )
    parser.add_argument(
        'query',
        nargs='*',
        help='Single query to process (optional)'
    )
    parser.add_argument(
        '-t', '--test',
        action='store_true',
        help='Run in test mode'
    )
    parser.add_argument(
        '-m', '--model',
        default=os.environ.get('LINGUAHOME_MODEL', 'gpt-4o'),
        help='LLM model to use (default: gpt-4o)'
    )
    
    args = parser.parse_args()
    
    # Create agent
    workspace = Path(__file__).parent
    
    try:
        agent = AgentLoop(
            workspace=workspace,
            llm_model=args.model,
        )
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        print("\nMake sure you have set the required API key:")
        print("  export OPENAI_API_KEY='your-key'        # For GPT models")
        print("  export ANTHROPIC_API_KEY='your-key'     # For Claude models")
        print("  export GEMINI_API_KEY='your-key'        # For Gemini models")
        return 1
    
    # Run appropriate mode
    if args.test:
        run_test_mode(agent)
    elif args.query:
        query = ' '.join(args.query)
        success = run_single_query(agent, query)
        return 0 if success else 1
    else:
        run_interactive(agent)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
