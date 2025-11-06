from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('alerts/', views.CommunityAlertListView.as_view(), name='alert-list'),
    path('alerts/create/', views.CommunityAlertCreateView.as_view(), name='post_alert'),
    path('alerts/<int:pk>/', views.CommunityAlertDetailView.as_view(), name='alert-detail'),
    path('alerts/<int:pk>/update/', views.CommunityAlertUpdateView.as_view(), name='alert-update'),
    path('alerts/<int:pk>/delete/', views.CommunityAlertDeleteView.as_view(), name='alert-delete'),
    path('feed/', views.CommunityFeedView.as_view(), name='community_feed'),
]
