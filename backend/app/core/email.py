"""
Email service for sending transactional emails.

Uses fastapi-mail for async email sending with SMTP.
Gracefully degrades if SMTP is not configured.
"""
from typing import Optional

from app.core.config import settings

# Lazy-loaded email configuration
_fast_mail: Optional["FastMail"] = None
_email_configured: bool = False


def _get_fast_mail():
    """
    Lazy-load FastMail instance.
    Only creates connection when actually needed.
    Returns None if SMTP is not properly configured.
    """
    global _fast_mail, _email_configured
    
    if _fast_mail is not None:
        return _fast_mail
    
    # Check if SMTP is configured
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD or settings.SMTP_PASSWORD == "your_smtp_password_or_api_key":
        print("⚠️  SMTP not configured - email sending disabled")
        print("   Set SMTP_USER, SMTP_PASSWORD, and MAIL_FROM in .env to enable emails")
        _email_configured = False
        return None
    
    # Check MAIL_FROM is valid
    if not settings.MAIL_FROM or '@' not in settings.MAIL_FROM:
        print("⚠️  MAIL_FROM not configured - email sending disabled")
        _email_configured = False
        return None
    
    # Check for reserved/invalid domains that will fail validation
    mail_domain = settings.MAIL_FROM.split('@')[1].lower()
    invalid_tlds = ['.local', '.localhost', '.test', '.invalid', '.example']
    if any(mail_domain.endswith(tld) for tld in invalid_tlds) or mail_domain in ['localhost', 'local', 'example.com']:
        print(f"⚠️  MAIL_FROM domain '{mail_domain}' is reserved/invalid - email sending disabled")
        print("   Set a real email address in MAIL_FROM to enable emails")
        _email_configured = False
        return None
    
    try:
        from fastapi_mail import FastMail, ConnectionConfig
        
        email_config = ConnectionConfig(
            MAIL_USERNAME=settings.SMTP_USER,
            MAIL_PASSWORD=settings.SMTP_PASSWORD,
            MAIL_FROM=settings.MAIL_FROM,
            MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
            MAIL_PORT=settings.SMTP_PORT,
            MAIL_SERVER=settings.SMTP_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
        )
        
        _fast_mail = FastMail(email_config)
        _email_configured = True
        print("✅ Email service configured successfully")
        return _fast_mail
        
    except Exception as e:
        print(f"⚠️  Failed to configure email service: {e}")
        print("   Email sending will be disabled")
        _email_configured = False
        return None


async def send_password_reset_email(
    email: str,
    token: str,
    username: str | None = None
) -> bool:
    """
    Send password reset email with reset link.
    
    Args:
        email: User's email address
        token: Password reset token
        username: Optional username for personalization
        
    Returns:
        True if email sent successfully, False otherwise
        
    Security:
        - Token is included in URL, not email body
        - Link expires after configured time
        - Uses TLS for transmission
    """
    fast_mail = _get_fast_mail()
    
    if fast_mail is None:
        print(f"📧 [DEV MODE] Password reset requested for {email}")
        print(f"   Reset link: {settings.FRONTEND_URL}/reset-password?token={token}&email={email}")
        print(f"   (Configure SMTP to send real emails)")
        return True  # Return True so the flow continues
    
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}&email={email}"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 30px; background-color: #f9fafb; }}
            .button {{ 
                display: inline-block; 
                padding: 12px 30px; 
                background-color: #3b82f6; 
                color: white; 
                text-decoration: none; 
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            .warning {{ color: #dc2626; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📞 Phonebook App</h1>
            </div>
            <div class="content">
                <h2>Password Reset Request</h2>
                <p>Hello{f' {username}' if username else ''},</p>
                <p>We received a request to reset your password. Click the button below to create a new password:</p>
                
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background: #e5e7eb; padding: 10px; border-radius: 5px;">
                    {reset_url}
                </p>
                
                <p class="warning">
                    ⚠️ This link will expire in {settings.RESET_TOKEN_EXPIRE_HOURS} hour(s).
                </p>
                
                <p>If you didn't request a password reset, please ignore this email or contact support if you have concerns.</p>
            </div>
            <div class="footer">
                <p>This is an automated message from Phonebook App.</p>
                <p>Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        from fastapi_mail import MessageSchema, MessageType
        
        message = MessageSchema(
            subject="Password Reset Request - Phonebook App",
            recipients=[email],
            body=html_body,
            subtype=MessageType.html,
        )
        
        await fast_mail.send_message(message)
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {email}: {e}")
        return False


async def send_password_changed_notification(
    email: str,
    username: str | None = None
) -> bool:
    """
    Send notification that password was changed.
    
    Args:
        email: User's email address
        username: Optional username for personalization
        
    Returns:
        True if email sent successfully
        
    Security: Alerts user if password was changed unexpectedly
    """
    fast_mail = _get_fast_mail()
    
    if fast_mail is None:
        print(f"📧 [DEV MODE] Password changed notification for {email}")
        return True
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3b82f6; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 30px; background-color: #f9fafb; }}
            .footer {{ padding: 20px; text-align: center; color: #666; font-size: 12px; }}
            .alert {{ background-color: #fef2f2; border: 1px solid #dc2626; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📞 Phonebook App</h1>
            </div>
            <div class="content">
                <h2>Password Changed Successfully</h2>
                <p>Hello{f' {username}' if username else ''},</p>
                <p>Your password has been successfully changed.</p>
                
                <div class="alert">
                    <strong>⚠️ Didn't make this change?</strong>
                    <p>If you didn't change your password, please contact support immediately as your account may have been compromised.</p>
                </div>
            </div>
            <div class="footer">
                <p>This is an automated message from Phonebook App.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        from fastapi_mail import MessageSchema, MessageType
        
        message = MessageSchema(
            subject="Password Changed - Phonebook App",
            recipients=[email],
            body=html_body,
            subtype=MessageType.html,
        )
        
        await fast_mail.send_message(message)
        return True
        
    except Exception as e:
        print(f"❌ Failed to send notification to {email}: {e}")
        return False
