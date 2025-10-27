from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import (
    CreateView, UpdateView, DeleteView, DetailView, ListView
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from .models import AdoptionListing, Pet


# ------------------------------------------------------
# 1️⃣ CREATE ADOPTION POST
# ------------------------------------------------------
class CreateAdoptionPostView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = AdoptionListing
    fields = ['requirements', 'additional_info']
    template_name = 'adoption/adoption_form.html'

    def form_valid(self, form):
        pet = get_object_or_404(Pet, id=self.kwargs['pet_id'])
        form.instance.pet = pet
        form.instance.posted_by = self.request.user
        return super().form_valid(form)

    def test_func(self):
        """Ensure only the pet owner can list their pet for adoption"""
        pet = get_object_or_404(Pet, id=self.kwargs['pet_id'])
        return self.request.user == pet.owner

    def get_success_url(self):
        return reverse_lazy('view_adoption_listings')


# ------------------------------------------------------
# 2️⃣ UPDATE ADOPTION POST
# ------------------------------------------------------
class UpdateAdoptionPostView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AdoptionListing
    fields = ['requirements', 'additional_info']
    template_name = 'adoption/adoption_form.html'
    success_url = reverse_lazy('view_adoption_listings')

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.posted_by


# ------------------------------------------------------
# 3️⃣ DELETE ADOPTION POST
# ------------------------------------------------------
class DeleteAdoptionPostView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AdoptionListing
    template_name = 'adoption/adoption_confirm_delete.html'
    success_url = reverse_lazy('view_adoption_listings')

    def test_func(self):
        listing = self.get_object()
        return self.request.user == listing.posted_by


# ------------------------------------------------------
# 4️⃣ VIEW A SINGLE ADOPTION POST
# ------------------------------------------------------
class AdoptionPostDetailView(DetailView):
    model = AdoptionListing
    template_name = 'adoption/adoption_detail.html'
    context_object_name = 'listing'


# ------------------------------------------------------
# 5️⃣ VIEW ALL ADOPTION POSTS OF CURRENT USER
# ------------------------------------------------------
class UserAdoptionPostListView(LoginRequiredMixin, ListView):
    model = AdoptionListing
    template_name = 'adoption/user_adoption_posts.html'
    context_object_name = 'listings'

    def get_queryset(self):
        return AdoptionListing.objects.filter(posted_by=self.request.user)


# Create your views here.
