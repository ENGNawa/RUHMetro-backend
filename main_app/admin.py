from django.contrib import admin
from .models import Line, Station, Category, Place, Post

admin.site.register(Line)
admin.site.register(Station)
admin.site.register(Category)
admin.site.register(Place)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_by", "station", "place", "created_at")
    search_fields = ("title", "body")
    list_filter = ("station", "place", "created_by")