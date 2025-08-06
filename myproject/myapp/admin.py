from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):  # ✅ Inherit from UserAdmin
    list_display = ('username', 'user_type', 'is_approved', 'restaurant_name')
    list_filter = ('user_type', 'is_approved')
    actions = ['approve_restaurants']

    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('user_type', 'restaurant_name', 'restaurant_location', 'is_approved', 'profile_picture', 'bio'),
        }),
    )

    def approve_restaurants(self, request, queryset):
        updated = queryset.filter(user_type='restaurant').update(is_approved=True)
        self.message_user(request, f"{updated} restaurant(s) approved.")
