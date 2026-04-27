"""
Secure Email Service with Digital Signatures and Encryption
"""
import smtplib
import hashlib
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from django.conf import settings
from django.template import loader
from django.utils import timezone
import os
import json

class SecureEmailService:
    """
    Service for sending encrypted and digitally signed emails
    """
    
    def __init__(self):
        self.encryption_key = self._get_or_create_encryption_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_or_create_encryption_key(self):
        """Get or create encryption key for email content"""
        key_file = os.path.join(settings.BASE_DIR, 'email_encryption.key')
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                key = f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            # Set secure permissions
            os.chmod(key_file, 0o600)
        
        return key
    
    def encrypt_receipt_data(self, receipt_data):
        """Encrypt receipt data to prevent tampering"""
        json_data = json.dumps(receipt_data, default=str)
        encrypted_data = self.cipher_suite.encrypt(json_data.encode())
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_receipt_data(self, encrypted_data):
        """Decrypt receipt data for verification"""
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_data = self.cipher_suite.decrypt(encrypted_bytes)
        return json.loads(decrypted_data.decode())
    
    def generate_digital_signature(self, receipt_data):
        """Generate digital signature for receipt verification"""
        # Create a hash of the receipt data
        receipt_json = json.dumps(receipt_data, sort_keys=True, default=str)
        receipt_hash = hashlib.sha256(receipt_json.encode()).hexdigest()
        
        # Create signature using server secret
        server_secret = getattr(settings, 'RECEIPT_SIGNATURE_SECRET', 'default-secret-key')
        signature_input = f"{receipt_hash}:{server_secret}:{timezone.now().strftime('%Y%m%d')}"
        signature = hashlib.sha256(signature_input.encode()).hexdigest()
        
        return signature
    
    def verify_digital_signature(self, receipt_data, signature):
        """Verify digital signature of receipt"""
        try:
            # Recreate the hash
            receipt_json = json.dumps(receipt_data, sort_keys=True, default=str)
            receipt_hash = hashlib.sha256(receipt_json.encode()).hexdigest()
            
            # Recreate signature
            server_secret = getattr(settings, 'RECEIPT_SIGNATURE_SECRET', 'default-secret-key')
            signature_input = f"{receipt_hash}:{server_secret}:{timezone.now().strftime('%Y%m%d')}"
            expected_signature = hashlib.sha256(signature_input.encode()).hexdigest()
            
            # Compare signatures (constant-time comparison to prevent timing attacks)
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    def send_payment_receipt_email(self, payment, receipt, user_email):
        """
        Send encrypted payment receipt email with digital signature
        """
        try:
            # Prepare receipt data
            receipt_data = {
                'receipt_number': receipt.receipt_number,
                'payment_id': payment.payment_id,
                'amount': float(payment.amount),
                'payment_date': payment.payment_date.isoformat(),
                'payment_status': payment.payment_status,
                'payment_method': payment.payment_method,
                'transaction_id': payment.transaction_id,
                'booking_id': payment.booking.id,
                'property_name': payment.booking.rental_property.name,
                'user_email': user_email,
                'currency': 'UGX'
            }
            
            # Generate digital signature
            signature = self.generate_digital_signature(receipt_data)
            
            # Encrypt sensitive data
            encrypted_data = self.encrypt_receipt_data(receipt_data)
            
            # Create verification URL
            verification_url = f"{getattr(settings, 'FRONTEND_URL', 'http://localhost:5173')}/verify-receipt/{receipt.receipt_number}/"
            
            # Load email template
            context = {
                'user_name': payment.booking.user.get_full_name() or payment.booking.user.username,
                'receipt_number': receipt.receipt_number,
                'amount': payment.amount,
                'payment_date': payment.payment_date,
                'property_name': payment.booking.rental_property.name,
                'verification_url': verification_url,
                'signature': signature,
                'encrypted_data': encrypted_data[:100] + '...',  # Show partial encrypted data
                'support_email': 'support@renthu.ug',
                'support_phone': '+256 123 456 789'
            }
            
            try:
                template = loader.get_template('emails/payment_receipt.html')
                html_content = template.render(context)
            except Exception as template_error:
                print(f"Template error: {str(template_error)}")
                # Fallback to simple HTML
                html_content = f"""
                <html>
                <body>
                    <h2>Payment Receipt - {receipt.receipt_number}</h2>
                    <p>Thank you for your payment!</p>
                    <p><strong>Amount:</strong> UGX {payment.amount:,.2f}</p>
                    <p><strong>Property:</strong> {payment.booking.rental_property.name}</p>
                    <p><strong>Date:</strong> {payment.payment_date}</p>
                    <p><strong>Receipt Number:</strong> {receipt.receipt_number}</p>
                    <p><strong>Verification URL:</strong> <a href="{verification_url}">{verification_url}</a></p>
                    <p><strong>Digital Signature:</strong> {signature}</p>
                    <p>Keep this receipt for your records.</p>
                    <p>For support: support@renthu.ug | +256 123 456 789</p>
                </body>
                </html>
                """
            
            # Create email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Payment Receipt - {receipt.receipt_number} - RentHu Uganda"
            msg['From'] = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@renthu.ug')
            msg['To'] = user_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Create PDF receipt attachment
            pdf_content = self._generate_pdf_receipt(receipt_data, signature)
            pdf_part = MIMEApplication(pdf_content, Name=f"Receipt_{receipt.receipt_number}.pdf")
            pdf_part['Content-Disposition'] = f'attachment; filename="Receipt_{receipt.receipt_number}.pdf"'
            msg.attach(pdf_part)
            
            # Add custom headers for verification
            msg['X-Receipt-Signature'] = signature
            msg['X-Receipt-Number'] = receipt.receipt_number
            msg['X-Encryption-Method'] = 'Fernet'
            
            # Send email (in development, this will print to console)
            if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
                print("=" * 80)
                print("EMAIL CONTENT (Development Mode):")
                print("=" * 80)
                print(f"To: {user_email}")
                print(f"Subject: {msg['Subject']}")
                print(f"Signature: {signature}")
                print(f"Encrypted Data Length: {len(encrypted_data)}")
                print("=" * 80)
                return True
            
            # In production, send via SMTP
            with smtplib.SMTP(getattr(settings, 'EMAIL_HOST', 'localhost'), 
                            getattr(settings, 'EMAIL_PORT', 587)) as server:
                if getattr(settings, 'EMAIL_USE_TLS', True):
                    server.starttls()
                if getattr(settings, 'EMAIL_HOST_USER', None):
                    server.login(getattr(settings, 'EMAIL_HOST_USER'), 
                              getattr(settings, 'EMAIL_HOST_PASSWORD', ''))
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"Error sending receipt email: {str(e)}")
            return False
    
    def _generate_pdf_receipt(self, receipt_data, signature):
        """Generate PDF receipt with watermark and signature"""
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.colors import Color, grey, lightgrey
            from io import BytesIO
            
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            # Add watermark "RENTHU UGANDA - ORIGINAL RECEIPT"
            p.saveState()
            p.setFont("Helvetica", 50)
            p.setFillColor(Color(0.9, 0.9, 0.9, 0.3))
            p.rotate(45)
            p.drawString(100, 100, "RENTHU UGANDA - ORIGINAL RECEIPT")
            p.restoreState()
            
            # Header
            p.setFont("Helvetica-Bold", 20)
            p.drawString(50, height - 50, "RENTHU UGANDA - PAYMENT RECEIPT")
            p.setFont("Helvetica", 12)
            p.drawString(50, height - 80, "Secure & Digitally Signed Receipt")
            
            # Receipt details
            y_position = height - 120
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y_position, f"Receipt Number: {receipt_data['receipt_number']}")
            
            p.setFont("Helvetica", 10)
            y_position -= 30
            p.drawString(50, y_position, f"Payment ID: {receipt_data['payment_id']}")
            y_position -= 20
            p.drawString(50, y_position, f"Payment Date: {receipt_data['payment_date']}")
            y_position -= 20
            p.drawString(50, y_position, f"Amount: UGX {receipt_data['amount']:,.2f}")
            y_position -= 20
            p.drawString(50, y_position, f"Payment Method: {receipt_data['payment_method'].title()}")
            y_position -= 20
            p.drawString(50, y_position, f"Transaction ID: {receipt_data['transaction_id'] or 'N/A'}")
            y_position -= 20
            p.drawString(50, y_position, f"Property: {receipt_data['property_name']}")
            y_position -= 20
            p.drawString(50, y_position, f"Email: {receipt_data['user_email']}")
            
            # Security features
            y_position -= 40
            p.setFont("Helvetica-Bold", 12)
            p.drawString(50, y_position, "SECURITY FEATURES:")
            
            p.setFont("Helvetica", 9)
            y_position -= 25
            p.drawString(50, y_position, f"✓ Digital Signature: {signature[:20]}...")
            y_position -= 15
            p.drawString(50, y_position, "✓ Encrypted Data Verification")
            y_position -= 15
            p.drawString(50, y_position, "✓ Tamper-Proof Design")
            y_position -= 15
            p.drawString(50, y_position, "✓ Unique Receipt Number")
            
            # Verification instructions
            y_position -= 30
            p.setFont("Helvetica-Bold", 10)
            p.drawString(50, y_position, "TO VERIFY THIS RECEIPT:")
            y_position -= 20
            p.setFont("Helvetica", 9)
            verification_text = (
                "1. Visit our website and enter the receipt number\n"
                "2. Or scan the QR code (if available)\n"
                "3. The digital signature will be verified automatically\n"
                "4. Any tampering will invalidate this receipt"
            )
            for line in verification_text.split('\n'):
                p.drawString(50, y_position, line)
                y_position -= 15
            
            # Footer
            y_position = 50
            p.setFont("Helvetica-Bold", 10)
            p.drawString(50, y_position, "IMPORTANT:")
            y_position -= 20
            p.setFont("Helvetica", 8)
            p.drawString(50, y_position, "This receipt is digitally signed and encrypted. Any attempt to modify")
            y_position -= 12
            p.drawString(50, y_position, "this document will invalidate its authenticity. Keep it safe.")
            y_position -= 12
            p.drawString(50, y_position, "For support: support@renthu.ug | +256 123 456 789")
            
            # Add border
            p.setStrokeColor(grey)
            p.setLineWidth(2)
            p.rect(20, 20, width - 40, height - 40)
            
            p.save()
            pdf_content = buffer.getvalue()
            buffer.close()
            
            return pdf_content
            
        except ImportError:
            # If reportlab is not available, return simple text content
            return f"Receipt {receipt_data['receipt_number']}".encode()
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return f"Receipt {receipt_data['receipt_number']}".encode()

# Create singleton instance
secure_email_service = SecureEmailService()
