from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.contrib import messages
from .models import Notification


@login_required
def mark_notification_read(request, pk):
    """Mark a single notification as read and redirect to its link"""
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.mark_as_read()

    if notification.link:
        return redirect(notification.link)
    return redirect('notifications:list')


@login_required
def mark_all_read(request):
    """Mark all notifications as read for the current user"""
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect('notifications:list')


@login_required
def get_unread_count(request):
    """API endpoint to get unread notification count"""
    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({'count': count})


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 20

    def get_queryset(self):
        try:
            return Notification.objects.filter(
                recipient=self.request.user
            ).order_by('-created_at')
        except Exception as e:
            messages.error(self.request, 'Unable to load notifications. Please try again.')
            return Notification.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['unread_count'] = Notification.objects.filter(
                recipient=self.request.user,
                is_read=False
            ).count()
        except Exception:
            context['unread_count'] = 0
            messages.warning(self.request, 'Some notification data could not be loaded.')
        return context
