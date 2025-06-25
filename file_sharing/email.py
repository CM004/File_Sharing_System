import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import secrets
import string
from typing import Optional

# Email configuration (for demo purposes - you can use real SMTP in production)
SMTP_SERVER = "smtp.gmail.com"  # Change as needed
SMTP_PORT = 587
EMAIL_USER = "your-email@gmail.com"  # Change this
EMAIL_PASSWORD = "your-app-password"  # Change this

def generate_verification_token(length: int = 32) -> str:
    """Generate a secure verification token"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def send_verification_email(email: str, token: str, base_url: str = "http://localhost:8000"):
    """Send verification email to user"""
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = email
        msg['Subject'] = "Email Verification - File Sharing System"
        
        # Create verification link
        verification_link = f"{base_url}/client/verify?token={token}"
        
        # Email body
        body = f"""
        Hello!
        
        Thank you for signing up to our File Sharing System.
        
        Please click the following link to verify your email address:
        {verification_link}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        
        Best regards,
        File Sharing System Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email (for demo, we'll just print it)
        print(f"=== EMAIL SENT ===")
        print(f"To: {email}")
        print(f"Subject: Email Verification")
        print(f"Body: {body}")
        print(f"==================")
        
        # Uncomment the following lines to actually send emails
        # server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        # server.starttls()
        # server.login(EMAIL_USER, EMAIL_PASSWORD)
        # text = msg.as_string()
        # server.sendmail(EMAIL_USER, email, text)
        # server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_download_link_email(email: str, download_link: str):
    """Send download link email to user"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = email
        msg['Subject'] = "File Download Link - File Sharing System"
        
        body = f"""
        Hello!
        
        You requested a file download. Here's your secure download link:
        
        {download_link}
        
        This link will expire in 1 hour and can only be used by you.
        
        Best regards,
        File Sharing System Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # For demo, just print the email
        print(f"=== DOWNLOAD LINK EMAIL ===")
        print(f"To: {email}")
        print(f"Subject: File Download Link")
        print(f"Body: {body}")
        print(f"===========================")
        
        return True
        
    except Exception as e:
        print(f"Error sending download link email: {e}")
        return False

# Store verification tokens (in production, use Redis or database)
verification_tokens = {}

def store_verification_token(email: str, token: str):
    """Store verification token with expiry"""
    expiry = datetime.utcnow() + timedelta(hours=24)
    verification_tokens[token] = {
        'email': email,
        'expiry': expiry
    }

def get_verification_token(token: str) -> Optional[str]:
    """Get email associated with verification token"""
    if token in verification_tokens:
        token_data = verification_tokens[token]
        if token_data['expiry'] > datetime.utcnow():
            email = token_data['email']
            # Remove used token
            del verification_tokens[token]
            return email
    return None
