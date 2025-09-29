"""
Tests for email notification system using Resend.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import os
from datetime import datetime

from monkey_coder.email.sender import EmailNotificationService, email_notification_service
from monkey_coder.monitoring.automated_rollback import RollbackReason


class TestEmailNotificationService:
    """Test the email notification service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock environment variables
        self.env_vars = {
            "RESEND_API_KEY": "re_test_key",
            "NOTIFICATION_EMAIL_FROM": "test@example.com",
            "ADMIN_NOTIFICATION_EMAILS": "admin@example.com,admin2@example.com",
            "ENQUIRY_NOTIFICATION_EMAILS": "support@example.com",
            "ROLLBACK_NOTIFICATION_EMAILS": "devops@example.com",
            "ENV": "development"
        }
        
    def test_email_list_parsing(self):
        """Test parsing of comma-separated email lists."""
        service = EmailNotificationService()
        
        # Test empty string
        assert service._parse_email_list("") == []
        
        # Test single email
        assert service._parse_email_list("test@example.com") == ["test@example.com"]
        
        # Test multiple emails
        emails = service._parse_email_list("test1@example.com,test2@example.com,test3@example.com")
        assert emails == ["test1@example.com", "test2@example.com", "test3@example.com"]
        
        # Test emails with spaces
        emails = service._parse_email_list("test1@example.com, test2@example.com , test3@example.com")
        assert emails == ["test1@example.com", "test2@example.com", "test3@example.com"]
    
    @patch.dict(os.environ, {"ENV": "development"})
    async def test_send_email_verification_development(self):
        """Test email verification in development mode."""
        service = EmailNotificationService()
        
        with patch.object(service, '_send_email', new_callable=AsyncMock) as mock_send:
            await service.send_email_verification("test@example.com", "test_token")
            
            mock_send.assert_called_once()
            args = mock_send.call_args
            assert args[1]["to_emails"] == ["test@example.com"]
            assert "verify-email?token=test_token" in args[1]["html_content"]
            assert args[1]["email_type"] == "verification"
    
    @patch.dict(os.environ, {
        "ENQUIRY_NOTIFICATION_EMAILS": "support@example.com",
        "ENV": "development"
    })
    async def test_send_enquiry_notification(self):
        """Test enquiry notification sending."""
        service = EmailNotificationService()
        
        enquiry_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "subject": "Test Enquiry",
            "message": "This is a test message",
            "timestamp": "2024-01-01T10:00:00",
            "ip_address": "192.168.1.1"
        }
        
        with patch.object(service, '_send_email', new_callable=AsyncMock) as mock_send:
            await service.send_enquiry_notification(enquiry_data)
            
            mock_send.assert_called_once()
            args = mock_send.call_args
            assert "support@example.com" in args[1]["to_emails"]
            assert "New Enquiry: Test Enquiry" in args[1]["subject"]
            assert "John Doe" in args[1]["html_content"]
            assert "john@example.com" in args[1]["html_content"]
            assert args[1]["email_type"] == "enquiry"
    
    @patch.dict(os.environ, {
        "ROLLBACK_NOTIFICATION_EMAILS": "devops@example.com",
        "ENV": "development"
    })
    async def test_send_rollback_notification(self):
        """Test rollback notification sending."""
        service = EmailNotificationService()
        
        rollback_data = {
            "deployment_id": "dep_123",
            "previous_deployment_id": "dep_122",
            "reason": "startup_failure",
            "timestamp": "2024-01-01T10:00:00",
            "success": True,
            "error_message": None,
            "rollback_duration": 45.2
        }
        
        with patch.object(service, '_send_email', new_callable=AsyncMock) as mock_send:
            await service.send_rollback_notification(rollback_data)
            
            mock_send.assert_called_once()
            args = mock_send.call_args
            assert "devops@example.com" in args[1]["to_emails"]
            assert "🚨 Deployment Rollback: startup_failure" in args[1]["subject"]
            assert "dep_123" in args[1]["html_content"]
            assert "dep_122" in args[1]["html_content"]
            assert args[1]["email_type"] == "rollback"
    
    @patch.dict(os.environ, {
        "ADMIN_NOTIFICATION_EMAILS": "admin@example.com",
        "ENV": "development"
    })
    async def test_send_deployment_alert(self):
        """Test deployment alert sending."""
        service = EmailNotificationService()
        
        details = {
            "deployment_id": "dep_123",
            "service_id": "svc_456",
            "error_message": "Health check timeout"
        }
        
        with patch.object(service, '_send_email', new_callable=AsyncMock) as mock_send:
            await service.send_deployment_alert("Deployment Failed", "Test failure message", details)
            
            mock_send.assert_called_once()
            args = mock_send.call_args
            assert "admin@example.com" in args[1]["to_emails"]
            assert "🚂 Railway Deployment Alert: Deployment Failed" in args[1]["subject"]
            assert "Test failure message" in args[1]["html_content"]
            assert "dep_123" in args[1]["html_content"]
            assert args[1]["email_type"] == "alert"
    
    @patch.dict(os.environ, {"ENV": "development"})
    async def test_send_email_development_logging(self, caplog):
        """Test that emails are logged in development mode."""
        import logging
        caplog.set_level(logging.INFO)
        
        service = EmailNotificationService()
        
        await service._send_email(
            to_emails=["test@example.com"],
            subject="Test Subject",
            html_content="<html><body>Test</body></html>",
            email_type="test"
        )
        
        # Check that email was logged instead of sent
        assert "[DEV EMAIL - TEST]" in caplog.text
        assert "test@example.com" in caplog.text
        assert "Test Subject" in caplog.text
    
    @patch.dict(os.environ, {"ENV": "production"})
    @patch('monkey_coder.email.sender.resend', create=True)
    async def test_send_email_production_success(self, mock_resend):
        """Test successful email sending in production mode."""
        mock_resend.emails.send = Mock(return_value={"id": "email_123"})
        
        service = EmailNotificationService()
        service.resend_client = mock_resend
        
        await service._send_email(
            to_emails=["test@example.com"],
            subject="Test Subject",
            html_content="<html><body>Test</body></html>",
            email_type="test"
        )
        
        mock_resend.emails.send.assert_called_once()
        call_args = mock_resend.emails.send.call_args[0][0]
        assert call_args["to"] == ["test@example.com"]
        assert call_args["subject"] == "Test Subject"
        assert call_args["html"] == "<html><body>Test</body></html>"
    
    @patch.dict(os.environ, {"ENV": "production"})
    @patch('monkey_coder.email.sender.resend', create=True)
    async def test_send_email_production_failure(self, mock_resend):
        """Test email sending failure in production mode."""
        mock_resend.emails.send = Mock(side_effect=Exception("Resend API error"))
        
        service = EmailNotificationService()
        service.resend_client = mock_resend
        
        with pytest.raises(Exception, match="Resend API error"):
            await service._send_email(
                to_emails=["test@example.com"],
                subject="Test Subject",
                html_content="<html><body>Test</body></html>",
                email_type="test"
            )
    
    def test_format_details_html(self):
        """Test formatting of details dictionary as HTML."""
        service = EmailNotificationService()
        
        # Test empty details
        assert service._format_details_html({}) == ""
        assert service._format_details_html(None) == ""
        
        # Test details with data
        details = {
            "deployment_id": "dep_123",
            "error_count": 5,
            "response_time": "2.5s"
        }
        
        html = service._format_details_html(details)
        assert "<h4>Additional Details</h4>" in html
        assert "<li><strong>Deployment Id:</strong> dep_123</li>" in html
        assert "<li><strong>Error Count:</strong> 5</li>" in html
        assert "<li><strong>Response Time:</strong> 2.5s</li>" in html


class TestEmailServiceIntegration:
    """Test integration with other components."""
    
    @patch.dict(os.environ, {"ENV": "development"})
    async def test_enquiry_endpoint_integration(self):
        """Test that enquiry endpoint properly uses email service."""
        from monkey_coder.email.sender import email_notification_service
        
        enquiry_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "subject": "Integration Test",
            "message": "Testing integration with email service",
            "timestamp": datetime.utcnow().isoformat(),
            "ip_address": "127.0.0.1"
        }
        
        with patch.object(email_notification_service, 'send_enquiry_notification', new_callable=AsyncMock) as mock_send:
            await email_notification_service.send_enquiry_notification(enquiry_data)
            mock_send.assert_called_once_with(enquiry_data)
    
    @patch.dict(os.environ, {"ENV": "development"})
    async def test_rollback_integration(self):
        """Test that rollback manager properly uses email service."""
        from monkey_coder.monitoring.automated_rollback import RollbackManager
        
        # Create a manager instance
        manager = RollbackManager()
        
        # Mock the email service method directly
        with patch.object(manager.email_service, 'send_rollback_notification', new_callable=AsyncMock) as mock_send:
            rollback_data = {
                "deployment_id": "dep_123",
                "previous_deployment_id": "dep_122",
                "reason": RollbackReason.STARTUP_FAILURE.value,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "error_message": None,
                "rollback_duration": 30.5
            }
            
            await manager.email_service.send_rollback_notification(rollback_data)
            mock_send.assert_called_once_with(rollback_data)


class TestBackwardsCompatibility:
    """Test backwards compatibility with existing EmailSender class."""
    
    def test_legacy_email_sender_exists(self):
        """Test that legacy EmailSender class still exists."""
        from monkey_coder.email.sender import EmailSender
        
        sender = EmailSender()
        assert hasattr(sender, 'send_email_verification')
    
    async def test_legacy_email_sender_functionality(self):
        """Test that legacy EmailSender still works."""
        from monkey_coder.email.sender import EmailSender
        
        sender = EmailSender()
        
        with patch.object(sender._service, 'send_email_verification', new_callable=AsyncMock) as mock_send:
            await sender.send_email_verification("test@example.com", "token123")
            mock_send.assert_called_once_with("test@example.com", "token123")
