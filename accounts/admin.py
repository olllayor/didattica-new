from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

# Inline admin descriptor for Profile model
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profiles'
    fk_name = 'user'
    fields = ('name', 'bio', 'profile_image', 'website', 'followers', 'following')

# Custom UserAdmin to include ProfileInline
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_name', 'get_followers_count', 'get_following_count')
    list_select_related = ('profile',)

    def get_name(self, instance):
        return instance.profile.name
    get_name.short_description = 'Name'

    def get_followers_count(self, instance):
        return instance.profile.followers.count()
    get_followers_count.short_description = 'Followers'

    def get_following_count(self, instance):
        return instance.profile.following.count()
    get_following_count.short_description = 'Following'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

# Unregister the default UserAdmin and register the custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'bio', 'website', 'created_at', 'updated_at', 'get_followers_count', 'get_following_count')
    list_filter = ('created_at', 'user')
    search_fields = ('user__username', 'bio', 'website')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at', 'get_followers_count', 'get_following_count')

    def get_followers_count(self, instance):
        return instance.followers.count()
    get_followers_count.short_description = 'Followers'

    def get_following_count(self, instance):
        return instance.following.count()
    get_following_count.short_description = 'Following'