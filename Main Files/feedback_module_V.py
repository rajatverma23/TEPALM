"""
Feedback Module for PANDULIPI
Handles user feedback collection and email sending
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QComboBox, QLineEdit,
                            QMessageBox, QGroupBox, QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont


class FeedbackEmailSender(QThread):
    """Background thread for sending feedback emails"""
    success = pyqtSignal()
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, feedback_data, email_config):
        super().__init__()
        self.feedback_data = feedback_data
        self.email_config = email_config
    
    def run(self):
        """Send feedback email"""
        try:
            self.progress.emit("Preparing email...")
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"PANDULIPI Feedback: {self.feedback_data['category']}"
            msg['From'] = self.email_config['sender_email']
            msg['To'] = self.email_config['recipient_email']
            
            # Create email body
            email_body = self._create_email_body()
            
            # Attach HTML and plain text versions
            text_part = MIMEText(email_body['text'], 'plain', 'utf-8')
            html_part = MIMEText(email_body['html'], 'html', 'utf-8')
            msg.attach(text_part)
            msg.attach(html_part)
            
            self.progress.emit("Connecting to email server...")
            
            # Send email using SMTP
            with smtplib.SMTP(self.email_config['smtp_server'], 
                            self.email_config['smtp_port']) as server:
                server.starttls()
                
                self.progress.emit("Authenticating...")
                server.login(self.email_config['sender_email'], 
                           self.email_config['sender_password'])
                
                self.progress.emit("Sending feedback...")
                server.send_message(msg)
            
            self.success.emit()
            
        except smtplib.SMTPAuthenticationError:
            self.error.emit("Authentication failed. Please check email credentials.")
        except smtplib.SMTPException as e:
            self.error.emit(f"SMTP error: {str(e)}")
        except Exception as e:
            self.error.emit(f"Failed to send feedback: {str(e)}")
    
    def _create_email_body(self):
        """Create formatted email body"""
        data = self.feedback_data
        
        # Plain text version
        text_body = f"""
PANDULIPI Feedback Report
{'=' * 50}

Timestamp: {data['timestamp']}
Category: {data['category']}
User Name: {data.get('user_name', 'Anonymous')}
User Email: {data.get('user_email', 'Not provided')}

Feedback:
{data['feedback']}

{'=' * 50}
System Information:
{'=' * 50}
Application Version: {data.get('app_version', 'Unknown')}
Document Type: {data.get('document_type', 'Unknown')}
Current Page: {data.get('current_page', 'N/A')}
Total Pages: {data.get('total_pages', 'N/A')}

OCR Settings:
- Language: {data.get('ocr_language', 'Unknown')}
- FoundIR Enabled: {data.get('foundir_enabled', False)}
- Spell Check Enabled: {data.get('spell_check_enabled', False)}

"""
        
        # HTML version
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ background-color: white; padding: 30px; border-radius: 10px; max-width: 800px; margin: 0 auto; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; margin-top: 25px; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; }}
        .metadata {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .feedback-box {{ background-color: #fff; border-left: 4px solid #3498db; padding: 15px; margin: 15px 0; font-size: 14px; line-height: 1.6; }}
        .info-grid {{ display: grid; grid-template-columns: 200px 1fr; gap: 10px; margin: 10px 0; }}
        .info-label {{ font-weight: bold; color: #7f8c8d; }}
        .info-value {{ color: #2c3e50; }}
        .category {{ background-color: #3498db; color: white; padding: 5px 15px; border-radius: 15px; display: inline-block; margin: 10px 0; }}
        .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #bdc3c7; color: #7f8c8d; font-size: 12px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📝 PANDULIPI Feedback Report</h1>
        
        <div class="metadata">
            <div class="info-grid">
                <div class="info-label">Timestamp:</div>
                <div class="info-value">{data['timestamp']}</div>
                
                <div class="info-label">Category:</div>
                <div class="info-value"><span class="category">{data['category']}</span></div>
                
                <div class="info-label">User Name:</div>
                <div class="info-value">{data.get('user_name', 'Anonymous')}</div>
                
                <div class="info-label">User Email:</div>
                <div class="info-value">{data.get('user_email', 'Not provided')}</div>
            </div>
        </div>
        
        <h2>Feedback Details</h2>
        <div class="feedback-box">
            {data['feedback'].replace(chr(10), '<br>')}
        </div>
        
        <h2>System Information</h2>
        <div class="info-grid">
            <div class="info-label">App Version:</div>
            <div class="info-value">{data.get('app_version', 'Unknown')}</div>
            
            <div class="info-label">Document Type:</div>
            <div class="info-value">{data.get('document_type', 'Unknown')}</div>
            
            <div class="info-label">Current Page:</div>
            <div class="info-value">{data.get('current_page', 'N/A')}</div>
            
            <div class="info-label">Total Pages:</div>
            <div class="info-value">{data.get('total_pages', 'N/A')}</div>
        </div>
        
        <h2>OCR Configuration</h2>
        <div class="info-grid">
            <div class="info-label">Language:</div>
            <div class="info-value">{data.get('ocr_language', 'Unknown')}</div>
            
            <div class="info-label">FoundIR:</div>
            <div class="info-value">{'✓ Enabled' if data.get('foundir_enabled', False) else '✗ Disabled'}</div>
            
            <div class="info-label">Spell Check:</div>
            <div class="info-value">{'✓ Enabled' if data.get('spell_check_enabled', False) else '✗ Disabled'}</div>
        </div>
        
        <div class="footer">
            <p>This feedback was automatically generated by PANDULIPI - Manuscript Annotation Tool</p>
        </div>
    </div>
</body>
</html>
"""
        
        return {'text': text_body, 'html': html_body}


class FeedbackDialog(QDialog):
    """Dialog for collecting user feedback"""
    
    def __init__(self, parent=None, app_context=None):
        super().__init__(parent)
        self.app_context = app_context or {}
        self.email_sender = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the feedback dialog UI"""
        self.setWindowTitle("Send Feedback - PANDULIPI")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Header
        header = QLabel("📧 Send Feedback")
        header.setFont(QFont("Arial", 16, QFont.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px;")
        main_layout.addWidget(header)
        
        info_label = QLabel(
            "We'd love to hear your thoughts! Your feedback helps us improve PANDULIPI."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #7f8c8d; padding: 0 10px 10px 10px;")
        main_layout.addWidget(info_label)
        
        # User information group
        user_group = QGroupBox("Your Information (Optional)")
        user_layout = QVBoxLayout()
        user_group.setLayout(user_layout)
        
        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Your name")
        name_layout.addWidget(self.name_input)
        user_layout.addLayout(name_layout)
        
        # Email input
        email_layout = QHBoxLayout()
        email_layout.addWidget(QLabel("Email:"))
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("your.email@example.com (for follow-up)")
        email_layout.addWidget(self.email_input)
        user_layout.addLayout(email_layout)
        
        main_layout.addWidget(user_group)
        
        # Feedback category
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "Bug Report",
            "Feature Request",
            "Performance Issue",
            "OCR Accuracy",
            "User Interface",
            "Documentation",
            "General Feedback",
            "Other"
        ])
        category_layout.addWidget(self.category_combo, 1)
        main_layout.addLayout(category_layout)
        
        # Feedback text
        main_layout.addWidget(QLabel("Your Feedback:"))
        self.feedback_text = QTextEdit()
        self.feedback_text.setPlaceholderText(
            "Please describe your feedback in detail...\n\n"
            "For bug reports, include:\n"
            "- What you were doing\n"
            "- What you expected to happen\n"
            "- What actually happened\n\n"
            "For feature requests, describe:\n"
            "- What feature you'd like\n"
            "- Why it would be useful\n"
            "- How you imagine it working"
        )
        self.feedback_text.setMinimumHeight(200)
        main_layout.addWidget(self.feedback_text, 1)
        
        # Include system info checkbox
        self.include_system_info = QCheckBox("Include system information (recommended)")
        self.include_system_info.setChecked(True)
        self.include_system_info.setToolTip(
            "Includes: app version, document type, OCR settings, etc.\n"
            "This helps us understand the context of your feedback."
        )
        main_layout.addWidget(self.include_system_info)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        main_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #3498db; padding: 5px;")
        self.status_label.setWordWrap(True)
        main_layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.send_button = QPushButton("📧 Send Feedback")
        self.send_button.clicked.connect(self.send_feedback)
        self.send_button.setDefault(True)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        button_layout.addWidget(self.send_button)
        
        main_layout.addLayout(button_layout)
        
        # Character counter
        self.char_counter = QLabel("0 characters")
        self.char_counter.setStyleSheet("color: #95a5a6; font-size: 10px;")
        self.char_counter.setAlignment(Qt.AlignRight)
        main_layout.addWidget(self.char_counter)
        
        # Connect text change for character counter
        self.feedback_text.textChanged.connect(self.update_char_counter)
    
    def update_char_counter(self):
        """Update character counter"""
        text = self.feedback_text.toPlainText()
        char_count = len(text)
        self.char_counter.setText(f"{char_count} characters")
        
        # Change color based on length
        if char_count < 20:
            self.char_counter.setStyleSheet("color: #e74c3c; font-size: 10px;")
        elif char_count < 50:
            self.char_counter.setStyleSheet("color: #f39c12; font-size: 10px;")
        else:
            self.char_counter.setStyleSheet("color: #27ae60; font-size: 10px;")
    
    def send_feedback(self):
        """Validate and send feedback"""
        feedback = self.feedback_text.toPlainText().strip()
        
        if not feedback:
            QMessageBox.warning(
                self,
                "Empty Feedback",
                "Please enter your feedback before sending."
            )
            self.feedback_text.setFocus()
            return
        
        if len(feedback) < 10:
            QMessageBox.warning(
                self,
                "Feedback Too Short",
                "Please provide more detailed feedback (at least 10 characters)."
            )
            self.feedback_text.setFocus()
            return
        
        # Prepare feedback data
        feedback_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'category': self.category_combo.currentText(),
            'feedback': feedback,
            'user_name': self.name_input.text().strip() or 'Anonymous',
            'user_email': self.email_input.text().strip() or 'Not provided'
        }
        
        # Add system information if checkbox is checked
        if self.include_system_info.isChecked():
            feedback_data.update(self.app_context)
        
        # Load email configuration
        email_config = self.load_email_config()
        
        if not email_config:
            QMessageBox.critical(
                self,
                "Configuration Error",
                "Email configuration not found. Please contact the administrator."
            )
            return
        
        # Disable UI during sending
        self.send_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Preparing to send feedback...")
        
        # Create and start email sender thread
        self.email_sender = FeedbackEmailSender(feedback_data, email_config)
        self.email_sender.success.connect(self.handle_send_success)
        self.email_sender.error.connect(self.handle_send_error)
        self.email_sender.progress.connect(self.update_send_progress)
        self.email_sender.start()
    
    def load_email_config(self):
        """Load email configuration from file"""
        config_file = "email_config.json"
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                
                required_keys = ['smtp_server', 'smtp_port', 'sender_email', 
                               'sender_password', 'recipient_email']
                
                if all(key in config for key in required_keys):
                    return config
                else:
                    print(f"Missing required keys in {config_file}")
                    return None
                    
        except FileNotFoundError:
            # Create default config file
            default_config = {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "sender_email": "your-email@gmail.com",
                "sender_password": "your-app-password",
                "recipient_email": "feedback@pandulipi.com",
                "note": "For Gmail, use App Password (not regular password). See: https://support.google.com/accounts/answer/185833"
            }
            
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            
            print(f"Created default {config_file}. Please configure it.")
            return None
            
        except Exception as e:
            print(f"Error loading email config: {e}")
            return None
    
    def update_send_progress(self, message):
        """Update progress message"""
        self.status_label.setText(message)
    
    def handle_send_success(self):
        """Handle successful feedback submission"""
        self.progress_bar.setVisible(False)
        self.status_label.setStyleSheet("color: #27ae60; padding: 5px; font-weight: bold;")
        self.status_label.setText("✓ Feedback sent successfully!")
        
        QMessageBox.information(
            self,
            "Feedback Sent",
            "Thank you for your feedback!\n\n"
            "We appreciate you taking the time to help us improve PANDULIPI."
        )
        
        self.accept()
    
    def handle_send_error(self, error_message):
        """Handle feedback submission error"""
        self.progress_bar.setVisible(False)
        self.status_label.setStyleSheet("color: #e74c3c; padding: 5px;")
        self.status_label.setText(f"✗ Error: {error_message}")
        
        # Re-enable buttons
        self.send_button.setEnabled(True)
        self.cancel_button.setEnabled(True)
        
        QMessageBox.critical(
            self,
            "Send Failed",
            f"Failed to send feedback:\n\n{error_message}\n\n"
            "Please check your internet connection and email configuration."
        )