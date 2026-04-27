from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import datetime, timedelta

class PropertyAnalytics(models.Model):
    property = models.OneToOneField('properties.Property', on_delete=models.CASCADE, related_name='analytics')
    
    # Booking Statistics
    total_bookings = models.PositiveIntegerField(default=0)
    confirmed_bookings = models.PositiveIntegerField(default=0)
    cancelled_bookings = models.PositiveIntegerField(default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    
    # Revenue Statistics
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    monthly_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    average_booking_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Occupancy Statistics
    occupancy_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_stay_duration = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Performance Metrics
    views_count = models.PositiveIntegerField(default=0)
    inquiries_count = models.PositiveIntegerField(default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Rating Statistics
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.PositiveIntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['property']),
            models.Index(fields=['total_revenue']),
            models.Index(fields=['occupancy_rate']),
        ]
    
    def __str__(self):
        return f"{self.property.name} - Analytics"
    
    def update_analytics(self):
        """Update analytics based on current data"""
        from bookings.models import Booking
        from properties.models import PropertyReview
        
        # Booking stats
        bookings = Booking.objects.filter(rental_property=self.property)
        self.total_bookings = bookings.count()
        self.confirmed_bookings = bookings.filter(status='confirmed').count()
        self.cancelled_bookings = bookings.filter(status='cancelled').count()
        self.completed_bookings = bookings.filter(status='completed').count()
        
        # Revenue stats
        completed_bookings = bookings.filter(status='completed')
        self.total_revenue = sum(b.final_amount for b in completed_bookings)
        
        # Monthly revenue (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        recent_bookings = completed_bookings.filter(created_at__gte=thirty_days_ago)
        self.monthly_revenue = sum(b.final_amount for b in recent_bookings)
        
        if self.completed_bookings > 0:
            self.average_booking_value = self.total_revenue / self.completed_bookings
        
        # Occupancy rate
        if self.property.total_rooms > 0:
            occupied_rooms = self.property.total_rooms - self.property.available_rooms
            self.occupancy_rate = (occupied_rooms / self.property.total_rooms) * 100
        
        # Rating stats
        reviews = PropertyReview.objects.filter(rental_property=self.property)
        self.total_reviews = reviews.count()
        if self.total_reviews > 0:
            total_rating = sum(r.rating for r in reviews)
            self.average_rating = total_rating / self.total_reviews
        
        # Conversion rate
        if self.views_count > 0:
            self.conversion_rate = (self.confirmed_bookings / self.views_count) * 100
        
        self.save()

class PlatformAnalytics(models.Model):
    date = models.DateField(unique=True)
    
    # User Statistics
    new_users = models.PositiveIntegerField(default=0)
    active_users = models.PositiveIntegerField(default=0)
    total_users = models.PositiveIntegerField(default=0)
    
    # Property Statistics
    new_properties = models.PositiveIntegerField(default=0)
    total_properties = models.PositiveIntegerField(default=0)
    approved_properties = models.PositiveIntegerField(default=0)
    
    # Booking Statistics
    new_bookings = models.PositiveIntegerField(default=0)
    confirmed_bookings = models.PositiveIntegerField(default=0)
    completed_bookings = models.PositiveIntegerField(default=0)
    
    # Revenue Statistics
    daily_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    commission_earned = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Platform Activity
    page_views = models.PositiveIntegerField(default=0)
    search_queries = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['daily_revenue']),
        ]
    
    def __str__(self):
        return f"Analytics - {self.date}"

class UserActivity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Related objects
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE, null=True, blank=True)
    booking = models.ForeignKey('bookings.Booking', on_delete=models.CASCADE, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.activity_type}"
