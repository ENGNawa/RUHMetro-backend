from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LineViewSet, StationViewSet

router = DefaultRouter()
router.register(r"lines", LineViewSet, basename="line")
router.register(r"stations", StationViewSet, basename="station")

urlpatterns = [path("", include(router.urls))]