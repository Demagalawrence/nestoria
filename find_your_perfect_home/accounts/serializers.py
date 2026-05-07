from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserDocument

class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    secret_key = serializers.CharField(required=False, allow_blank=True, write_only=True)
    national_id_card = serializers.FileField(required=False, write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 
                 'role', 'user_type', 'contact_number', 'alternate_number', 'profile_picture',
                 'date_of_birth', 'gender', 'occupation', 'company_name', 'annual_income',
                 'id_proof_type', 'id_proof_number', 'id_proof_document', 'national_id_card',
                 'permanent_address', 'current_address', 'emergency_contact_name',
                 'emergency_contact_number', 'emergency_contact_relation', 'secret_key']
    
    def validate(self, attrs):
        if not attrs.get('confirm_password'):
            attrs['confirm_password'] = attrs.get('password')

        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Validate email format
        email = attrs.get('email')
        if email and '@' not in email:
            raise serializers.ValidationError("Please enter a valid email address")
            
        # Check if username already exists
        username_was_provided = bool(attrs.get('username'))
        username = attrs.get('username') or (email.split('@')[0] if email else '')
        if not username:
            raise serializers.ValidationError("Username or email is required")

        if username_was_provided and User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists")

        if not username_was_provided:
            base_username = username
            suffix = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{suffix}"
                suffix += 1
            attrs['username'] = username
            
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already registered")
        
        # Handle secret key for admin users
        role = attrs.get('role')
        secret_key = attrs.get('secret_key', '')
        if role == 'admin':
            if not secret_key:
                raise serializers.ValidationError("Admin users must provide a secret key")
            # You can add validation for the secret key here if needed
            
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        national_id_card = validated_data.pop('national_id_card', None)
        if national_id_card and not validated_data.get('id_proof_document'):
            validated_data['id_proof_document'] = national_id_card
            validated_data.setdefault('id_proof_type', 'other')
        try:
            user = User.objects.create_user(**validated_data)
            return user
        except Exception as e:
            raise serializers.ValidationError(f"Registration failed: {str(e)}")

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Simple user lookup - try username first, then email
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Try to find user by username
            user = User.objects.filter(username=username).first()
            
            # If not found by username, try email
            if not user:
                user = User.objects.filter(email=username).first()
            
            # Authenticate the user
            if user and user.check_password(password):
                return {'user': user}
            else:
                raise serializers.ValidationError('Invalid credentials')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include username and password')
        
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name', 'age',
                 'role', 'user_type', 'contact_number', 'alternate_number', 'profile_picture',
                 'date_of_birth', 'gender', 'occupation', 'company_name', 'annual_income',
                 'permanent_address', 'current_address', 'emergency_contact_name',
                 'emergency_contact_number', 'emergency_contact_relation', 'is_verified',
                 'verification_status', 'email_verified', 'phone_verified', 'created_at']
        read_only_fields = ['id', 'username', 'email_verified', 'phone_verified', 
                           'is_verified', 'verification_status', 'created_at']

class UserDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDocument
        fields = ['id', 'document_type', 'document', 'document_number', 'expiry_date', 
                 'is_verified', 'uploaded_at']
        read_only_fields = ['id', 'is_verified', 'uploaded_at']
