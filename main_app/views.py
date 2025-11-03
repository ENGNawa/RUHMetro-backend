from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework import status
from django.db.models import QuerySet, Q, Count, Avg
from .models import Line, Station, Category, Place, Post, Comment, Rating
from .serializers import LineSerializer, StationSerializer, RegisterSerializer, MeSerializer, CategorySerializer, PlaceSerializer, PostSerializer, CommentSerializer, RatingSerializer, PostPublicSerializer, PostOwnerSerializer
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
import math

class RegisterView(APIView):
    def post(self, request):
        s = RegisterSerializer(data=request.data)
        if s.is_valid():
            user = s.save()
            return Response({"message": "User registered", "username": user.username}, status=201)
        return Response(s.errors, status=400)

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        s = MeSerializer(request.user)
        return Response(s.data, status=200)
    
class LineViewSet(viewsets.ModelViewSet):
    queryset = Line.objects.all().order_by("code")
    serializer_class = LineSerializer
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=True, methods=["get"], url_path="stations")
    def stations(self, request, pk=None):
        qs = Station.objects.select_related("line").filter(line_id=pk).order_by("code")
        data = StationSerializer(qs, many=True).data
        return Response(data, status=200)
    
class StationViewSet(viewsets.ModelViewSet):
    queryset: QuerySet[Station] = Station.objects.select_related("line").all().order_by("code")
    serializer_class = StationSerializer
    permission_classes = [IsAdminOrReadOnly]

# got the idea from a github example about nearest location
# it uses lat & lng with haversine formula to find closest stations
# ref: https://stackoverflow.com/questions/29765052/how-to-get-the-nearest-location-entries-from-a-database
   
    @action(detail=False, methods=["get"], url_path="nearest")
    def nearest(self, request):
        try:
            lat = float(request.query_params.get("lat"))
            lng = float(request.query_params.get("lng"))
        except (TypeError, ValueError):
            return Response({"error :"}, status=400)

        limit = int(request.query_params.get("limit", 1))
        R = 6371.0

        def haversine(lat1, lon1, lat2, lon2):
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
            return 2*R*math.asin(math.sqrt(a))

        stations = []
        for s in Station.objects.select_related("line").all():
            d = haversine(lat, lng, float(s.lat), float(s.lng))
            stations.append((d, s))
        stations.sort(key=lambda x: x[0])

        data = []
        for d, s in stations[:limit]:
            item = StationSerializer(s).data
            item["distance_km"] = round(d, 3)
            data.append(item)
        return Response(data, status=200)
    
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(float, (lat1, lon1, lat2, lon2))
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2*R*math.asin(math.sqrt(a))

class PlaceViewSet(viewsets.ModelViewSet):
    queryset = Place.objects.select_related(
        "category", "nearest_station", "nearest_station__line"
    ).all()
    serializer_class = PlaceSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()

        cat_id = request.query_params.get("category_id")
        if cat_id:
            qs = qs.filter(category_id=cat_id)

        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")

        data = PlaceSerializer(qs, many=True).data
        if lat and lng:
            try:
                lat = float(lat)
                lng = float(lng)
            except ValueError:
                return Response(data, status=200)

            for item in data:
                try:
                    d = haversine_km(lat, lng, float(item["lat"]), float(item["lng"]))
                    item["distance_km"] = round(d, 3)
                except:
                    item["distance_km"] = None

            data.sort(key=lambda x: (x.get("distance_km") is None, x.get("distance_km")))

        return Response(data, status=200)
    

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.select_related("station","place","created_by").all()
    serializer_class = PostSerializer
    permission_classes = [IsOwnerOrAdminOrReadOnly]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == "list" and not self.request.user.is_staff:
            qs = qs.filter(created_by=self.request.user)

        q = self.request.query_params.get("q")
        station_id = self.request.query_params.get("station_id")
        place_id = self.request.query_params.get("place_id")
        if q:
            qs = qs.filter(Q(title_icontains=q) | Q(body_icontains=q))
        if station_id:
            qs = qs.filter(station_id=station_id)
        if place_id:
            qs = qs.filter(place_id=place_id)

        if self.action == "list":
            qs = qs.annotate(
                comments_count=Count("comments"),
                ratings_count=Count("ratings"),
                avg_rating=Avg("ratings__value"),
            ).order_by("-created_at")
        else:
            qs = qs.order_by("-created_at")
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return PostOwnerSerializer
        return PostSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ExploreViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PostPublicSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        qs = (
            Post.objects.filter(is_public=True)
            .select_related("created_by", "station", "place")
            .annotate(
                comments_count=Count("comments"),
                ratings_count=Count("ratings"),
                avg_rating=Avg("ratings__value"),
            )
            .order_by("-created_at")
        )
        q = self.request.query_params.get("q")
        place_id = self.request.query_params.get("place_id")
        station_id = self.request.query_params.get("station_id")
        if q:
            qs = qs.filter(Q(title_icontains=q) | Q(body_icontains=q))
        if place_id:
            qs = qs.filter(place_id=place_id)
        if station_id:
            qs = qs.filter(station_id=station_id)
        return qs

class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    def get_queryset(self):
        qs = Comment.objects.select_related("created_by","post")
        post_id = self.request.query_params.get("post_id")
        if post_id:
            qs = qs.filter(post_id=post_id)
        return qs
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        qs = Rating.objects.select_related("created_by","post")
        post_id = self.request.query_params.get("post_id")
        if post_id:
            qs = qs.filter(post_id=post_id)
        return qs.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        obj, _created = Rating.objects.update_or_create(
            post=serializer.validated_data["post"],
            created_by=self.request.user,
            defaults={"value": serializer.validated_data["value"]},
        )
        self.instance = obj

    def create(self, request, *args, **kwargs):
        s = self.get_serializer(data=request.data)
        s.is_valid(raise_exception=True)
        self.perform_create(s)
        return Response(self.get_serializer(self.instance).data, status=status.HTTP_201_CREATED)