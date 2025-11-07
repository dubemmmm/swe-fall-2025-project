from django.urls import path
from .views import (
    AdoptionCreateView,
    AdoptionUpdateView,
    AdoptionDeleteView,
    AdoptionDetailView,
    UserAdoptionListView,
    AllAdoptionListView,
    AdoptionRequestCreateView,
    MyAdoptionRequestsListView,
    AdoptionRequestDetailView,
    ApproveAdoptionRequestView,
    RejectAdoptionRequestView
)

app_name = 'adoption'  # ✅ important for reverse('adoption:<name>')

urlpatterns = [
    path('', AllAdoptionListView.as_view(), name='list'),
    path('create/', AdoptionCreateView.as_view(), name='create'),
    path('<int:pk>/update/', AdoptionUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', AdoptionDeleteView.as_view(), name='delete'),
    path('<int:pk>/', AdoptionDetailView.as_view(), name='detail'),
    path('<int:pk>/request/', AdoptionRequestCreateView.as_view(), name='request_adoption'),
    path('my-adoptions/', UserAdoptionListView.as_view(), name='user_adoptions'),
    path('my-requests/', MyAdoptionRequestsListView.as_view(), name='my_requests'),
    path('request/<int:pk>/', AdoptionRequestDetailView.as_view(), name='request_detail'),
    path('request/<int:pk>/approve/', ApproveAdoptionRequestView.as_view(), name='approve_request'),
    path('request/<int:pk>/reject/', RejectAdoptionRequestView.as_view(), name='reject_request'),
]
