from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LineViewSet, StationViewSet, RegisterView, MeView, CategoryViewSet, PlaceViewSet, PostViewSet

router = DefaultRouter()
router.register(r"lines", LineViewSet, basename="line")
router.register(r"stations", StationViewSet, basename="station")
router.register("categories", CategoryViewSet, basename="categories")
router.register(r"places", PlaceViewSet, basename="places")
router.register(r"posts", PostViewSet, basename="post")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/me/", MeView.as_view(), name="auth-me"),
    path("", include(router.urls))
    
    ]