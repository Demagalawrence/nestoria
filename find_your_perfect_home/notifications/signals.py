from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from bookings.models import Booking, BookingHistory
from payments.models import Payment
from properties.models import Property, PropertyReview
from .models import Notification, NotificationPreference

@receiver(post_save, sender=Booking)
def booking_notification(sender, instance, created, **kwargs):
    """Send notifications for booking events"""
    if created:
        # New booking created
        create_notification(
            user=instance.user,
            notification_type='booking_confirmed',
            title='Booking Confirmed',
            message=f'Your booking {instance.booking_reference} has been confirmed.',
            booking=instance,
            property=instance.rental_property
        )
        
        # Notify property owner
        if instance.rental_property.owner != instance.user:
            create_notification(
                user=instance.rental_property.owner,
                notification_type='booking_confirmed',
                title='New Booking Received',
                message=f'New booking {instance.booking_reference} for {instance.rental_property.name}.',
                booking=instance,
                property=instance.rental_property
            )

@receiver(pre_save, sender=Booking)
def booking_status_change_notification(sender, instance, **kwargs):
    """Send notifications for booking status changes"""
    if instance.pk:
        try:
            old_instance = Booking.objects.get(pk=instance.pk)
            if old_instance.status != instance.status:
                # Status changed
                if instance.status == 'cancelled':
                    create_notification(
                        user=instance.user,
                        notification_type='booking_cancelled',
                        title='Booking Cancelled',
                        message=f'Your booking {instance.booking_reference} has been cancelled.',
                        booking=instance,
                        property=instance.rental_property
                    )
                elif instance.status == 'confirmed' and old_instance.status == 'pending':
                    create_notification(
                        user=instance.user,
                        notification_type='booking_confirmed',
                        title='Booking Confirmed',
                        message=f'Your booking {instance.booking_reference} has been confirmed.',
                        booking=instance,
                        property=instance.rental_property
                    )
        except Booking.DoesNotExist:
            pass

@receiver(post_save, sender=Payment)
def payment_notification(sender, instance, created, **kwargs):
    """Send notifications for payment events"""
    if created or instance.payment_status == 'completed':
        if instance.payment_status == 'completed':
            if not Notification.objects.filter(
                user=instance.booking.user,
                notification_type='payment_completed',
                payment=instance
            ).exists():
                create_notification(
                    user=instance.booking.user,
                    notification_type='payment_completed',
                    title='Payment Completed',
                    message=f'Payment of {instance.amount} for booking {instance.booking.booking_reference} has been completed.',
                    booking=instance.booking,
                    property=instance.booking.rental_property,
                    payment=instance
                )

            if not PropertyReview.objects.filter(
                user=instance.booking.user,
                rental_property=instance.booking.rental_property
            ).exists() and not Notification.objects.filter(
                user=instance.booking.user,
                notification_type='review_requested',
                booking=instance.booking
            ).exists():
                create_notification(
                    user=instance.booking.user,
                    notification_type='review_requested',
                    title='Rate Your Hostel Services',
                    message=f'Your payment for {instance.booking.rental_property.name} is complete. Please rate the services you received.',
                    booking=instance.booking,
                    property=instance.booking.rental_property,
                    payment=instance
                )
            
            # Notify property owner
            if (
                instance.booking.rental_property.owner != instance.booking.user and
                not Notification.objects.filter(
                    user=instance.booking.rental_property.owner,
                    notification_type='payment_completed',
                    payment=instance
                ).exists()
            ):
                create_notification(
                    user=instance.booking.rental_property.owner,
                    notification_type='payment_completed',
                    title='Payment Received',
                    message=f'Payment of {instance.amount} received for booking {instance.booking.booking_reference}.',
                    booking=instance.booking,
                    property=instance.booking.rental_property,
                    payment=instance
                )
        elif instance.payment_status == 'failed':
            create_notification(
                user=instance.booking.user,
                notification_type='payment_failed',
                title='Payment Failed',
                message=f'Payment for booking {instance.booking.booking_reference} has failed. Please try again.',
                booking=instance.booking,
                payment=instance
            )

@receiver(post_save, sender=Property)
def property_notification(sender, instance, created, **kwargs):
    """Send notifications for property events"""
    if not created and instance.is_approved:
        try:
            old_instance = Property.objects.get(pk=instance.pk)
            if not old_instance.is_approved and instance.is_approved:
                # Property was approved
                create_notification(
                    user=instance.owner,
                    notification_type='property_approved',
                    title='Property Approved',
                    message=f'Your property {instance.name} has been approved and is now live.',
                    property=instance
                )
        except Property.DoesNotExist:
            pass

def create_notification(user, notification_type, title, message, booking=None, property=None, payment=None):
    """Helper function to create notifications"""
    try:
        preferences = NotificationPreference.objects.get(user=user)
        
        # Check if user wants this type of notification
        send_notification = True
        if notification_type in ['booking_confirmed', 'booking_cancelled'] and not preferences.booking_updates:
            send_notification = False
        elif notification_type in ['payment_completed', 'payment_failed'] and not preferences.payment_updates:
            send_notification = False
        elif notification_type in ['property_approved', 'property_rejected'] and not preferences.property_updates:
            send_notification = False
        
        if send_notification:
            Notification.objects.create(
                user=user,
                notification_type=notification_type,
                title=title,
                message=message,
                booking=booking,
                property=property,
                payment=payment
            )
    except NotificationPreference.DoesNotExist:
        # Create default preferences and send notification
        NotificationPreference.objects.create(user=user)
        Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            booking=booking,
            property=property,
            payment=payment
        )
