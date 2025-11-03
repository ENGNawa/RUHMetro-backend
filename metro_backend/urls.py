from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from main_app.views import RegisterView, MeView
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("main_app.urls")),

    path("api/auth/register/", RegisterView.as_view(), name='auth_register'),
    path("api/auth/login/", TokenObtainPairView.as_view(), name='auth_login'),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name='auth_refresh'),
    path("api/auth/me/", MeView.as_view(), name='auth_me'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)