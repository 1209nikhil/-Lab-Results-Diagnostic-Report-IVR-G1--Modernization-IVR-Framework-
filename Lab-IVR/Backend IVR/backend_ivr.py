from fastapi import FastAPI, Form
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.rest import Client
import os
from supabase import create_client, Client as SupabaseClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Your current ngrok public URL
BASE_URL = os.getenv("BASE_URL")

# Professional English voice
# Popular Indian Female voice
IVR_VOICE = "Polly.Aditi"

# Supabase Configurations
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: SupabaseClient = create_client(SUPABASE_URL, SUPABASE_KEY)

# Twilio Configurations
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# This is a Twilio phone number available to send SMS (or a WhatsApp Sandbox number for WhatsApp)
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER") 
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


@app.post("/voice")
async def main_menu():
    """
    Step 1: Welcome Prompt and Patient ID Gather
    """
    response = VoiceResponse()

    gather = Gather(
        action=f"{BASE_URL}/handle-patient-id",
        method="POST",
        timeout=10,          # 10 second timeout after last digit
        finishOnKey="#"      # User will press # to submit
    )

    gather.say(
        "Welcome to the Lab Results and Diagnostic Report AI system. "
        "To access your secure medical records, please enter your five digit Patient ID using your keypad, followed by the pound sign.",
        voice=IVR_VOICE
    )

    response.append(gather)

    response.say(
        "We did not receive any input. Please try again.",
        voice=IVR_VOICE
    )

    response.redirect(f"{BASE_URL}/voice")

    return Response(content=str(response), media_type="application/xml")


@app.post("/handle-patient-id")
async def handle_patient_id(Digits: str = Form(default=None)):
    """
    Step 2: Check database and give summary, then offer delivery options
    """
    response = VoiceResponse()

    # Log to file for persistent debug
    with open("D:/IVR/ivr_debug.log", "a") as f:
        f.write(f"Received Digits: {Digits}\n")

    if Digits:
        # Strip whitespace, spaces from keypad or terminating characters like '#'
        Digits = Digits.strip().replace("#", "").replace("*", "")
        with open("D:/IVR/ivr_debug.log", "a") as f:
            f.write(f"Cleaned Digits: {Digits}\n")

    # Query Supabase instead of Dummy Dictionary
    res = supabase.table("lab_results").select("*").eq("patient_id", Digits).execute()
    
    with open("D:/IVR/ivr_debug.log", "a") as f:
        f.write(f"Supabase Output: {res.data}\n")
    
    if res.data and len(res.data) > 0:
        patient_record = res.data[0]
        
        if patient_record["status"] == "Pending":
            response.say(
                f"Hello {patient_record['name']}. {patient_record['summary']} "
                "Thank you for calling. Goodbye.",
                voice=IVR_VOICE
            )
            response.hangup()
        else:
            # Results are ready, read summary and offer options
            gather = Gather(
                num_digits=1,
                action=f"{BASE_URL}/handle-delivery-options?patient_id={Digits}",
                method="POST"
            )

            gather.say(
                f"Hello {patient_record['name']}. Your diagnostic reports are ready. "
                f"Here is a summary: {patient_record['summary']} "
                "If you would like the full PDF report sent to your registered Phone number via SMS, press 1. "
                "To receive an Email, press 2. "
                "To speak directly with a healthcare professional, press 3. "
                "To listen to this summary again, press 4.",
                voice=IVR_VOICE
            )

            response.append(gather)

    else:
        # Invalid ID
        response.say(
            "We could not find a match for that Patient ID. Please try again.",
            voice=IVR_VOICE
        )
        response.redirect(f"{BASE_URL}/voice")

    return Response(content=str(response), media_type="application/xml")


@app.post("/handle-delivery-options")
async def handle_delivery_options(patient_id: str = None, Digits: str = Form(default=None)):
    """
    Step 3: Handle Delivery Options for the Report
    """
    response = VoiceResponse()

    if Digits == "1":
        # Send via Twilio SMS
        res = supabase.table("lab_results").select("*").eq("patient_id", patient_id).execute()
        if res.data and len(res.data) > 0:
            patient_record = res.data[0]
            if patient_record.get('phone_number'):
                message_body = f"Hello {patient_record['name']},\n\nYour lab results are ready.\nSummary: {patient_record['summary']}\nDoctor Notes: {patient_record['doctor_notes']}\n\nThank you, LabResults AI."
                try:
                    twilio_client.messages.create(
                        body=message_body,
                        from_=TWILIO_PHONE_NUMBER,
                        to=patient_record['phone_number']
                    )
                    response.say(
                        "Your full diagnostic report has been sent securely to your registered phone number. "
                        "Thank you for using our system. Goodbye and take care.",
                        voice=IVR_VOICE
                    )
                except Exception as e:
                    print("Error sending SMS: ", e)
                    response.say("There was an error sending the message. Please contact support. Goodbye.", voice=IVR_VOICE)
            else:
                 response.say("We do not have a registered phone number on file. Goodbye.", voice=IVR_VOICE)
        response.hangup()

    elif Digits == "2":
        # Mock Email sending
        res = supabase.table("lab_results").select("*").eq("patient_id", patient_id).execute()
        if res.data and len(res.data) > 0:
            patient_record = res.data[0]
            print(f"--- MOCK SENDING EMAIL ---")
            print(f"To: {patient_record.get('email')}")
            print(f"Subject: Your Lab Results")
            print(f"Body: Hello {patient_record['name']}, attached is your lab report. Summary: {patient_record['summary']}")
            print(f"--------------------------")
            
        response.say(
            "Your full diagnostic report has been sent to your registered Email address. "
            "Thank you for using our system. Goodbye and take care.",
            voice=IVR_VOICE
        )
        response.hangup()

    elif Digits == "3":
        response.say(
            "Transferring your call to the next available healthcare representative. Please hold.",
            voice=IVR_VOICE
        )
        # Note: response.dial() would be used here to connect to a real number
        response.hangup()
        
    elif Digits == "4":
        # Redirect back to hear summary again
        response.redirect(f"{BASE_URL}/handle-patient-id?Digits={patient_id}")

    else:
        response.say(
            "Invalid entry. Returning to the main menu.",
            voice=IVR_VOICE
        )
        response.redirect(f"{BASE_URL}/voice")

    return Response(content=str(response), media_type="application/xml")
