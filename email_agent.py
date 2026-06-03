import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv
from openai import OpenAI


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file.")

if not SENDER_EMAIL:
    raise ValueError("SENDER_EMAIL not found in .env file.")

if not GMAIL_APP_PASSWORD:
    raise ValueError("GMAIL_APP_PASSWORD not found in .env file.")


client = OpenAI(api_key=OPENAI_API_KEY)


# =========================================================
# AI EMAIL GENERATOR
# =========================================================

def generate_email(context, recipient_name, tone):
    prompt = f"""
You are EmailMate AI, a professional email writing assistant.

Write a polished email based on the user's context.

Rules:
- Keep it clear, polite, and professional.
- Do not invent fake details.
- If something is missing, keep the wording general.
- Use the selected tone.
- Return only the subject and email body.
- Do not include markdown formatting.
- Do not include placeholders unless necessary.

Recipient Name:
{recipient_name}

Tone:
{tone}

Context:
{context}

Output format:

Subject: [email subject]

Body:
[email body]
"""

    response = client.responses.create(
        model="gpt-4o-mini",
        input=prompt
    )

    return response.output_text


# =========================================================
# EMAIL SENDER
# =========================================================

def send_email(to_email, subject, body):
    msg = EmailMessage()

    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)


# =========================================================
# PARSE SUBJECT AND BODY
# =========================================================

def parse_email(ai_output):
    subject = "No Subject"
    body = ai_output

    if "Subject:" in ai_output and "Body:" in ai_output:
        subject_part = ai_output.split("Body:")[0]
        body_part = ai_output.split("Body:")[1]

        subject = subject_part.replace("Subject:", "").strip()
        body = body_part.strip()

    return subject, body


# =========================================================
# MAIN PROGRAM
# =========================================================

print("===== EmailMate AI Agent =====")
print("This agent writes a professional email and sends it after your confirmation.")
print("Type carefully. You will review the email before sending.\n")

recipient_email = input("Enter recipient email address: ").strip()
recipient_name = input("Enter recipient name, or leave blank: ").strip()

print("\nChoose email tone:")
print("1. Professional")
print("2. Friendly")
print("3. Formal")
print("4. Short and direct")
print("5. Apologetic")

tone_choice = input("Enter tone number 1-5: ").strip()

tone_map = {
    "1": "Professional",
    "2": "Friendly",
    "3": "Formal",
    "4": "Short and direct",
    "5": "Apologetic"
}

tone = tone_map.get(tone_choice, "Professional")

print("\nEnter email context.")
print("Example: I want to ask my professor for an extension because I was sick.")
print("When finished, type END on a new line and press Enter.\n")

lines = []

while True:
    line = input()
    if line.strip().upper() == "END":
        break
    lines.append(line)

context = "\n".join(lines)

print("\nGenerating email...\n")

ai_email = generate_email(context, recipient_name, tone)

subject, body = parse_email(ai_email)

print("===== GENERATED EMAIL =====\n")
print("To:", recipient_email)
print("Subject:", subject)
print("\nBody:\n")
print(body)

print("\n===========================\n")

confirm = input("Do you want to send this email? Type yes to send: ").strip().lower()

if confirm == "yes":
    try:
        send_email(recipient_email, subject, body)
        print("\nEmail sent successfully!")
    except Exception as e:
        print("\nEmail failed to send.")
        print("Error:", e)
else:
    print("\nEmail not sent. You can copy the draft above or run the agent again.")