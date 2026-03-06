import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
my_phone = os.getenv("MY_PHONE_NUMBER")
twilio_phone = os.getenv("TWILIO_PHONE_NUMBER")
base_url = os.getenv("BASE_URL")

client = Client(account_sid, auth_token)

call = client.calls.create(
    to=my_phone,  # Registered phone number
    from_=twilio_phone,
    url=f"{base_url}/voice"
)

print("Call initiated:", call.sid)

"""
Lab Results & Diagnostic IVR Flow:
1. trigger_call.py sends API request to Twilio to call the patient
2. Patient answers the call
3. Twilio sends POST to the /voice webhook
4. FastAPI asks for a 5 digit Patient ID
5. User enters "12345" or "67890" using DTMF keypad
6. Twilio posts input to /handle-patient-id
7. Backend fetches the dummy patient record
8. IVR reads a summary of the diagnostic test
9. If results are ready, user gets options:
    1 -> Send PDF via WhatsApp
    2 -> Send via Email
    3 -> Transfer to Healthcare Representative
10. IVR executes the selection and hangs up.
"""
