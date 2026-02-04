#!/usr/bin/env python3
"""
LinguaHome - Language-Driven Smart Home Automation

Main entry point for CLI and testing.
"""

import os
import sys
import argparse
from pathlib import Path


def interactive_mode(agent):
    """Run interactive CLI mode."""
    print("=" * 60)
    print("🏠 LinguaHome - Smart Home Assistant")
    print("=" * 60)
    print("Commands: 'quit' to exit, 'clear' to reset conversation")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ('quit', 'exit', 'q'):
                print("👋 Goodbye!")
                break
            
            if user_input.lower() == 'clear':
                agent.reset_conversation()
                print("🔄 Conversation cleared.")
                continue
            
            # Process the request
            print("\n⏳ Processing...")
            response = agent.process(user_input)
            
            print("\n🤖 LinguaHome:")
            print(response.message)
            
            if response.code_generated and os.environ.get('LINGUAHOME_DEBUG'):
                print("\n📝 Generated Code:")
                print("-" * 40)
                print(response.code_generated)
                print("-" * 40)
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


def single_query(agent, query: str, show_code: bool = False):
    """Process a single query."""
    response = agent.process(query)
    print(response.message)
    
    if show_code and response.code_generated:
        print("\n--- Generated Code ---")
        print(response.code_generated)
    
    return response.success


def main():
    parser = argparse.ArgumentParser(
        description="LinguaHome - Language-Driven Smart Home Automation"
    )
    parser.add_argument(
        "query",
        nargs="*",
        help="Query to process (interactive mode if empty)"
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("LINGUAHOME_MODEL", "gpt-4o"),
        help="LLM model to use (default: gpt-4o)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show generated code"
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run test queries"
    )
    
    args = parser.parse_args()
    
    # Set debug mode
    if args.debug:
        os.environ['LINGUAHOME_DEBUG'] = '1'
    
    # Import here to avoid circular imports
    from agent.loop import AgentLoop
    
    # Create agent
    workspace = Path(__file__).parent
    agent = AgentLoop(
        workspace=workspace,
        llm_model=args.model,
    )
    
    if args.test:
        # Run test queries
        test_queries = [
            "What's the temperature in Robot Corner?",
            "List all rooms",
            "Which room is the warmest?",
        ]
        print("🧪 Running test queries...\n")
        for query in test_queries:
            print(f"📝 Query: {query}")
            single_query(agent, query, show_code=args.debug)
            print()
    elif args.query:
        # Single query mode
        query = " ".join(args.query)
        single_query(agent, query, show_code=args.debug)
    else:
        # Interactive mode
        interactive_mode(agent)


if __name__ == "__main__":
    main()
