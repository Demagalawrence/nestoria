from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserDocument

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'role', 'user_type', 'is_verified', 'created_at')
    list_filter = ('role', 'user_type', 'is_verified', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'contact_number')
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'contact_number', 'alternate_number', 'date_of_birth', 'gender')}),
        ('Profile', {'fields': ('profile_picture', 'occupation', 'company_name', 'annual_income')}),
        ('Role & Type', {'fields': ('role', 'user_type')}),
        ('Address', {'fields': ('permanent_address', 'current_address')}),
        ('Emergency Contact', {'fields': ('emergency_contact_name', 'emergency_contact_number', 'emergency_contact_relation')}),
        ('Verification', {'fields': ('email_verified', 'phone_verified', 'is_verified', 'verification_status', 'verification_documents')}),
        ('Preferences', {'fields': ('preferences',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at', 'last_login_ip')}),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login_ip')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role', 'user_type'),
        }),
    )

@admin.register(UserDocument)
class UserDocumentAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'document_number', 'is_verified', 'uploaded_at')
    list_filter = ('document_type', 'is_verified')
    search_fields = ('user__username', 'document_number', 'document_name')
    readonly_fields = ('uploaded_at',)
