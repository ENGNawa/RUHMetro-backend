from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainView, TokenRefreshView
from main_app.views import RegisterView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("main_app.urls")),

    path("api/auth/register/", RegisterView.as_view(), name='auth_register'),
    path("api/auth/login/", TokenObtainView.as_view(), name='auth_login'),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name='auth_refresh'),
]