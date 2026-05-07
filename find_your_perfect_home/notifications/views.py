from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Notification, NotificationTemplate, NotificationPreference
from .serializers import NotificationSerializer, NotificationTemplateSerializer, NotificationPreferenceSerializer

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type', 'channel', 'is_read']
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return Response({'message': 'Notification marked as read'})
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True, 
        read_at=timezone.now()
    )
    return Response({'message': 'All notifications marked as read'})

class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preference

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_statistics(request):
    user = request.user
    notifications = Notification.objects.filter(user=user)
    
    stats = {
        'total_notifications': notifications.count(),
        'unread_notifications': notifications.filter(is_read=False).count(),
        'email_notifications': notifications.filter(channel='email').count(),
        'sms_notifications': notifications.filter(channel='sms').count(),
        'push_notifications': notifications.filter(channel='push').count(),
        'by_type': {}
    }
    
    # Count by notification type
    for notification_type, _ in Notification.NOTIFICATION_TYPES:
        stats['by_type'][notification_type] = notifications.filter(
            notification_type=notification_type
        ).count()
    
    return Response(stats)

# Admin views for notification templates
class NotificationTemplateListView(generics.ListAPIView):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return NotificationTemplate.objects.all()
        return NotificationTemplate.objects.none()

class NotificationTemplateDetailView(generics.RetrieveUpdateAPIView):
    queryset = NotificationTemplate.objects.all()
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role == 'admin':
            return NotificationTemplate.objects.all()
        return NotificationTemplate.objects.none()
