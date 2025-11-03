from rest_framework import serializers
from .models import Line, Station, Category, Place, Post
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    class Meta:
        model = User
        fields = ("username", "email", "password")
    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
class LineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Line
        fields = ["id", "name", "code", "color"]

class StationSerializer(serializers.ModelSerializer):
    line = LineSerializer(read_only=True)
    line_id = serializers.PrimaryKeyRelatedField(
        queryset=Line.objects.all(), source="line", write_only=True
    )
    class Meta:
        model = Station
        fields = ["id", "name", "code", "lat", "lng", "line", "line_id"]

class MeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "is_staff", "is_superuser"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "code"]

class StationMiniSerializer(serializers.ModelSerializer):
    line = serializers.CharField(source="line.code", read_only=True)
    class Meta:
        model = Station
        fields = ["id", "name", "code", "line"]

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "code"]

class PlaceSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source="category", read_only=True)
    nearest_station_detail = StationMiniSerializer(source="nearest_station", read_only=True)
    distance_km = serializers.FloatField(read_only=True)

    class Meta:
        model = Place
        fields = [
            "id", "name", "description",
            "category", "category_detail",
            "nearest_station", "nearest_station_detail",
            "lat", "lng",
            "created_by", "created_at",
            "distance_km",
        ]
        read_only_fields = ["created_by", "created_at", "distance_km"]

    def validate(self, attrs):
        lat = attrs.get("lat", getattr(self.instance, "lat", None))
        lng = attrs.get("lng", getattr(self.instance, "lng", None))
        if lat is None or lng is None:
            raise ValidationError("lat and lng are required")
        if not (-90 <= float(lat) <= 90):
            raise ValidationError("lat must be between -90 and 90")
        if not (-180 <= float(lng) <= 180):
            raise ValidationError("lng must be between -180 and 180")
        return attrs

class PostSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id", "title", "body", "image",
            "station", "place",
            "created_by", "author",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_by", "author", "created_at", "updated_at"]
