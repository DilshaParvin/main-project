from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('user', 'User'),
        ('restaurant', 'Restaurant'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    restaurant_name = models.CharField(max_length=255, blank=True, null=True)
    restaurant_location = models.CharField(max_length=255, blank=True, null=True)
    is_approved = models.BooleanField(default=False)  # Admin approval for restaurants
    contact_number = models.CharField(max_length=20, blank=True, null=True)
    opening_hours = models.CharField(max_length=100, blank=True, null=True)
    
    followers = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='following',
        blank=True
    )

    def is_restaurant(self):
        return self.user_type == 'restaurant'

    def get_display_name(self):
        # Return the display name based on user type.
        if self.user_type == 'restaurant' and self.restaurant_name:
            return self.restaurant_name
        return self.get_full_name() or self.username

    def __str__(self):
        return self.get_display_name()
    
    def follower_count(self):
        return self.followers.count()

    def following_count(self):
        return self.following.count()



User = get_user_model()





class Recipe(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField(help_text="Enter each ingredient on a new line")
    instructions = models.TextField(help_text="Enter each step on a new line")
    cook_time = models.PositiveIntegerField(help_text="Cooking time in minutes")
    servings = models.PositiveIntegerField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    likes = models.ManyToManyField(User, through='Like', related_name='liked_recipes')
    tags = models.ManyToManyField('Tag', related_name='recipes', blank=True)

    is_promoted = models.BooleanField(default=False, help_text="Mark this recipe as promoted")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('recipe_detail', kwargs={'pk': self.pk})

    def get_total_time(self):
        return self.cook_time

    def get_likes_count(self):
        return self.likes.count()

    def get_ingredients_list(self):
        return [ingredient.strip() for ingredient in self.ingredients.split('\n') if ingredient.strip()]

    def get_instructions_list(self):
        return [instruction.strip() for instruction in self.instructions.split('\n') if instruction.strip()]


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')

    def __str__(self):
        return f'{self.user.username} likes {self.recipe.title}'


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author.username} on {self.recipe.title}'


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('recipes:tag', kwargs={'tag_name': self.name})







class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('like', 'Like'),
        ('follow', 'Follow'),
        ('message', 'Message'),
    )

    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    from_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES)
    message = models.TextField(blank=True)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.notification_type} to {self.to_user.username}"











class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='received_messages', on_delete=models.CASCADE)
    message = models.TextField(blank=True)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        if self.recipe:
            return f"From {self.sender} to {self.recipient} - Recipe: {self.recipe.title}"
        return f"From {self.sender} to {self.recipient} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"







class SpecialOffer(models.Model):
    restaurant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'restaurant'}
    )
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='offers/', blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.restaurant.username}"
