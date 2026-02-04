#!/usr/bin/env python3
"""
LinguaHome Telegram Bot

Telegram integration for natural language smart home control.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, Set

# Telegram bot library
try:
    from telegram import Update
    from telegram.ext import (
        Application,
        CommandHandler,
        MessageHandler,
        ContextTypes,
        filters,
    )
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

# LinguaHome components
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from agent.loop import AgentLoop


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Telegram bot for LinguaHome.
    
    Wraps the AgentLoop and provides Telegram-specific handling.
    """
    
    def __init__(
        self,
        token: str,
        workspace: Path = None,
        llm_model: str = "gpt-4o",
        allowed_users: Set[int] = None,
    ):
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot not installed. Run: pip install python-telegram-bot")
        
        self.token = token
        self.workspace = workspace or Path.cwd()
        self.llm_model = llm_model
        self.allowed_users = allowed_users or set()
        
        # Agent per user to maintain separate conversations
        self.agents: dict[int, AgentLoop] = {}
        
        # Build application
        self.app = Application.builder().token(token).build()
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register bot command and message handlers."""
        self.app.add_handler(CommandHandler("start", self._start_command))
        self.app.add_handler(CommandHandler("help", self._help_command))
        self.app.add_handler(CommandHandler("clear", self._clear_command))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
    
    def _is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized."""
        if not self.allowed_users:
            return True  # No restrictions
        return user_id in self.allowed_users
    
    def _get_agent(self, user_id: int) -> AgentLoop:
        """Get or create agent for user."""
        if user_id not in self.agents:
            self.agents[user_id] = AgentLoop(
                workspace=self.workspace,
                llm_model=self.llm_model,
            )
        return self.agents[user_id]
    
    async def _start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user_id = update.effective_user.id
        
        if not self._is_authorized(user_id):
            await update.message.reply_text("X Unauthorized. Contact the administrator.")
            return
        
        welcome = (
            "welcome LinguaHome Smart Home Assistant\n\n"
            "I can help you control your smart home using natural language.\n\n"
            "Examples:\n"
            "speech balloon 'What's the temperature in Robot Corner?'\n"
            "speech balloon 'Turn off the plug in Entrance'\n"
            "speech balloon 'Which room is warmest?'\n\n"
            "Commands:\n"
            "/help - Show this message\n"
            "/clear - Reset conversation"
        )
        await update.message.reply_text(welcome)
    
    async def _help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_text = (
            "LinguaHome Commands\n\n"
            "/start - Welcome message\n"
            "/help - Show this help\n"
            "/clear - Clear conversation history\n\n"
            "Just send me natural language messages to:\n"
            "bullet Query sensors (temperature, motion, doors)\n"
            "bullet Control devices (turn on/off plugs)\n"
            "bullet Get smart home insights"
        )
        await update.message.reply_text(help_text)
    
    async def _clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /clear command."""
        user_id = update.effective_user.id
        
        if user_id in self.agents:
            self.agents[user_id].reset_conversation()
        
        await update.message.reply_text("recycle Conversation cleared. Start fresh!")
    
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular text messages."""
        user_id = update.effective_user.id
        
        if not self._is_authorized(user_id):
            await update.message.reply_text("X Unauthorized.")
            return
        
        user_message = update.message.text
        logger.info(f"User {user_id}: {user_message}")
        
        # Show typing indicator
        await update.message.chat.send_action("typing")
        
        try:
            # Get agent and process
            agent = self._get_agent(user_id)
            response = await agent.process_async(user_message)
            
            # Send response
            await update.message.reply_text(response.message)
            
            logger.info(f"Response sent: {response.message[:50]}...")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(f"X Error: {str(e)}")
    
    def run(self) -> None:
        """Run the bot."""
        logger.info("Starting LinguaHome Telegram Bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("X TELEGRAM_BOT_TOKEN environment variable not set")
        return
    
    # Parse allowed users
    allowed_users_str = os.environ.get("TELEGRAM_ALLOWED_USERS", "")
    allowed_users = set()
    if allowed_users_str:
        allowed_users = {int(uid.strip()) for uid in allowed_users_str.split(",")}
    
    workspace = Path(__file__).parent.parent
    model = os.environ.get("LINGUAHOME_MODEL", "gpt-4o")
    
    bot = TelegramBot(
        token=token,
        workspace=workspace,
        llm_model=model,
        allowed_users=allowed_users,
    )
    
    print(f"robot LinguaHome Telegram Bot starting...")
    print(f"Model: {model}")
    if allowed_users:
        print(f"Allowed users: {allowed_users}")
    
    bot.run()


if __name__ == "__main__":
    main()
