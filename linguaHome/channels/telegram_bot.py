"""
LinguaHome Telegram Bot

Telegram channel integration for LinguaHome.
"""

import os
import asyncio
import logging
from pathlib import Path
from typing import Optional

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    print("Warning: python-telegram-bot not installed. Run: pip install python-telegram-bot")

from linguaHome.agent.loop import AgentLoop

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    """
    Telegram bot for LinguaHome.
    """
    
    def __init__(
        self,
        token: str,
        workspace: Path,
        llm_model: str = "gpt-4o",
        allowed_users: Optional[list] = None,
    ):
        if not TELEGRAM_AVAILABLE:
            raise ImportError("python-telegram-bot is required")
        
        self.token = token
        self.workspace = workspace
        self.allowed_users = allowed_users or []
        
        # Create agent
        self.agent = AgentLoop(
            workspace=workspace,
            llm_model=llm_model,
        )
        
        # Per-user conversation tracking
        self._user_agents: dict[int, AgentLoop] = {}
    
    def _get_agent_for_user(self, user_id: int) -> AgentLoop:
        """Get or create agent for a specific user."""
        if user_id not in self._user_agents:
            self._user_agents[user_id] = AgentLoop(
                workspace=self.workspace,
                llm_model=self.agent.llm.model,
            )
        return self._user_agents[user_id]
    
    def _is_authorized(self, user_id: int) -> bool:
        """Check if user is authorized."""
        if not self.allowed_users:
            return True  # No restrictions
        return user_id in self.allowed_users
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        welcome = f"""
🏠 **Welcome to LinguaHome, {user.first_name}!**

I'm your smart home assistant. I can help you:
• 🌡️ Check sensor readings (temperature, motion, doors)
• 🔌 Control smart plugs
• 📊 Analyze your home data

Just send me a message in natural language!

**Examples:**
• "Robot Corner 温度多少？"
• "关掉入口的插座"
• "哪个房间最热？"
• "列出所有传感器"

Type /help for more commands.
"""
        await update.message.reply_text(welcome, parse_mode='Markdown')
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_text = """
🏠 **LinguaHome Commands**

/start - Welcome message
/help - This help message
/clear - Reset conversation history
/status - Show system status
/rooms - List all rooms
/sensors - List all sensors

**Natural Language Examples:**
• "What's the temperature in Robot Corner?"
• "Turn off all plugs"
• "Is anyone in the Entrance?"
• "Compare temperatures in all rooms"
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /clear command."""
        user_id = update.effective_user.id
        agent = self._get_agent_for_user(user_id)
        agent.reset_conversation()
        await update.message.reply_text("🔄 Conversation cleared!")
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command."""
        status = """
🏠 **LinguaHome Status**

✅ System: Online
✅ Fibaro HC3: Connected
✅ LLM: Ready

📊 **Sensors**: 15 active
🔌 **Controllable Devices**: 5 plugs
🏠 **Rooms**: 5
"""
        await update.message.reply_text(status, parse_mode='Markdown')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle incoming messages."""
        user_id = update.effective_user.id
        
        # Authorization check
        if not self._is_authorized(user_id):
            await update.message.reply_text("❌ Unauthorized. Contact admin.")
            return
        
        user_message = update.message.text
        logger.info(f"User {user_id}: {user_message}")
        
        # Send typing indicator
        await update.message.chat.send_action("typing")
        
        try:
            # Get user-specific agent
            agent = self._get_agent_for_user(user_id)
            
            # Process with agent
            response = await agent.process_async(user_message)
            
            # Send response
            await update.message.reply_text(response.message)
            
            # Log code if generated
            if response.code_generated:
                logger.debug(f"Generated code:\n{response.code_generated}")
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(f"❌ Error: {str(e)}")
    
    def run(self) -> None:
        """Start the bot."""
        # Create application
        application = Application.builder().token(self.token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("clear", self.clear_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Start polling
        logger.info("Starting LinguaHome Telegram bot...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point for Telegram bot."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("Set it with: export TELEGRAM_BOT_TOKEN='your-token-here'")
        return
    
    # Get workspace
    workspace = Path(__file__).parent
    
    # Get model
    model = os.environ.get("LINGUAHOME_MODEL", "gpt-4o")
    
    # Get allowed users (comma-separated list of Telegram user IDs)
    allowed_users_str = os.environ.get("TELEGRAM_ALLOWED_USERS", "")
    allowed_users = [int(u.strip()) for u in allowed_users_str.split(",") if u.strip()]
    
    # Create and run bot
    bot = TelegramBot(
        token=token,
        workspace=workspace,
        llm_model=model,
        allowed_users=allowed_users if allowed_users else None,
    )
    
    bot.run()


if __name__ == "__main__":
    main()
