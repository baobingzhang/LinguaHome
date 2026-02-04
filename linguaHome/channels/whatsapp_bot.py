"""
LinguaHome WhatsApp Bot

WhatsApp channel integration using Twilio API.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from flask import Flask, request

try:
    from twilio.twiml.messaging_response import MessagingResponse
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("Warning: twilio not installed. Run: pip install twilio flask")

from linguaHome.agent.loop import AgentLoop

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class WhatsAppBot:
    """
    WhatsApp bot for LinguaHome using Twilio.
    """
    
    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        whatsapp_number: str,
        workspace: Path,
        llm_model: str = "gpt-4o",
        allowed_numbers: Optional[list] = None,
    ):
        if not TWILIO_AVAILABLE:
            raise ImportError("twilio and flask are required")
        
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.whatsapp_number = whatsapp_number  # Format: whatsapp:+14155238886
        self.workspace = workspace
        self.allowed_numbers = allowed_numbers or []
        
        # Twilio client for sending messages
        self.twilio_client = TwilioClient(account_sid, auth_token)
        
        # Create agent
        self.agent = AgentLoop(
            workspace=workspace,
            llm_model=llm_model,
        )
        
        # Per-user agents
        self._user_agents: dict[str, AgentLoop] = {}
        
        # Flask app
        self.app = Flask(__name__)
        self._setup_routes()
    
    def _get_agent_for_user(self, phone_number: str) -> AgentLoop:
        """Get or create agent for a specific user."""
        if phone_number not in self._user_agents:
            self._user_agents[phone_number] = AgentLoop(
                workspace=self.workspace,
                llm_model=self.agent.llm.model,
            )
        return self._user_agents[phone_number]
    
    def _is_authorized(self, phone_number: str) -> bool:
        """Check if phone number is authorized."""
        if not self.allowed_numbers:
            return True  # No restrictions
        return phone_number in self.allowed_numbers
    
    def _setup_routes(self):
        """Setup Flask routes."""
        
        @self.app.route('/webhook', methods=['POST'])
        def webhook():
            """Handle incoming WhatsApp messages."""
            # Get message details
            from_number = request.form.get('From', '')
            message_body = request.form.get('Body', '').strip()
            
            logger.info(f"Received from {from_number}: {message_body}")
            
            # Create response
            resp = MessagingResponse()
            
            # Authorization check
            if not self._is_authorized(from_number):
                resp.message("❌ Unauthorized. Contact admin.")
                return str(resp)
            
            # Handle commands
            if message_body.lower() == '/start':
                welcome = """🏠 *Welcome to LinguaHome!*

I'm your smart home assistant. I can help you:
• 🌡️ Check sensor readings
• 🔌 Control smart plugs
• 📊 Analyze your home data

Just send me a message in natural language!

*Examples:*
• "Robot Corner 温度多少？"
• "关掉入口的插座"
• "哪个房间最热？"
"""
                resp.message(welcome)
                return str(resp)
            
            if message_body.lower() == '/clear':
                agent = self._get_agent_for_user(from_number)
                agent.reset_conversation()
                resp.message("🔄 Conversation cleared!")
                return str(resp)
            
            # Process with agent
            try:
                agent = self._get_agent_for_user(from_number)
                response = agent.process(message_body)
                resp.message(response.message)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                resp.message(f"❌ Error: {str(e)}")
            
            return str(resp)
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return {"status": "ok", "service": "LinguaHome WhatsApp"}
    
    def send_message(self, to_number: str, message: str) -> bool:
        """
        Send a message to a WhatsApp number.
        
        Args:
            to_number: WhatsApp number (format: whatsapp:+1234567890)
            message: Message text
            
        Returns:
            Success status
        """
        try:
            self.twilio_client.messages.create(
                body=message,
                from_=self.whatsapp_number,
                to=to_number
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False
    
    def run(self, host: str = '0.0.0.0', port: int = 5000, debug: bool = False):
        """Start the Flask server."""
        logger.info(f"Starting LinguaHome WhatsApp bot on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Main entry point for WhatsApp bot."""
    # Required environment variables
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    whatsapp_number = os.environ.get("TWILIO_WHATSAPP_NUMBER")  # e.g., whatsapp:+14155238886
    
    if not all([account_sid, auth_token, whatsapp_number]):
        print("Error: Missing Twilio configuration.")
        print("Required environment variables:")
        print("  TWILIO_ACCOUNT_SID - Your Twilio Account SID")
        print("  TWILIO_AUTH_TOKEN - Your Twilio Auth Token")
        print("  TWILIO_WHATSAPP_NUMBER - Your Twilio WhatsApp number (format: whatsapp:+14155238886)")
        print("\nOptional:")
        print("  WHATSAPP_ALLOWED_NUMBERS - Comma-separated list of allowed phone numbers")
        print("  LINGUAHOME_MODEL - LLM model to use (default: gpt-4o)")
        return
    
    # Get workspace
    workspace = Path(__file__).parent.parent
    
    # Get model
    model = os.environ.get("LINGUAHOME_MODEL", "gpt-4o")
    
    # Get allowed numbers
    allowed_numbers_str = os.environ.get("WHATSAPP_ALLOWED_NUMBERS", "")
    allowed_numbers = [n.strip() for n in allowed_numbers_str.split(",") if n.strip()]
    
    # Create and run bot
    bot = WhatsAppBot(
        account_sid=account_sid,
        auth_token=auth_token,
        whatsapp_number=whatsapp_number,
        workspace=workspace,
        llm_model=model,
        allowed_numbers=allowed_numbers if allowed_numbers else None,
    )
    
    # Get port from environment (for deployment)
    port = int(os.environ.get("PORT", 5000))
    
    bot.run(port=port)


if __name__ == "__main__":
    main()
