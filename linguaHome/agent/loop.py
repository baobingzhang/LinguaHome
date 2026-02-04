"""
LinguaHome Agent Loop

Core processing engine: User Message -> LLM -> Code -> Execute -> Response
"""

import asyncio
from pathlib import Path
from typing import Optional, Callable, Awaitable
from dataclasses import dataclass

from .memory import MemoryStore
from .context import ContextBuilder
from .code_executor import CodeExecutor
from .llm_provider import LLMProvider, Message, LLMResponse


@dataclass
class AgentResponse:
    """Agent response to user."""
    message: str
    code_generated: Optional[str] = None
    code_executed: bool = False
    success: bool = True


class AgentLoop:
    """
    LinguaHome Agent Loop.
    
    Processes user messages through:
    1. Context building (System Prompt + Memory)
    2. LLM code generation
    3. Code extraction and validation
    4. Safe code execution
    5. Response formatting
    """
    
    def __init__(
        self,
        workspace: Path,
        llm_model: str = "gpt-4o",
        temperature: float = 0.1,
        code_timeout: int = 30,
        safe_mode: bool = True,
    ):
        self.workspace = workspace
        
        # Initialize components
        self.memory = MemoryStore(workspace)
        self.context = ContextBuilder(self.memory)
        self.executor = CodeExecutor(timeout=code_timeout, safe_mode=safe_mode)
        self.llm = LLMProvider(model=llm_model, temperature=temperature)
        
        # History for context
        self.conversation_history: list[Message] = []
        self.max_history = 10
    
    def reset_conversation(self) -> None:
        """Reset conversation history."""
        self.conversation_history = []
    
    def process(self, user_message: str) -> AgentResponse:
        """
        Process a user message synchronously.
        
        Args:
            user_message: The user's natural language request
            
        Returns:
            AgentResponse with the result
        """
        try:
            # Build messages
            messages = self._build_messages(user_message)
            
            # Get LLM response
            llm_response = self.llm.chat(messages)
            
            # Extract code from response
            code = self.executor.extract_code_from_response(llm_response.content)
            
            if code:
                # Execute the code
                success, stdout, stderr = self.executor.execute(code)
                
                if success and stdout:
                    # Code executed successfully
                    response_text = stdout.strip()
                    
                    # Remember this interaction
                    self.memory.remember_user_command(user_message, response_text[:100])
                    
                    return AgentResponse(
                        message=response_text,
                        code_generated=code,
                        code_executed=True,
                        success=True,
                    )
                elif not success:
                    # Execution failed
                    error_msg = f"❌ Code execution failed:\n{stderr[:500]}"
                    return AgentResponse(
                        message=error_msg,
                        code_generated=code,
                        code_executed=False,
                        success=False,
                    )
                else:
                    # No output
                    return AgentResponse(
                        message="✅ Command executed (no output)",
                        code_generated=code,
                        code_executed=True,
                        success=True,
                    )
            else:
                # No code generated - direct text response
                return AgentResponse(
                    message=llm_response.content,
                    code_generated=None,
                    code_executed=False,
                    success=True,
                )
                
        except Exception as e:
            return AgentResponse(
                message=f"❌ Error: {str(e)}",
                success=False,
            )
    
    async def process_async(self, user_message: str) -> AgentResponse:
        """
        Process a user message asynchronously.
        """
        try:
            # Build messages
            messages = self._build_messages(user_message)
            
            # Get LLM response
            llm_response = await self.llm.chat_async(messages)
            
            # Extract and execute code
            code = self.executor.extract_code_from_response(llm_response.content)
            
            if code:
                success, stdout, stderr = self.executor.execute(code)
                
                if success and stdout:
                    self.memory.remember_user_command(user_message, stdout[:100])
                    return AgentResponse(
                        message=stdout.strip(),
                        code_generated=code,
                        code_executed=True,
                        success=True,
                    )
                elif not success:
                    return AgentResponse(
                        message=f"❌ Execution failed:\n{stderr[:500]}",
                        code_generated=code,
                        code_executed=False,
                        success=False,
                    )
                else:
                    return AgentResponse(
                        message="✅ Command executed",
                        code_generated=code,
                        code_executed=True,
                        success=True,
                    )
            else:
                return AgentResponse(
                    message=llm_response.content,
                    success=True,
                )
                
        except Exception as e:
            return AgentResponse(
                message=f"❌ Error: {str(e)}",
                success=False,
            )
    
    def _build_messages(self, user_message: str) -> list[Message]:
        """Build the message list for LLM."""
        messages = [
            Message(role="system", content=self.context.build_system_prompt())
        ]
        
        # Add conversation history (limited)
        messages.extend(self.conversation_history[-self.max_history:])
        
        # Add current user message
        user_prompt = self.context.build_user_prompt(user_message)
        messages.append(Message(role="user", content=user_prompt))
        
        # Update history
        self.conversation_history.append(Message(role="user", content=user_message))
        
        return messages


# Convenience function
def create_agent(
    workspace: Path = None,
    model: str = None,
) -> AgentLoop:
    """Create an agent with default settings."""
    import os
    workspace = workspace or Path.cwd()
    model = model or os.environ.get("LINGUAHOME_MODEL", "gpt-4o")
    return AgentLoop(workspace=workspace, llm_model=model)


if __name__ == "__main__":
    # Interactive test
    import sys
    
    print("🏠 LinguaHome Agent Test")
    print("=" * 50)
    
    agent = create_agent(workspace=Path.cwd())
    
    test_queries = [
        "What's the temperature in Robot Corner?",
        "List all rooms and their sensors",
        "Turn off the plug in Entrance",
    ]
    
    if len(sys.argv) > 1:
        # Use command line argument
        query = " ".join(sys.argv[1:])
        print(f"\nQuery: {query}")
        response = agent.process(query)
        print(f"\nResponse:\n{response.message}")
        if response.code_generated:
            print(f"\nGenerated Code:\n{response.code_generated}")
    else:
        # Run test queries
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            print("-" * 40)
            response = agent.process(query)
            print(f"Response: {response.message[:200]}...")
            print(f"Code executed: {response.code_executed}")
            print()
