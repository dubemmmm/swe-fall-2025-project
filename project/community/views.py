from django.shortcuts import render
from django.views.generic import CreateView, DetailView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Q
from .models import CommunityAlert
from decimal import Decimal
import math


class CommunityAlertCreateView(LoginRequiredMixin, CreateView):
    """Create a new community alert"""
    model = CommunityAlert
    fields = ['alert_type', 'title', 'description', 'pet_type', 'size',
              'color_markings', 'location', 'latitude', 'longitude',
              'contact_info', 'photo']
    template_name = 'community/alert_form.html'
    success_url = reverse_lazy('alert-list')

    def form_valid(self, form):
        # Validate required fields
        if not form.cleaned_data.get('contact_info') or not form.cleaned_data.get('contact_info').strip():
            messages.error(self.request, 'Contact information is required.')
            return self.form_invalid(form)

        if not form.cleaned_data.get('location') or not form.cleaned_data.get('location').strip():
            messages.error(self.request, 'Location is required.')
            return self.form_invalid(form)

        form.instance.user = self.request.user
        messages.success(self.request, 'Alert posted successfully!')
        return super().form_valid(form)


class CommunityAlertDetailView(DetailView):
    """View a single community alert"""
    model = CommunityAlert
    template_name = 'community/alert_detail.html'
    context_object_name = 'alert'


class CommunityAlertUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update a community alert (mark as resolved, edit details)"""
    model = CommunityAlert
    fields = ['title', 'description', 'pet_type', 'size', 'color_markings',
              'location', 'latitude', 'longitude', 'contact_info', 'photo', 'is_active']
    template_name = 'community/alert_form.html'

    def test_func(self):
        alert = self.get_object()
        return self.request.user == alert.user

    def form_valid(self, form):
        messages.success(self.request, 'Alert updated successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('alert-detail', kwargs={'pk': self.object.pk})


class CommunityAlertListView(ListView):
    """List and filter community alerts"""
    model = CommunityAlert
    template_name = 'community/alert_list.html'
    context_object_name = 'alerts'
    paginate_by = 10

    def get_queryset(self):
        queryset = CommunityAlert.objects.all()

        # Filter by alert type
        alert_type = self.request.GET.get('type')
        if alert_type in ['LOST', 'FOUND', 'EMERGENCY']:
            queryset = queryset.filter(alert_type=alert_type)

        # Filter by active status (default: active only)
        status = self.request.GET.get('status')
        if status != 'all':
            queryset = queryset.filter(is_active=True)

        # Filter by location radius
        radius = self.request.GET.get('radius')
        if radius and self.request.user.is_authenticated:
            if self.request.user.latitude and self.request.user.longitude:
                try:
                    radius_km = float(radius)
                    user_lat = float(self.request.user.latitude)
                    user_lon = float(self.request.user.longitude)

                    # Filter alerts within radius
                    nearby_alerts = []
                    for alert in queryset:
                        if alert.latitude and alert.longitude:
                            distance = self._calculate_distance(
                                user_lat, user_lon,
                                float(alert.latitude), float(alert.longitude)
                            )
                            if distance <= radius_km:
                                nearby_alerts.append(alert.pk)

                    queryset = queryset.filter(pk__in=nearby_alerts)
                except (ValueError, TypeError):
                    pass

        return queryset.order_by('-created_at')

    def _calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two points in kilometers using Haversine formula"""
        R = 6371  # Earth's radius in kilometers

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

        return R * c
