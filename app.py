from fastapi import FastAPI, Request
import httpx
import uvicorn

app = FastAPI(title="Gupshup Sandbox Bot")

# --- Configuration ---
# Replace these with your actual Gupshup Sandbox details
GUPSHUP_API_KEY = "sk_cf00f6dfca5f4f1c88110a5e048cc6d7"
GUPSHUP_APP_NAME = "AIMosque"
GUPSHUP_SANDBOX_NUMBER = "917834811114" # This is the standard Gupshup sandbox sender number

async def send_reply(destination_phone: str, text: str):
    """Sends a WhatsApp message back to the user via Gupshup API."""
    url = "https://api.gupshup.io/sm/api/v1/msg"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "apikey": GUPSHUP_API_KEY
    }
    data = {
        "channel": "whatsapp",
        "source": GUPSHUP_SANDBOX_NUMBER,
        "destination": destination_phone,
        "message": f'{{"type":"text","text":"{text}"}}',
        "src.name": GUPSHUP_APP_NAME
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, data=data)
        print(f"Sent reply to {destination_phone}. Gupshup API Status: {response.status_code}")

@app.post("/webhook/gupshup")
async def gupshup_webhook(request: Request):
    """Receives incoming messages from Gupshup Sandbox."""
    try:
        payload = await request.json()
        
        # Gupshup sends delivery receipts and other events. We only care about user messages.
        if payload.get("type") == "message":
            # Extract the user's phone number and the text they sent
            sender_phone = payload["payload"]["sender"]["phone"]
            incoming_text = payload["payload"]["payload"]["text"]
            
            print(f"📲 Received Message from {sender_phone}: {incoming_text}")
            
            # --- Tawasol Bot Logic ---
            if incoming_text.strip() == "1":
                reply_text = "Verification of leave balance and applicable policies is underway... [cite: 115]"
            else:
                reply_text = "Peace be upon you, dear Sheikh. [cite: 115] Welcome to Tawasol. Reply '1' to submit a leave request."
                
            # Send the reply back to WhatsApp
            await send_reply(sender_phone, reply_text)
            
    except Exception as e:
        print(f"❌ Error processing webhook: {e}")

    # Always return a 200 OK success status to Gupshup so they don't retry sending the message
    return {"status": "success"}

if __name__ == "__main__":
    print("🚀 Starting Gupshup Webhook Server on port 8000...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
