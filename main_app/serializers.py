from rest_framework import serializers
from .models import Line, Station
from django.contrib.auth.models import User

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
        fields = ["id", "username", "email"]