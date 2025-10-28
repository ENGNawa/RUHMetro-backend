from rest_framework import serializers
from .models import Line, Station

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