from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import PetProfile
from .forms import PetProfileForm


class PetProfileListView(LoginRequiredMixin, ListView):
    """
    Displays a list of pet profiles belonging to the currently logged-in user.
    This view is primarily used as a redirect target after pet deletion.
    """
    model = PetProfile
    template_name = 'pets/petprofile_list.html'

    def get_queryset(self):
        return PetProfile.objects.filter(owner=self.request.user)


class PetProfileCreateView(LoginRequiredMixin, CreateView):
    """
    Allows a logged-in user to create a new pet profile.
    The owner field is automatically set to the current user.
    """
    model = PetProfile
    form_class = PetProfileForm
    template_name = 'pets/petprofile_form.html'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('pets:pet_detail', kwargs={'pk': self.object.pk})


class PetProfileDetailView(LoginRequiredMixin, DetailView):
    """
    Displays the details of a specific pet profile.
    """
    model = PetProfile
    template_name = 'pets/petprofile_detail.html'
    context_object_name = 'pet'


class PetProfileUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """
    Allows the owner of a pet profile to update its details.
    """
    model = PetProfile
    form_class = PetProfileForm
    template_name = 'pets/petprofile_edit.html'
    context_object_name = 'pet'

    def test_func(self):
        pet = self.get_object()
        return self.request.user == pet.owner

    def get_success_url(self):
        return reverse_lazy('pets:pet_detail', kwargs={'pk': self.object.pk})


class PetProfileDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Allows the owner of a pet profile to delete it.
    """
    model = PetProfile
    template_name = 'pets/petprofile_confirm_delete.html'
    context_object_name = 'pet'
    success_url = reverse_lazy('pets:pet_list') # Redirect to the user's pet list after deletion

    def test_func(self):
        pet = self.get_object()
        return self.request.user == pet.owner
