import os
from dotenv import load_dotenv
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# load .env
load_dotenv()

def send_otp_email(to_email, otp):

    api_key = os.getenv("BREVO_API_KEY")
    sender_email = os.getenv("SENDER_EMAIL")

    print("API KEY:", api_key)  # DEBUG
    print("SENDER:", sender_email)

    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = api_key

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )

    subject = "Your OTP Code"
    html_content = f"<h3>Your OTP is: {otp}</h3>"

    sender = {
        "name": "SecureAuth System",
        "email": sender_email
    }

    to = [{"email": to_email}]

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to,
        html_content=html_content,
        subject=subject,
        sender=sender
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
        print("✅ Email sent successfully")
    except ApiException as e:
        print("❌ Email error:", e)