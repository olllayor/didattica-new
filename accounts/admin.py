from django.contrib import admin
from .models import Profile

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'website', 'created_at', 'updated_at')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'bio', 'website')
    date_hierarchy = 'created_at'