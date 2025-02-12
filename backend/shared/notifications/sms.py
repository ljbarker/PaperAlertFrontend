from twilio.rest import Client

# Set these with your Twilio account details or use environment variables
TWILIO_ACCOUNT_SID = "US482743f0eab9050875b43cd7ea2b9375"
TWILIO_AUTH_TOKEN = "ACcd95593fc552285c9fe933e1faf16d55:44c0cc63531806d419764297687b9107
"
TWILIO_PHONE_NUMBER = "your_twilio_phone_number"

def send_sms(recipient_number, message):
    """Send an SMS using Twilio."""
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=recipient_number
        )
        return f"✅ SMS sent successfully to {recipient_number} with SID {message.sid}"
    except Exception as e:
        return f"❌ Failed to send SMS: {e}"
