from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.urls import reverse_lazy, reverse
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import AdoptionPost, AdoptionRequest
from .forms import AdoptionRequestForm


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if the current user has already requested this adoption
        if self.request.user.is_authenticated:
            from .models import AdoptionRequest
            user_request = AdoptionRequest.objects.filter(
                adoption_post=self.object,
                requester=self.request.user
            ).first()

            context['user_has_requested'] = user_request is not None
            context['user_request_status'] = user_request.status if user_request else None
            context['user_request'] = user_request
        else:
            context['user_has_requested'] = False
            context['user_request_status'] = None
            context['user_request'] = None
        return context


# View all adoption posts of the logged-in user
class UserAdoptionListView(LoginRequiredMixin, ListView):
    model = AdoptionPost
    template_name = 'adoption/user_adoptions.html'

    def get_queryset(self):
        return AdoptionPost.objects.filter(owner=self.request.user)


# View all active adoption posts (public)
class AllAdoptionListView(ListView):
    model = AdoptionPost
    template_name = 'adoption/adoption_list.html'
    context_object_name = 'adoptions'

    def get_queryset(self):
        return AdoptionPost.objects.filter(is_active=True).select_related('pet', 'owner').order_by('-created_at')


# Submit an adoption request
class AdoptionRequestCreateView(LoginRequiredMixin, CreateView):
    model = AdoptionRequest
    form_class = AdoptionRequestForm
    template_name = 'adoption/adoption_request_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.adoption_post = get_object_or_404(AdoptionPost, pk=self.kwargs['pk'])

        # Prevent owner from requesting their own pet
        if self.adoption_post.owner == request.user:
            messages.error(request, "You cannot request to adopt your own pet.")
            return redirect('adoption:detail', pk=self.adoption_post.pk)

        # Check if user has already requested
        if AdoptionRequest.objects.filter(adoption_post=self.adoption_post, requester=request.user).exists():
            messages.info(request, "You have already submitted a request for this pet.")
            return redirect('adoption:detail', pk=self.adoption_post.pk)

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['adoption_post'] = self.adoption_post
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial['user'] = self.request.user
        return initial

    def form_valid(self, form):
        form.instance.adoption_post = self.adoption_post
        form.instance.requester = self.request.user

        # Create notification for the pet owner
        from notifications.models import Notification
        Notification.objects.create(
            recipient=self.adoption_post.owner,
            notification_type='new_adoption_request',
            title=f'New Adoption Request for {self.adoption_post.pet.name}',
            message=f'{self.request.user.profile_name or self.request.user.username} has submitted an adoption request for your pet {self.adoption_post.pet.name}.',
            link=f'/adoption/my-requests/'
        )

        messages.success(self.request, f"Your adoption request for {self.adoption_post.pet.name} has been submitted!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('adoption:detail', kwargs={'pk': self.adoption_post.pk})


# View all adoption requests for user's pets
class MyAdoptionRequestsListView(LoginRequiredMixin, ListView):
    model = AdoptionRequest
    template_name = 'adoption/my_adoption_requests.html'
    context_object_name = 'requests'

    def get_queryset(self):
        # Get all requests for adoption posts owned by the current user
        return AdoptionRequest.objects.filter(
            adoption_post__owner=self.request.user
        ).select_related('adoption_post', 'adoption_post__pet', 'requester').order_by('-created_at')


# View detailed adoption request
class AdoptionRequestDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = AdoptionRequest
    template_name = 'adoption/adoption_request_detail.html'
    context_object_name = 'request'

    def test_func(self):
        # Only the pet owner can view the request
        request_obj = self.get_object()
        return request_obj.adoption_post.owner == self.request.user


# Approve an adoption request
class ApproveAdoptionRequestView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = AdoptionRequest
    http_method_names = ['post']

    def test_func(self):
        # Only the pet owner can approve the request
        request_obj = self.get_object()
        return request_obj.adoption_post.owner == self.request.user

    def post(self, request, *args, **kwargs):
        adoption_request = self.get_object()
        adoption_request.status = 'approved'
        adoption_request.save()

        # Create notification for the requester
        from notifications.models import Notification
        Notification.objects.create(
            recipient=adoption_request.requester,
            notification_type='adoption_approved',
            title=f'Adoption Request Approved!',
            message=f'Your adoption request for {adoption_request.adoption_post.pet.name} has been approved! Check your email for next steps.',
            link=f'/adoption/{adoption_request.adoption_post.pk}/'
        )

        # Send email notification to the requester
        try:
            pet_name = adoption_request.adoption_post.pet.name
            owner_name = adoption_request.adoption_post.owner.profile_name or adoption_request.adoption_post.owner.username
            owner_email = adoption_request.adoption_post.owner.email

            subject = f"Your adoption request for {pet_name} has been approved!"
            message = f"""
Dear {adoption_request.full_name},

Great news! Your adoption request for {pet_name} has been approved!

The pet owner will contact you shortly at {adoption_request.email} with further information regarding the next steps in the adoption process.

Please keep an eye on your email and phone ({adoption_request.phone_number}) for communication from the owner.

Next Steps:
- The owner will reach out to schedule a meet and greet
- You may be asked to provide additional documentation
- A home visit may be arranged
- Final adoption paperwork will be completed

If you have any questions in the meantime, you can reach out to the owner at: {owner_email}

Thank you for choosing to adopt!

Best regards,
PetNextDoor Team
            """

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@petnextdoor.com',
                [adoption_request.email],
                fail_silently=True,
            )
        except Exception as e:
            # Log the error but don't fail the approval
            print(f"Failed to send email: {e}")

        messages.success(
            request,
            f"You have approved the adoption request from {adoption_request.full_name}! "
            f"They will receive an email notification with further instructions."
        )
        return redirect('adoption:request_detail', pk=adoption_request.pk)


# Reject an adoption request
class RejectAdoptionRequestView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = AdoptionRequest
    http_method_names = ['post']

    def test_func(self):
        # Only the pet owner can reject the request
        request_obj = self.get_object()
        return request_obj.adoption_post.owner == self.request.user

    def post(self, request, *args, **kwargs):
        adoption_request = self.get_object()
        adoption_request.status = 'rejected'
        adoption_request.save()

        # Create notification for the requester
        from notifications.models import Notification
        Notification.objects.create(
            recipient=adoption_request.requester,
            notification_type='adoption_rejected',
            title=f'Adoption Request Status Update',
            message=f'Your adoption request for {adoption_request.adoption_post.pet.name} was not approved at this time. Keep looking for your perfect match!',
            link=f'/adoption/{adoption_request.adoption_post.pk}/'
        )

        messages.info(request, f"You have rejected the adoption request from {adoption_request.full_name}.")
        return redirect('adoption:request_detail', pk=adoption_request.pk)