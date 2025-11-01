from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import QuerySet
from .models import Line, Station
from .serializers import LineSerializer, StationSerializer, RegisterSerializer, MeSerializer
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

    @action(detail=True, methods=["get"], url_path="stations")
    def stations(self, request, pk=None):
        qs = Station.objects.select_related("line").filter(line_id=pk).order_by("code")
        data = StationSerializer(qs, many=True).data
        return Response(data, status=200)
    
class StationViewSet(viewsets.ModelViewSet):
    queryset: QuerySet[Station] = Station.objects.select_related("line").all().order_by("code")
    serializer_class = StationSerializer

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