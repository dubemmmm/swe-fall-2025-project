from django.urls import path
from .views import (
    CreateAdoptionPostView,
    UpdateAdoptionPostView,
    DeleteAdoptionPostView,
    AdoptionPostDetailView,
    UserAdoptionPostListView,
)

urlpatterns = [
    # Create a new adoption listing for a pet
    path('create/<int:pet_id>/', CreateAdoptionPostView.as_view(), name='post_for_adoption'),

    # Update an existing listing
    path('<int:pk>/update/', UpdateAdoptionPostView.as_view(), name='update_adoption_post'),

    # Delete a listing
    path('<int:pk>/delete/', DeleteAdoptionPostView.as_view(), name='delete_adoption_post'),

    # View one adoption post
    path('<int:pk>/', AdoptionPostDetailView.as_view(), name='view_adoption_post'),

    # View all adoption posts of the logged-in user
    path('my-posts/', UserAdoptionPostListView.as_view(), name='user_adoption_posts'),
]
