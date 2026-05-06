from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserDocument

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 
                 'role', 'user_type', 'contact_number', 'date_of_birth', 'gender']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Validate email format
        email = attrs.get('email')
        if email and '@' not in email:
            raise serializers.ValidationError("Please enter a valid email address")
            
        # Check if username already exists
        username = attrs.get('username')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username already exists")
            
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already registered")
            
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
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
