import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    
logger = logging.getLogger(__name__)

class EmailNotificationService:
    """Enhanced email notification service using Resend API.
    
    Handles enquiry notifications, rollback notifications, and general alerts.
    Falls back to logging in development or when Resend is not available.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("RESEND_API_KEY")
        self.env = os.getenv("ENV", "development")
        self.from_email = os.getenv("NOTIFICATION_EMAIL_FROM", "notifications@fastmonkey.au")
        
        # Email configuration
        self.admin_emails = self._parse_email_list(os.getenv("ADMIN_NOTIFICATION_EMAILS", ""))
        self.enquiry_emails = self._parse_email_list(os.getenv("ENQUIRY_NOTIFICATION_EMAILS", ""))
        self.rollback_emails = self._parse_email_list(os.getenv("ROLLBACK_NOTIFICATION_EMAILS", ""))
        
        # Initialize Resend client
        self.resend_client = None
        if RESEND_AVAILABLE and self.api_key:
            try:
                resend.api_key = self.api_key
                self.resend_client = resend
                logger.info("Resend email service initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Resend: {e}")
        else:
            if not RESEND_AVAILABLE:
                logger.warning("Resend package not available - email notifications will be logged only")
            if not self.api_key:
                logger.warning("No Resend API key configured - email notifications will be logged only")
    
    def _parse_email_list(self, email_string: str) -> List[str]:
        """Parse comma-separated email list."""
        if not email_string:
            return []
        return [email.strip() for email in email_string.split(",") if email.strip()]
    
    async def send_email_verification(self, to_email: str, token: str):
        """Send email verification (existing functionality)."""
        base = os.getenv("PUBLIC_APP_URL", "http://localhost:3000")
        verify_url = f"{base}/verify-email?token={token}"
        
        subject = "Verify your email address"
        html_content = f"""
        <html>
        <body>
            <h2>Email Verification</h2>
            <p>Please click the link below to verify your email address:</p>
            <p><a href="{verify_url}">Verify Email</a></p>
            <p>If you didn't request this verification, please ignore this email.</p>
            <p>Token: {token}</p>
        </body>
        </html>
        """
        
        await self._send_email(
            to_emails=[to_email],
            subject=subject,
            html_content=html_content,
            email_type="verification"
        )
    
    async def send_enquiry_notification(self, enquiry_data: Dict[str, Any]):
        """Send email notification for new enquiries."""
        if not self.enquiry_emails and not self.admin_emails:
            logger.warning("No enquiry notification emails configured")
            return
        
        recipient_emails = self.enquiry_emails or self.admin_emails
        
        subject = f"New Enquiry: {enquiry_data.get('subject', 'No Subject')}"
        
        html_content = f"""
        <html>
        <body>
            <h2>🔔 New Enquiry Received</h2>
            <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 10px 0;">
                <h3>Enquiry Details</h3>
                <p><strong>Name:</strong> {enquiry_data.get('name', 'N/A')}</p>
                <p><strong>Email:</strong> {enquiry_data.get('email', 'N/A')}</p>
                <p><strong>Subject:</strong> {enquiry_data.get('subject', 'N/A')}</p>
                <p><strong>Message:</strong></p>
                <div style="background-color: white; padding: 15px; border-left: 4px solid #007bff;">
                    {enquiry_data.get('message', 'No message provided')}
                </div>
                <p><strong>Submitted:</strong> {enquiry_data.get('timestamp', datetime.now().isoformat())}</p>
                <p><strong>IP Address:</strong> {enquiry_data.get('ip_address', 'Unknown')}</p>
            </div>
            <p style="font-size: 12px; color: #666;">
                This is an automated notification from Monkey Coder.
            </p>
        </body>
        </html>
        """
        
        await self._send_email(
            to_emails=recipient_emails,
            subject=subject,
            html_content=html_content,
            email_type="enquiry"
        )
    
    async def send_rollback_notification(self, rollback_data: Dict[str, Any]):
        """Send email notification for rollback events."""
        if not self.rollback_emails and not self.admin_emails:
            logger.warning("No rollback notification emails configured")
            return
        
        recipient_emails = self.rollback_emails or self.admin_emails
        
        reason = rollback_data.get('reason', 'Unknown')
        deployment_id = rollback_data.get('deployment_id', 'Unknown')
        
        subject = f"🚨 Deployment Rollback: {reason}"
        
        # Color coding based on reason
        if reason.lower() in ['startup_failure', 'crash_loop']:
            alert_color = "#dc3545"  # Red
            emoji = "🚨"
        elif reason.lower() in ['health_check_failure']:
            alert_color = "#fd7e14"  # Orange
            emoji = "⚠️"
        else:
            alert_color = "#6c757d"  # Gray
            emoji = "🔄"
        
        html_content = f"""
        <html>
        <body>
            <h2>{emoji} Deployment Rollback Alert</h2>
            <div style="background-color: #f8d7da; padding: 20px; border-radius: 8px; margin: 10px 0; border-left: 4px solid {alert_color};">
                <h3 style="color: {alert_color};">Rollback Details</h3>
                <p><strong>Deployment ID:</strong> {deployment_id}</p>
                <p><strong>Reason:</strong> {reason}</p>
                <p><strong>Previous Deployment:</strong> {rollback_data.get('previous_deployment_id', 'N/A')}</p>
                <p><strong>Timestamp:</strong> {rollback_data.get('timestamp', datetime.now().isoformat())}</p>
                <p><strong>Success:</strong> {'✅ Yes' if rollback_data.get('success', False) else '❌ No'}</p>
                
                {f'<p><strong>Error Message:</strong></p><div style="background-color: white; padding: 10px; font-family: monospace;">{rollback_data.get("error_message")}</div>' if rollback_data.get('error_message') else ''}
                
                <p><strong>Duration:</strong> {rollback_data.get('rollback_duration', 'Unknown')}s</p>
            </div>
            
            <div style="background-color: #e7f3ff; padding: 15px; border-radius: 8px; margin: 10px 0;">
                <h4>Next Steps</h4>
                <ul>
                    <li>Check application logs for detailed error information</li>
                    <li>Verify deployment configuration and dependencies</li>
                    <li>Test the rollback deployment for stability</li>
                    <li>Plan remediation for the failed deployment</li>
                </ul>
            </div>
            
            <p style="font-size: 12px; color: #666;">
                This is an automated notification from Monkey Coder deployment monitoring.
            </p>
        </body>
        </html>
        """
        
        await self._send_email(
            to_emails=recipient_emails,
            subject=subject,
            html_content=html_content,
            email_type="rollback"
        )
    
    async def send_deployment_alert(self, alert_type: str, message: str, details: Dict[str, Any] = None):
        """Send general deployment alert email."""
        if not self.admin_emails:
            logger.warning("No admin notification emails configured for deployment alerts")
            return
        
        subject = f"🚂 Railway Deployment Alert: {alert_type}"
        
        # Color coding for different alert types
        if "failed" in alert_type.lower() or "error" in alert_type.lower():
            alert_color = "#dc3545"  # Red
            emoji = "🚨"
        elif "warning" in alert_type.lower() or "slow" in alert_type.lower():
            alert_color = "#fd7e14"  # Orange  
            emoji = "⚠️"
        else:
            alert_color = "#28a745"  # Green
            emoji = "✅"
        
        html_content = f"""
        <html>
        <body>
            <h2>{emoji} Railway Deployment Alert</h2>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 10px 0; border-left: 4px solid {alert_color};">
                <h3 style="color: {alert_color};">{alert_type}</h3>
                <p><strong>Message:</strong> {message}</p>
                <p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</p>
                
                {self._format_details_html(details) if details else ''}
            </div>
            
            <p style="font-size: 12px; color: #666;">
                This is an automated alert from Monkey Coder deployment monitoring.
            </p>
        </body>
        </html>
        """
        
        await self._send_email(
            to_emails=self.admin_emails,
            subject=subject,
            html_content=html_content,
            email_type="alert"
        )
    
    def _format_details_html(self, details: Dict[str, Any]) -> str:
        """Format details dictionary as HTML."""
        if not details:
            return ""
        
        html = "<h4>Additional Details</h4><ul>"
        for key, value in details.items():
            formatted_key = key.replace('_', ' ').title()
            html += f"<li><strong>{formatted_key}:</strong> {value}</li>"
        html += "</ul>"
        return html
    
    async def _send_email(self, to_emails: List[str], subject: str, html_content: str, email_type: str = "notification"):
        """Internal method to send email via Resend or log in development."""
        if not to_emails:
            logger.warning(f"No recipient emails for {email_type} notification")
            return
        
        if self.env != "production" or not self.resend_client:
            logger.info(f"[DEV EMAIL - {email_type.upper()}]")
            logger.info(f"To: {', '.join(to_emails)}")
            logger.info(f"Subject: {subject}")
            logger.info(f"Content: {html_content[:200]}...")
            return
        
        try:
            for to_email in to_emails:
                params = {
                    "from": self.from_email,
                    "to": [to_email],
                    "subject": subject,
                    "html": html_content,
                }
                
                response = self.resend_client.emails.send(params)
                logger.info(f"Email sent successfully to {to_email}: {response}")
                
        except Exception as e:
            logger.error(f"Failed to send {email_type} email: {e}")
            raise

# Legacy EmailSender class for backwards compatibility
class EmailSender:
    """Legacy email sender - redirects to EmailNotificationService."""
    
    def __init__(self):
        self._service = EmailNotificationService()
    
    async def send_email_verification(self, to_email: str, token: str):
        await self._service.send_email_verification(to_email, token)

# Global instances
email_notification_service = EmailNotificationService()
email_sender = EmailSender()  # Maintain backwards compatibility
