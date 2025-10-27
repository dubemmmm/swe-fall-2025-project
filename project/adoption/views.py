from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from .models import AdoptionPost


# Create an adoption post
class AdoptionCreateView(LoginRequiredMixin, CreateView):
    model = AdoptionPost
    fields = ['pet', 'requirements', 'additional_info']
    template_name = 'adoption/adoption_form.html'
    success_url = reverse_lazy('adoption:user_adoptions')

    def form_valid(self, form):
        # Only allow the pet owner to list for adoption
        if form.instance.pet.owner != self.request.user:
            raise PermissionDenied("You can only list your own pets for adoption.")
        form.instance.owner = self.request.user
        return super().form_valid(form)


# Update an adoption post
class AdoptionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = AdoptionPost
    fields = ['requirements', 'additional_info']
    template_name = 'adoption/adoption_form.html'
    success_url = reverse_lazy('adoption:user_adoptions')

    def test_func(self):
        return self.get_object().owner == self.request.user


# Delete an adoption post
class AdoptionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = AdoptionPost
    template_name = 'adoption/adoption_confirm_delete.html'
    success_url = reverse_lazy('adoption:user_adoptions')

    def test_func(self):
        return self.get_object().owner == self.request.user


# View a single adoption post
class AdoptionDetailView(DetailView):
    model = AdoptionPost
    template_name = 'adoption/adoption_detail.html'


# View all adoption posts of the logged-in user
class UserAdoptionListView(LoginRequiredMixin, ListView):
    model = AdoptionPost
    template_name = 'adoption/user_adoptions.html'

    def get_queryset(self):
        return AdoptionPost.objects.filter(owner=self.request.user)


# Create your views here.
