from django.contrib import admin
from .models import AIModel, UserAPIToken

@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'model_id', 'is_active', 'created_at')
    search_fields = ('name', 'model_id')
    list_filter = ('is_active',)

@admin.register(UserAPIToken)
class UserAPITokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username',)

# Register your models here.
