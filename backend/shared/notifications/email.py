import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_SENDER = "paperalertbot@gmail.com"  # Replace with your sender email
EMAIL_PASSWORD = "zuwv szlz jcuo nxnu"  # Use an environment variable in production
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465

def send_email(recipient_email, subject, body):
    """Send an email to the specified recipient."""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = recipient_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, recipient_email, msg.as_string())
        
        return f"✅ Email successfully sent to {recipient_email}"
    except Exception as e:
        return f"❌ Failed to send email: {e}"
