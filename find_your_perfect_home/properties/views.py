from rest_framework import generics, status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from .models import Property, PropertyImage, PropertyVideo, Room, PropertyReview
from .serializers import (PropertySerializer, PropertyDetailSerializer, PropertyCreateSerializer,
                         PropertyImageSerializer, PropertyVideoSerializer, RoomSerializer, RoomCreateSerializer,
                         PropertyReviewSerializer)

class PropertyListView(generics.ListAPIView):
    queryset = Property.objects.filter(is_active=True, is_approved=True)
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'target_audience', 'gender_preference', 'district', 'county']
    search_fields = ['name', 'description', 'district', 'village']
    ordering_fields = ['rent_per_month', 'created_at', 'name']
    ordering = ['-created_at']

class PropertyDetailView(generics.RetrieveAPIView):
    queryset = Property.objects.filter(is_active=True)
    serializer_class = PropertyDetailSerializer
    permission_classes = [AllowAny]

class PropertyReviewListView(generics.ListAPIView):
    serializer_class = PropertyReviewSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        property_id = self.kwargs['pk']
        return PropertyReview.objects.filter(rental_property_id=property_id).order_by('-created_at')

class PropertyCreateView(generics.CreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        # Auto-approve properties created by owners
        serializer.save(owner=self.request.user, is_approved=True)

class PropertyUpdateView(generics.UpdateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)

class PropertyDeleteView(generics.DestroyAPIView):
    queryset = Property.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Property.objects.filter(owner=self.request.user)

class RoomListView(generics.ListAPIView):
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['room_type', 'status']
    
    def get_queryset(self):
        property_id = self.kwargs['pk']
        return Room.objects.filter(rental_property_id=property_id)

class RoomDetailView(generics.RetrieveAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [AllowAny]

class RoomCreateView(generics.CreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        property_id = self.kwargs['pk']
        property_obj = Property.objects.get(id=property_id, owner=self.request.user)
        serializer.save(rental_property=property_obj)

class RoomUpdateView(generics.UpdateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Room.objects.filter(rental_property__owner=self.request.user)

class RoomDeleteView(generics.DestroyAPIView):
    queryset = Room.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Room.objects.filter(rental_property__owner=self.request.user)

class PropertySearchView(generics.ListAPIView):
    serializer_class = PropertySerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'target_audience', 'gender_preference', 'district', 'county', 'furnishing']
    search_fields = ['name', 'description', 'district', 'village', 'nearby_landmarks']
    ordering_fields = ['rent_per_month', 'created_at', 'name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = Property.objects.filter(is_active=True, is_approved=True)
        
        # Custom filters
        min_rent = self.request.query_params.get('min_rent')
        max_rent = self.request.query_params.get('max_rent')
        min_rooms = self.request.query_params.get('min_rooms')
        amenities = self.request.query_params.getlist('amenities')
        
        if min_rent:
            queryset = queryset.filter(rent_per_month__gte=min_rent)
        if max_rent:
            queryset = queryset.filter(rent_per_month__lte=max_rent)
        if min_rooms:
            queryset = queryset.filter(available_rooms__gte=min_rooms)
        if amenities:
            for amenity in amenities:
                queryset = queryset.filter(amenities__contains=[amenity])
                
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(Q(district__icontains=location) | Q(village__icontains=location) | Q(county__icontains=location) | Q(address_line_1__icontains=location))
                
        audience_type = self.request.query_params.get('audience_type')
        if audience_type == 'university':
            queryset = queryset.filter(Q(target_audience='university_students') | Q(target_audience='students') | Q(name__icontains='university') | Q(name__icontains='campus') | Q(name__icontains='hostel'))
        elif audience_type == 'public':
            queryset = queryset.exclude(Q(target_audience='university_students') | Q(target_audience='students') | Q(name__icontains='university') | Q(name__icontains='campus') | Q(name__icontains='hostel'))
        
        return queryset

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_properties(request):
    properties = Property.objects.filter(owner=request.user)
    serializer = PropertySerializer(properties, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_property_image(request, pk):
    property_obj = Property.objects.get(id=pk, owner=request.user)
    serializer = PropertyImageSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(rental_property=property_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_property_video(request, pk):
    property_obj = Property.objects.get(id=pk, owner=request.user)
    serializer = PropertyVideoSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(rental_property=property_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_property_review(request, pk):
    property_obj = Property.objects.get(id=pk)
    serializer = PropertyReviewSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user, rental_property=property_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def populate_sample_properties(request):
    """
    One-time endpoint to populate sample properties.
    This should be removed after initial deployment.
    """
    try:
        from django.core.management import call_command
        call_command('create_sample_properties')
        return Response({
            'message': 'Sample properties created successfully',
            'status': 'success'
        }, status=200)
    except Exception as e:
        return Response({
            'message': f'Error creating sample properties: {str(e)}',
            'status': 'error'
        }, status=500)
