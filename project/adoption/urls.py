from django.urls import path
from .views import (
    AdoptionCreateView,
    AdoptionUpdateView,
    AdoptionDeleteView,
    AdoptionDetailView,
    UserAdoptionListView
)

app_name = 'adoption'  # ✅ important for reverse('adoption:<name>')

urlpatterns = [
    path('create/', AdoptionCreateView.as_view(), name='create'),
    path('<int:pk>/update/', AdoptionUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', AdoptionDeleteView.as_view(), name='delete'),
    path('<int:pk>/', AdoptionDetailView.as_view(), name='detail'),
    path('my-adoptions/', UserAdoptionListView.as_view(), name='user_adoptions'),
]
