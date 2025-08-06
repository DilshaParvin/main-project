"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),

    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),

    path('approve-restaurant/<int:user_id>/', views.approve_restaurant, name='approve_restaurant'),
    path('register/user/', views.register_user_view, name='register_user'),
    path('register/restaurant/', views.register_restaurant_view, name='register_restaurant'),
    path('', views.login_view, name='login'),      
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('restaurant/dashboard/', views.restaurant_dashboard_view, name='restaurant_dashboard'),
    path('restaurant/edit-dashboard/', views.edit_restaurant_profile_view, name='edit_restaurant_profile'),
    path('add-recipe/', views.add_recipe_view, name='add_recipe'),
    path('feed/', views.feed_view, name='feed'),
    path('explore/', views.explore_view, name='explore'), 
    path('recipe/<int:pk>/', views.recipe_detail_view, name='recipe_detail'),
    path('recipe/<int:pk>/edit/', views.edit_recipe, name='edit_recipe'),
    path('recipe/<int:pk>/delete/', views.delete_recipe, name='delete_recipe'),
    path('follow/<int:user_id>/', views.follow_user, name='follow_user'),
    path('unfollow/<int:user_id>/', views.unfollow_user, name='unfollow_user'),
    path('recipe/<int:recipe_id>/like/', views.toggle_like, name='toggle_like'),
    path('notifications/', views.all_notifications, name='all_notifications'),
    path('inbox/', views.inbox_view, name='inbox'),
    path('conversation/<int:user_id>/', views.conversation_view, name='conversation'),
    path('user/<int:user_id>/', views.public_profile, name='public_profile'),
    path('share/<int:recipe_id>/', views.share_recipe, name='share_recipe'),
    path('search-users/', views.search_users, name='search_users'),
    path('offers/create/', views.create_offer, name='create_offer'),
    path('ajax-search/', views.ajax_search, name='ajax_search'),
    path('tagged/<str:tag_name>/', views.tagged_recipes, name='tagged_recipes'),
    path('promotions/<int:promo_id>/', views.promotion_detail, name='promotion_detail'),



]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


