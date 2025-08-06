from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import CustomUser, Recipe, Tag, Message, SpecialOffer
from django.utils.text import slugify
from django.db.models import Q
from django.templatetags.static import static
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_POST


User = get_user_model()

# --- User Registration View ---
@never_cache
def register_user_view(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'register_user.html', {'error': "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, 'register_user.html', {'error': "Username already exists"})

        if User.objects.filter(email=email).exists():
            return render(request, 'register_user.html', {'error': "Email already registered"})

        user = User.objects.create_user(username=username, email=email, password=password1, user_type='user')

        if full_name:
            parts = full_name.split()
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = ' '.join(parts[1:])
        user.save()

        login(request, user)
        request.session['user_id'] = user.id
        return redirect('login')

    return render(request, 'register_user.html')



# --- Restaurant Registration View ---
@never_cache
def register_restaurant_view(request):
    if request.method == 'POST':
        restaurant_name = request.POST.get('restaurant_name').strip()
        restaurant_location = request.POST.get('restaurant_location').strip()
        username = request.POST.get('username').strip()
        email = request.POST.get('email').strip()
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            return render(request, 'register_restaurant.html', {'error': "Passwords do not match"})

        if User.objects.filter(username=username).exists():
            return render(request, 'register_restaurant.html', {'error': "Username already exists"})

        if User.objects.filter(email=email).exists():
            return render(request, 'register_restaurant.html', {'error': "Email already registered"})

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password1,
            user_type='restaurant',
            restaurant_name=restaurant_name,
            restaurant_location=restaurant_location,
            is_approved=False
        )
        user.save()
        login(request, user)
        request.session['user_id'] = user.id
        return redirect('login')

    return render(request, 'register_restaurant.html')

# ------------------ LOGIN ------------------
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            request.session['user_id'] = user.id
            request.session['username'] = user.username
            request.session.set_expiry(60 * 60 * 24 * 7)  # 7 days

            if user.is_superuser or user.is_staff:
                return redirect('admin_dashboard')

            return redirect('restaurant_dashboard' if user.user_type == 'restaurant' else 'feed')
        return render(request, 'login.html', {'error': 'Invalid credentials'})
    return render(request, 'login.html')


# ------------------ LOGOUT ------------------
@never_cache
def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('login')



# ----------------ADMIN DASHBOARD-----------------

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
@never_cache
def admin_dashboard(request):
    users = User.objects.filter(user_type='user')
    restaurants = User.objects.filter(user_type='restaurant', is_approved=True)
    pending_restaurants = User.objects.filter(user_type='restaurant', is_approved=False)
    return render(request, 'admin_dashboard.html', {
        'users': users,
        'restaurants': restaurants,
        'pending_restaurants': pending_restaurants
    })




@require_POST
@user_passes_test(is_admin)
def approve_restaurant(request, user_id):
    restaurant = get_object_or_404(User, id=user_id, user_type='restaurant')
    restaurant.is_approved = True
    restaurant.save()
    return redirect('admin_dashboard')

@require_POST
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    
    # Optional: prevent admin from deleting their own account
    if request.user == user:
        return redirect('admin_dashboard')  # or show an error message

    user.delete()
    return redirect('admin_dashboard')



# ------------------ PROFILE VIEW FOR USER ------------------

@login_required
@never_cache
def profile_view(request):
    user = request.user
    if user.user_type == 'restaurant':
        return redirect('restaurant_dashboard')
    return render(request, 'profile.html', {'user': user})


@login_required
def edit_profile_view(request):
    user = request.user

    # Redirect restaurant users to their own edit page
    if user.user_type == 'restaurant':
        return redirect('edit_restaurant_profile')

    if request.method == 'POST':
        full_name = request.POST.get('full_name', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        bio = request.POST.get('bio', '').strip()

        # Name split
        if full_name:
            name_parts = full_name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''

        # Optional: prevent duplicate usernames/emails
        if User.objects.exclude(pk=user.pk).filter(username=username).exists():
            messages.error(request, "Username is already taken.")
            return render(request, 'edit_profile.html', {'user': user})
        if User.objects.exclude(pk=user.pk).filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, 'edit_profile.html', {'user': user})

        # Update profile fields
        user.username = username
        user.email = email
        user.bio = bio

        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('profile')

    return render(request, 'edit_profile.html', {'user': user})


# ------------------ RESTAURANT DASHBOARD ------------------
@login_required
@never_cache
def restaurant_dashboard_view(request):
    user = request.user

    if user.user_type != 'restaurant':
        return redirect('profile')

    if not user.is_approved:
        return render(request, 'not_approved.html')

    recipes = Recipe.objects.filter(author=user)
    promotions = SpecialOffer.objects.filter(restaurant=user).order_by('-start_date')
    unread_notification_count = user.notifications.filter(is_read=False).count()

    return render(request, 'restaurant_dashboard.html', {
        'user': user,
        'recipes': recipes,
        'promotions': promotions,
        'unread_notification_count': unread_notification_count,
    })

@login_required
def edit_restaurant_profile_view(request):
    user = request.user
    if user.user_type != 'restaurant':
        messages.error(request, "Access denied.")
        return redirect('profile')

    if request.method == 'POST':
        user.restaurant_name = request.POST.get('restaurant_name')
        user.restaurant_location = request.POST.get('restaurant_location')
        user.bio = request.POST.get('bio')
        user.contact_number = request.POST.get('contact_number')
        user.opening_hours = request.POST.get('opening_hours')

        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('restaurant_dashboard')

    return render(request, 'edit_restaurant_profile.html', {'user': user})

# ------------------ RECIPE ADD/EDIT/DELETE ------------------
@login_required
def add_recipe_view(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        ingredients = request.POST.get('ingredients')
        instructions = request.POST.get('instructions')
        cook_time = request.POST.get('cook_time')
        servings = request.POST.get('servings')
        difficulty = request.POST.get('difficulty')
        image = request.FILES.get('image')
        tag_input = request.POST.get('tags')
        is_promoted = request.POST.get('is_promoted') == 'on'

        recipe = Recipe.objects.create(
            title=title,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            cook_time=cook_time,
            servings=servings,
            difficulty=difficulty,
            image=image,
            author=request.user,
            is_promoted=is_promoted if request.user.user_type == 'restaurant' else False
        )

        if tag_input:
            tag_names = [t.strip().lower() for t in tag_input.split(',') if t.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                recipe.tags.add(tag)

        return redirect('feed')

    return render(request, 'add_recipe.html')

@login_required
def edit_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)

    if request.method == 'POST':
        recipe.title = request.POST.get('title')
        recipe.description = request.POST.get('description')
        recipe.ingredients = request.POST.get('ingredients')
        recipe.instructions = request.POST.get('instructions')
        recipe.cook_time = request.POST.get('cook_time')
        recipe.servings = request.POST.get('servings')
        recipe.difficulty = request.POST.get('difficulty')
        recipe.is_promoted = bool(request.POST.get('is_promoted'))

        if 'image' in request.FILES:
            recipe.image = request.FILES['image']

        recipe.save()
        return redirect('profile')

    return render(request, 'edit_recipe.html', {'recipe': recipe})

@login_required
def delete_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)

    if request.method == 'POST':
        recipe.delete()
        return redirect('profile')

    return render(request, 'delete_recipe.html', {'recipe': recipe})

# ------------------ FEED ------------------

from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Recipe, SpecialOffer, CustomUser

@never_cache
@login_required
def feed_view(request):
    # Get the list of user IDs the current user follows
    followed_user_ids = list(request.user.following.values_list('id', flat=True))
    
    # Include current user ID as well to show their own recipes
    relevant_user_ids = followed_user_ids + [request.user.id]

    # Only show recipes from followed users and the current user
    recipes = Recipe.objects.filter(author__id__in=relevant_user_ids).order_by('-created_at')

    # Promoted recipes (optional: you could also filter by relevant_user_ids if needed)
    promoted_recipes = Recipe.objects.filter(is_promoted=True).order_by('-updated_at')[:5]

    # Only show active and non-expired promotions
    promotions = SpecialOffer.objects.filter(
        is_active=True,
        end_date__gte=timezone.now().date()
    ).order_by('-start_date')[:5]

    # Suggest other users to follow
    other_users = CustomUser.objects.exclude(id=request.user.id)[:5]

    return render(request, 'feed.html', {
        'recipes': recipes,
        'promoted_recipes': promoted_recipes,
        'promotions': promotions,
        'other_users': other_users,
        'followed_user_ids': followed_user_ids,
    })







#---------------PUBLIC FEED----------------
@login_required
@never_cache
def explore_view(request):
    followed_user_ids = list(request.user.following.values_list('id', flat=True))

    # Exclude recipes from followed users and the current user
    explore_recipes = Recipe.objects.exclude(
        author__id__in=followed_user_ids + [request.user.id]
    ).order_by('-created_at')

    return render(request, 'explore.html', {
        'explore_recipes': explore_recipes
    })





@login_required
def recipe_detail_view(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    return render(request, 'recipe_detail.html', {'recipe': recipe})





# -------------FOLLOW/UNFOLLOW USER------------------

from django.http import JsonResponse

@login_required
def follow_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, id=user_id)
        if target_user != request.user:
            if target_user in request.user.following.all():
                request.user.following.remove(target_user)
                return JsonResponse({'status': 'unfollowed'})
            else:
                request.user.following.add(target_user)

                # Notification: Wrap in try-except to avoid crashing if Notification fails
                try:
                    Notification.objects.create(
                        user=target_user,
                        message=f"{request.user.username} started following you."
                    )
                except Exception as e:
                    print("Notification error:", e)  # Optional: log error

                return JsonResponse({'status': 'followed'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def unfollow_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(CustomUser, id=user_id)
        if target_user != request.user:
            request.user.following.remove(target_user)
        return JsonResponse({'status': 'unfollowed'})




# ----------------LIKE/UNLIKE--------------------
from django.http import JsonResponse
from .models import Like, Notification

@login_required
def toggle_like(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    like, created = Like.objects.get_or_create(user=request.user, recipe=recipe)

    if not created:
        like.delete()
        liked = False
    else:
        liked = True
        if recipe.author != request.user:
            Notification.objects.create(
            to_user=recipe.author,
            from_user=request.user,
            notification_type='like',
            recipe=recipe,
            message=f"{request.user.get_display_name()} liked your recipe '{recipe.title}'."
            )  

    return JsonResponse({
        'liked': liked,
        'likes_count': recipe.likes.count()
    })




# -----------NOTIFICATION------------

@login_required
def all_notifications(request):
    user_notifications = request.user.notifications.all()
    user_notifications.update(is_read=True)
    return render(request, 'notifications/all.html', {'notifications': user_notifications})





# ----------------DM--------------------



def inbox_view(request):
    # Get all users who have sent or received messages with the current user
    messages = Message.objects.filter(Q(sender=request.user) | Q(recipient=request.user))
    user_ids = set()

    for msg in messages:
        if msg.sender != request.user:
            user_ids.add(msg.sender.id)
        if msg.recipient != request.user:
            user_ids.add(msg.recipient.id)

    users = User.objects.filter(id__in=user_ids)
    conversations = []

    for user in users:
        last_msg = Message.objects.filter(
            Q(sender=request.user, recipient=user) |
            Q(sender=user, recipient=request.user)
        ).order_by('-timestamp').first()

        unread = Message.objects.filter(sender=user, recipient=request.user, is_read=False).count()

        conversations.append({
            'id': user.id,
            'username': user.username,
            'profile_picture': getattr(user, 'profile_picture', None),
            'last_message': last_msg.message if last_msg else "",
            'unread_count': unread,
        })

    return render(request, 'messaging/inbox.html', {'conversations': conversations})


@login_required
def conversation_view(request, user_id):
    other_user = get_object_or_404(CustomUser, id=user_id)
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) | 
        Q(sender=other_user, recipient=request.user)
    ).order_by('timestamp')

    # Mark unread messages as read
    unread_messages = messages.filter(recipient=request.user, is_read=False)
    unread_messages.update(is_read=True)

    if request.method == 'POST':
        content = request.POST.get('message')
        recipe_id = request.POST.get('recipe_id')
        recipe = Recipe.objects.get(id=recipe_id) if recipe_id else None

        if content or recipe:
            Message.objects.create(
                sender=request.user,
                recipient=other_user,
                message=content,
                recipe=recipe
            )
        return redirect('conversation', user_id=other_user.id)

    return render(request, 'messaging/conversation.html', {
        'other_user': other_user,
        'messages': messages,
    })






# ----------PUBLIC PROFILE--------------
@login_required
def public_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    recipes = Recipe.objects.filter(author=user)
    is_following = request.user in user.followers.all()

    offers = []
    if user.user_type == 'restaurant':
        offers = SpecialOffer.objects.filter(restaurant=user, is_active=True)
    return render(request, 'public_profile.html', {
        'profile_user': user,
        'recipes': recipes,
        'is_following': is_following,
        'offers': offers
    })



# ------------------SHARE--------------------

@login_required
def share_recipe(request, recipe_id):
    if request.method == 'POST':
        recipient_id = request.POST.get('recipient_id')
        text = request.POST.get('text')
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        recipient = get_object_or_404(User, pk=recipient_id)

        Message.objects.create(
            sender=request.user,
            recipient=recipient,
            text=text,
            recipe=recipe
        )
        return redirect('conversation', user_id=recipient.id)
    


@login_required
def search_users(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(Q(username__icontains=query) | Q(first_name__icontains=query))\
                        .exclude(id=request.user.id)[:10]
    
    results = []
    for user in users:
        profile_pic = user.profile_picture.url if user.profile_picture else static('images/default-avatar.png')
        results.append({
            'id': user.id,
            'username': user.username,
            'profile_picture': profile_pic
        })

    return JsonResponse({'results': results})





# --------------???? FUNCTION------------------
# @login_required
# def user_search(request):
#     query = request.GET.get('q')
#     results = []

#     if query:
#         results = CustomUser.objects.filter(
#             Q(username__icontains=query)
#         ).exclude(id=request.user.id)

#     return render(request, 'search_results.html', {'results': results, 'query': query})






# -------------SPECIAL OFFER-------------
@never_cache
@login_required
def create_offer(request):
    if request.user.user_type != 'restaurant':
        return HttpResponseForbidden("Only restaurant users can create offers.")

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        image = request.FILES.get('image')

        SpecialOffer.objects.create(
            restaurant=request.user,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            image=image
        )
        return redirect('feed')  

    return render(request, 'add_offer.html')





# ---------- SEARCH FUNCTION-------------
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Recipe  # adjust if your model is named differently

User = get_user_model()

def ajax_search(request):
    query = request.GET.get('query', '').strip()
    user_list = []
    tag_list = []

    # Search users regardless of # or not
    if not query.startswith('#'):
        users = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query)
        )
        user_list = [{
            'id': user.id,
            'username': user.username,
        } for user in users]

    # Search tags only when query starts with #
    if query.startswith('#'):
        tag_query = query[1:]  # remove the #
        tag_list = list(
            Tag.objects.filter(name__icontains=tag_query)
            .values_list('name', flat=True)
            .distinct()
        )

    return JsonResponse({'users': user_list, 'tags': tag_list})




def tagged_recipes(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    recipes = Recipe.objects.filter(tags=tag).order_by('-created_at')

    context = {
        'tag': tag,
        'recipes': recipes,
    }
    return render(request, 'tagged_recipes.html', context) 





# ---------promotion detail---------
from django.shortcuts import get_object_or_404

@never_cache
@login_required
def promotion_detail(request, promo_id):
    promotion = get_object_or_404(SpecialOffer, id=promo_id, is_active=True)
    return render(request, 'promotion_detail.html', {'promotion': promotion})
