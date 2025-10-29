from django.urls import path
from . import views

urlpatterns = [
    path('alerts/', views.CommunityAlertListView.as_view(), name='alert-list'),
    path('alerts/create/', views.CommunityAlertCreateView.as_view(), name='post_alert'),
    path('alerts/<int:pk>/', views.CommunityAlertDetailView.as_view(), name='alert-detail'),
    path('alerts/<int:pk>/update/', views.CommunityAlertUpdateView.as_view(), name='alert-update'),
]
