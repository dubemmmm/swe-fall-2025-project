from django.urls import path
from .views import NotificationListView, mark_notification_read, mark_all_read, get_unread_count

app_name = 'notifications'

urlpatterns = [
    path('', NotificationListView.as_view(), name='list'),
    path('<int:pk>/read/', mark_notification_read, name='mark_read'),
    path('mark-all-read/', mark_all_read, name='mark_all_read'),
    path('api/unread-count/', get_unread_count, name='unread_count'),
]
