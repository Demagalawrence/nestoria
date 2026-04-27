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
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            # Try to find user by username or email
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            # Check if the input is an email
            if '@' in username:
                try:
                    users = User.objects.filter(email=username.lower())
                    if users.count() == 1:
                        username = users.first().username
                    elif users.count() > 1:
                        # If multiple users have the same email, try to find the one with matching username
                        # First try exact username match
                        matching_user = users.filter(username=username).first()
                        if matching_user:
                            username = matching_user.username
                        else:
                            # Otherwise prefer the first active user
                            active_users = users.filter(is_active=True)
                            if active_users.exists():
                                username = active_users.first().username
                            else:
                                username = users.first().username
                    # If no users found with that email, continue with original username
                except:
                    pass
            else:
                # If not email, try to find by username
                try:
                    user = User.objects.get(username=username)
                    username = user.username
                except User.DoesNotExist:
                    pass
            
            user = authenticate(username=username, password=password)
            
            if not user:
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
