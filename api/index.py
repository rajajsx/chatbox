from fastapi import FastAPI, Request
import httpx
import uvicorn
import json
import logging

# --- Set up Professional Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Gupshup Sandbox Bot")

# ⚠️ Paste your correct Sandbox Account API Key here again!
GUPSHUP_API_KEY = "j8lljkz3vaclvqae0ozyrvqyeijmualr" 
GUPSHUP_APP_NAME = "AIMosque"
GUPSHUP_SANDBOX_NUMBER = "917834811114"

async def send_whatsapp_message(destination_phone: str, message_payload: dict):
    """Sends a formatted JSON message back to the user via Gupshup API."""
    url = "https://api.gupshup.io/sm/api/v1/msg"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": GUPSHUP_API_KEY
    }
    data = {
        "channel": "whatsapp",
        "source": GUPSHUP_SANDBOX_NUMBER,
        "destination": destination_phone,
        "message": json.dumps(message_payload), 
        "src.name": GUPSHUP_APP_NAME
    }
    
    logger.info(f"📤 Sending payload to {destination_phone}")
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        if response.status_code == 200:
            logger.info(f"✅ Successfully sent reply to {destination_phone}.")
        else:
            logger.error(f"❌ Failed to send reply. Gupshup Status: {response.status_code} - {response.text}")


@app.post("/webhook/gupshup")
async def gupshup_webhook(request: Request):
    """Receives incoming messages from Gupshup Sandbox."""
    try:
        payload = await request.json()
        
        # Log the full incoming raw payload for deep debugging
        logger.info(f"📥 Raw Webhook Payload Received: {json.dumps(payload)}")
        
        if payload.get("type") == "message":
            sender_phone = payload["payload"]["sender"]["phone"]
            message_type = payload["payload"]["type"]
            
            # --- THE FIX: Handle both Typed Text and Menu Clicks ---
            if message_type == "text":
                incoming_text = payload["payload"]["payload"]["text"].strip()
            elif message_type == "list_reply":
                # When a user clicks a list menu, Gupshup sends the button's "title"
                incoming_text = payload["payload"]["payload"]["title"].strip()
            else:
                incoming_text = "" # Fallback for images, locations, etc.
            
            logger.info(f"💬 User {sender_phone} action ({message_type}): '{incoming_text}'")
            
            # --- Tawasol Bot Logic ---
            if incoming_text == "Leave Request":
                reply = {
                    "type": "text",
                    "text": "Verification of leave balance and applicable policies is underway... Please reply with your requested dates."
                }
                await send_whatsapp_message(sender_phone, reply)

            elif incoming_text == "Report Problem":
                reply = {
                    "type": "text",
                    "text": "Please type a short description of the problem at the mosque. This will be sent directly to the Mosque Eye dashboard."
                }
                await send_whatsapp_message(sender_phone, reply)

            else:
                logger.info("ℹ️ Unrecognized text or greeting. Sending the main menu.")
                menu_payload = {
                    "type": "list",
                    "title": "Tawasol Services",
                    "body": "Peace be upon you, dear Sheikh. How can I assist you today?",
                    "msgid": "main_menu_1",
                    "globalButtons": [{"type": "text", "title": "Select an Option"}],
                    "items": [
                        {
                            "title": "Main Menu",
                            "subtitle": "Please choose a service",
                            "options": [
                                {"type": "text", "title": "Leave Request", "description": "Submit a request for absence"},
                                {"type": "text", "title": "Report Problem", "description": "Report an infrastructure issue"}
                            ]
                        }
                    ]
                }
                await send_whatsapp_message(sender_phone, menu_payload)
            
    except Exception as e:
        logger.error(f"💥 CRITICAL ERROR processing webhook: {str(e)}")

    return {"status": "success"}

@app.get("/")
async def root():
    return {"message": "Server is running! Webhooks are located at /webhook/gupshup"}
