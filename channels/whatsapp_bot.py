#!/usr/bin/env python3
"""
LinguaHome WhatsApp Bot

WhatsApp integration using Twilio API.
"""

import os
import logging
from pathlib import Path
from typing import Set

# Flask for webhook
try:
    from flask import Flask, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

# Twilio
try:
    from twilio.rest import Client
    from twilio.twiml.messaging_response import MessagingResponse
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

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


class WhatsAppBot:
    """
    WhatsApp bot for LinguaHome using Twilio.
    
    Provides a Flask webhook to receive WhatsApp messages.
    """
    
    def __init__(
        self,
        account_sid: str = None,
        auth_token: str = None,
        whatsapp_number: str = None,
        workspace: Path = None,
        llm_model: str = "gpt-4o",
        allowed_numbers: Set[str] = None,
    ):
        if not FLASK_AVAILABLE:
            raise ImportError("Flask not installed. Run: pip install flask")
        if not TWILIO_AVAILABLE:
            raise ImportError("Twilio not installed. Run: pip install twilio")
        
        # Twilio credentials
        self.account_sid = account_sid or os.environ.get("TWILIO_ACCOUNT_SID")
        self.auth_token = auth_token or os.environ.get("TWILIO_AUTH_TOKEN")
        self.whatsapp_number = whatsapp_number or os.environ.get("TWILIO_WHATSAPP_NUMBER")
        
        if not all([self.account_sid, self.auth_token, self.whatsapp_number]):
            raise ValueError(
                "Missing Twilio credentials. Set TWILIO_ACCOUNT_SID, "
                "TWILIO_AUTH_TOKEN, and TWILIO_WHATSAPP_NUMBER environment variables."
            )
        
        self.workspace = workspace or Path.cwd()
        self.llm_model = llm_model
        self.allowed_numbers = allowed_numbers or set()
        
        # Twilio client
        self.client = Client(self.account_sid, self.auth_token)
        
        # Agent per user phone number
        self.agents: dict[str, AgentLoop] = {}
        
        # Flask app
        self.app = Flask(__name__)
        self._register_routes()
    
    def _register_routes(self) -> None:
        """Register Flask routes."""
        
        @self.app.route("/webhook", methods=["POST"])
        def webhook():
            """Handle incoming WhatsApp messages."""
            # Get message details
            from_number = request.form.get("From", "")
            message_body = request.form.get("Body", "").strip()
            
            logger.info(f"Received from {from_number}: {message_body}")
            
            # Create response
            resp = MessagingResponse()
            
            # Check authorization
            if not self._is_authorized(from_number):
                resp.message("X Unauthorized. Contact the administrator.")
                return str(resp)
            
            # Handle commands
            if message_body.lower() == "/start":
                welcome = (
                    "welcome LinguaHome Smart Home Assistant\n\n"
                    "I can help you control your smart home.\n\n"
                    "Examples:\n"
                    "- What's the temperature?\n"
                    "- Turn off the entrance plug\n"
                    "- Which room is warmest?\n\n"
                    "Send /clear to reset conversation."
                )
                resp.message(welcome)
                return str(resp)
            
            if message_body.lower() == "/clear":
                if from_number in self.agents:
                    self.agents[from_number].reset_conversation()
                resp.message("recycle Conversation cleared!")
                return str(resp)
            
            # Process with agent
            try:
                agent = self._get_agent(from_number)
                response = agent.process(message_body)
                resp.message(response.message)
            except Exception as e:
                logger.error(f"Error: {e}")
                resp.message(f"X Error: {str(e)}")
            
            return str(resp)
        
        @self.app.route("/health", methods=["GET"])
        def health():
            """Health check endpoint."""
            return {"status": "ok", "service": "LinguaHome WhatsApp Bot"}
    
    def _is_authorized(self, phone_number: str) -> bool:
        """Check if phone number is authorized."""
        if not self.allowed_numbers:
            return True  # No restrictions
        return phone_number in self.allowed_numbers
    
    def _get_agent(self, phone_number: str) -> AgentLoop:
        """Get or create agent for user."""
        if phone_number not in self.agents:
            self.agents[phone_number] = AgentLoop(
                workspace=self.workspace,
                llm_model=self.llm_model,
            )
        return self.agents[phone_number]
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
        """Run the Flask server."""
        logger.info(f"Starting LinguaHome WhatsApp Bot on {host}:{port}")
        self.app.run(host=host, port=port, debug=debug)


def main():
    """Main entry point."""
    # Validate credentials
    required_vars = ["TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN", "TWILIO_WHATSAPP_NUMBER"]
    missing = [v for v in required_vars if not os.environ.get(v)]
    
    if missing:
        print(f"X Missing environment variables: {', '.join(missing)}")
        print("\nRequired:")
        print("  TWILIO_ACCOUNT_SID     - Your Twilio Account SID")
        print("  TWILIO_AUTH_TOKEN      - Your Twilio Auth Token")
        print("  TWILIO_WHATSAPP_NUMBER - Twilio WhatsApp number (e.g., whatsapp:+14155238886)")
        print("\nOptional:")
        print("  WHATSAPP_ALLOWED_NUMBERS - Comma-separated allowed phone numbers")
        print("  LINGUAHOME_MODEL         - LLM model to use (default: gpt-4o)")
        print("  PORT                     - Server port (default: 5000)")
        return
    
    # Parse allowed numbers
    allowed_str = os.environ.get("WHATSAPP_ALLOWED_NUMBERS", "")
    allowed_numbers = set()
    if allowed_str:
        allowed_numbers = {num.strip() for num in allowed_str.split(",")}
    
    workspace = Path(__file__).parent.parent
    model = os.environ.get("LINGUAHOME_MODEL", "gpt-4o")
    port = int(os.environ.get("PORT", "5000"))
    
    bot = WhatsAppBot(
        workspace=workspace,
        llm_model=model,
        allowed_numbers=allowed_numbers,
    )
    
    print(f"robot LinguaHome WhatsApp Bot")
    print(f"Model: {model}")
    print(f"Port: {port}")
    print(f"Webhook URL: http://your-server:{port}/webhook")
    print("\nNote: Configure this URL in your Twilio Console.")
    
    bot.run(port=port)


if __name__ == "__main__":
    main()
