from django.urls import path
from . import views

app_name = 'pets'

urlpatterns = [
    path('', views.PetProfileListView.as_view(), name='pet_list'),
    path('create/', views.PetProfileCreateView.as_view(), name='pet_create'),
    path('<int:pk>/', views.PetProfileDetailView.as_view(), name='pet_detail'),
    path('<int:pk>/update/', views.PetProfileUpdateView.as_view(), name='pet_update'),
    path('<int:pk>/delete/', views.PetProfileDeleteView.as_view(), name='pet_delete'),
]