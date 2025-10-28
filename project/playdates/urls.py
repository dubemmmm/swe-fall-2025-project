from django.urls import path
from playdates import views

urlpatterns = [
    # Create playdate
    path('create/', views.PlaydateCreateView.as_view(), name='playdate-create'),

    # Browse public playdates
    path('browse/', views.BrowsePlaydatesView.as_view(), name='browse-playdates'),

    # Request to join playdate
    path('<int:pk>/request-join/', views.RequestToJoinView.as_view(), name='request-join'),

    # Approve/deny join request
    path('<int:pk>/approve/<int:participant_id>/', views.ApproveRequestView.as_view(), name='approve-request'),

    # List all playdates
    path('', views.PlaydateListView.as_view(), name='playdate-list'),

    # My playdates (user's own playdates)
    path('my-playdates/', views.MyPlaydatesView.as_view(), name='my-playdates'),

    # Playdate detail
    path('<int:pk>/', views.PlaydateDetailView.as_view(), name='playdate-detail'),

    # Invite pet to playdate
    path('<int:pk>/invite/', views.PlaydateInviteView.as_view(), name='playdate-invite'),

    # Respond to playdate invitation
    path('<int:pk>/respond/', views.PlaydateRespondView.as_view(), name='playdate-respond'),

    # Update playdate
    path('<int:pk>/update/', views.PlaydateUpdateView.as_view(), name='playdate-update'),

    # Delete playdate
    path('<int:pk>/delete/', views.PlaydateDeleteView.as_view(), name='playdate-delete'),
]
