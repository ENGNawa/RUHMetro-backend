from django.db import models
from django.contrib.auth.models import User

class Line(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    color = models.CharField(max_length=7)  # "#00AEEF"

    def __str__(self):
        return f"{self.code} - {self.name}"

class Station(models.Model):
    name = models.CharField(max_length=120)
    code = models.CharField(max_length=20, unique=True)
    line = models.ForeignKey(Line, on_delete=models.CASCADE, related_name="stations")
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    lng = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return f"{self.code} - {self.name}"
    
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Place(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="places")
    nearest_station = models.ForeignKey(Station, on_delete=models.SET_NULL, null=True, blank=True, related_name="places")
    lat = models.DecimalField(max_digits=15, decimal_places=7)
    lng = models.DecimalField(max_digits=15, decimal_places=7)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="places")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name