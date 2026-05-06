from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('owner', 'Property Owner'),
        ('admin', 'Admin'),
        ('agent', 'Real Estate Agent'),
    ]
    
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('professional', 'Working Professional'),
        ('family', 'Family'),
        ('business', 'Business Traveler'),
        ('expatriate', 'Expatriate'),
        ('retired', 'Retired Person'),
        ('other', 'Other'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='tenant')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, blank=True, null=True)
    contact_number = models.CharField(max_length=20, blank=True)
    alternate_number = models.CharField(max_length=20, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, help_text="Personal phone number for students")
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        blank=True
    )
    occupation = models.CharField(max_length=100, blank=True)
    company_name = models.CharField(max_length=200, blank=True)
    annual_income = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    id_proof_type = models.CharField(
        max_length=20,
        choices=[
            ('aadhaar', 'Aadhaar Card'),
            ('passport', 'Passport'),
            ('driving_license', 'Driving License'),
            ('voter_id', 'Voter ID'),
            ('pan_card', 'PAN Card'),
        ],
        blank=True
    )
    id_proof_number = models.CharField(max_length=50, blank=True)
    id_proof_document = models.FileField(upload_to='id_proofs/', blank=True, null=True)
    permanent_address = models.TextField(blank=True)
    current_address = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_number = models.CharField(max_length=20, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    is_verified = models.BooleanField(default=False)
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('verified', 'Verified'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    verification_documents = models.JSONField(default=list)
    preferences = models.JSONField(default=dict)  # Store user preferences like location, budget, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)
    secret_key = models.CharField(max_length=100, blank=True, null=True, help_text="Admin secret key for secure login")
    
    def __str__(self):
        return f"{self.username} ({self.role})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def age(self):
        from django.utils import timezone
        if self.date_of_birth:
            return int((timezone.now().date() - self.date_of_birth).days / 365.25)
        return None

class UserDocument(models.Model):
    DOCUMENT_TYPES = [
        ('profile_pic', 'Profile Picture'),
        ('id_proof', 'ID Proof'),
        ('address_proof', 'Address Proof'),
        ('income_proof', 'Income Proof'),
        ('student_id', 'Student ID'),
        ('company_id', 'Company ID'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document = models.FileField(upload_to='user_documents/')
    document_number = models.CharField(max_length=100, blank=True)
    expiry_date = models.DateField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.document_type}"
