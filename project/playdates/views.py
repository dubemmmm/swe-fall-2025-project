from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils import timezone
from django import forms

from playdates.models import Playdate, PlaydateParticipant
from pets.models import PetProfile


class PlaydateForm(forms.ModelForm):
    """Custom form for creating playdates with proper widgets"""

    scheduled_time = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'input-field'
            },
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']
    )

    class Meta:
        model = Playdate
        fields = ['organizer_pet', 'scheduled_time', 'location', 'description', 'max_participants', 'is_public']
        widgets = {
            'organizer_pet': forms.Select(attrs={'class': 'input-field'}),
            'location': forms.TextInput(attrs={'class': 'input-field'}),
            'description': forms.Textarea(attrs={'class': 'input-field', 'rows': 4}),
            'max_participants': forms.NumberInput(attrs={'class': 'input-field', 'min': 2, 'value': 5}),
            'is_public': forms.CheckboxInput(attrs={'class': 'checkbox-input'}),
        }


class PlaydateCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new playdate.
    Can be either:
    1. Public/Open - appears in browse for anyone to request
    2. Private with invite - invite specific pet(s)
    """
    model = Playdate
    form_class = PlaydateForm
    template_name = 'playdates/create_playdates.html'
    success_url = reverse_lazy('playdates:playdate-list')

    def get_form(self, form_class=None):
        """Customize the form to only show the current user's pets"""
        form = super().get_form(form_class)
        form.fields['organizer_pet'].queryset = PetProfile.objects.filter(
            owner=self.request.user,
            is_playdate_available=True
        )
        form.fields['organizer_pet'].label = 'Your Pet'
        form.fields['is_public'].label = 'Make this playdate public (others can request to join)'
        return form

    def get_context_data(self, **kwargs):
        """Add available pets that can be invited and user's pets for display"""
        context = super().get_context_data(**kwargs)

        # Add user's pets for visual display in the template
        context['user_pets'] = PetProfile.objects.filter(
            owner=self.request.user,
            is_playdate_available=True
        )

        # Add available pets that can be invited
        context['available_pets'] = PetProfile.objects.filter(
            is_playdate_available=True
        ).exclude(
            owner=self.request.user
        ).select_related('owner')

        return context

    def form_valid(self, form):
        """Set the organizer and handle invitations"""
        if form.cleaned_data['scheduled_time'] <= timezone.now():
            messages.error(self.request, 'Scheduled time must be in the future.')
            return self.form_invalid(form)

        if form.cleaned_data['organizer_pet'].owner != self.request.user:
            messages.error(self.request, 'You can only create playdates for your own pets.')
            return self.form_invalid(form)

        if not form.cleaned_data['organizer_pet'].is_playdate_available:
            messages.error(self.request, 'This pet is not available for playdates.')
            return self.form_invalid(form)

        form.instance.organizer = self.request.user
        form.instance.status = 'OPEN'

        response = super().form_valid(form)

        # Handle initial invitations if provided
        invited_pet_ids = self.request.POST.getlist('invited_pets')
        if invited_pet_ids:
            for pet_id in invited_pet_ids:
                try:
                    invited_pet = PetProfile.objects.get(id=pet_id, is_playdate_available=True)
                    PlaydateParticipant.objects.create(
                        playdate=self.object,
                        user=invited_pet.owner,
                        pet=invited_pet,
                        status='INVITED'
                    )
                except PetProfile.DoesNotExist:
                    pass

        if invited_pet_ids:
            messages.success(self.request, f'Playdate created and {len(invited_pet_ids)} invitation(s) sent!')
        else:
            if form.cleaned_data['is_public']:
                messages.success(self.request, 'Public playdate created! Other users can now request to join.')
            else:
                messages.success(self.request, 'Playdate created! You can invite pets from the playdate detail page.')

        return response


class BrowsePlaydatesView(LoginRequiredMixin, ListView):
    """View for browsing all public/open playdates"""
    model = Playdate
    template_name = 'playdates/browse_playdates.html'
    context_object_name = 'playdates'
    paginate_by = 12

    def get_queryset(self):
        """Get public playdates that are open and in the future"""
        queryset = Playdate.objects.filter(
            is_public=True,
            status='OPEN',
            scheduled_time__gte=timezone.now()
        ).exclude(
            organizer=self.request.user  # Don't show user's own playdates
        ).select_related(
            'organizer_pet', 'organizer', 'organizer_pet__owner'
        ).prefetch_related('participants')

        # Filter by location if provided
        location = self.request.GET.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location)

        # Filter by pet species if provided
        species = self.request.GET.get('species')
        if species:
            queryset = queryset.filter(organizer_pet__species=species)

        return queryset.order_by('scheduled_time')

    def get_context_data(self, **kwargs):
        """Add user's pets and filter options"""
        context = super().get_context_data(**kwargs)
        context['my_pets'] = PetProfile.objects.filter(
            owner=self.request.user,
            is_playdate_available=True
        )
        context['species_choices'] = PetProfile.SPECIES_CHOICES
        return context


class RequestToJoinView(LoginRequiredMixin, View):
    """View for requesting to join a playdate"""

    def post(self, request, pk):
        """Handle join request"""
        playdate = get_object_or_404(Playdate, pk=pk, is_public=True)
        pet_id = request.POST.get('pet_id')

        if not pet_id:
            messages.error(request, 'Please select a pet.')
            return redirect('browse-playdates')

        try:
            pet = PetProfile.objects.get(id=pet_id, owner=request.user, is_playdate_available=True)
        except PetProfile.DoesNotExist:
            messages.error(request, 'Invalid pet selection.')
            return redirect('browse-playdates')

        # Check if playdate is full
        if playdate.is_full():
            messages.warning(request, 'This playdate is already full.')
            return redirect('playdate-detail', pk=pk)

        # Check if already participating or requested
        existing = PlaydateParticipant.objects.filter(playdate=playdate, pet=pet).first()
        if existing:
            if existing.status == 'REQUESTED':
                messages.info(request, 'You have already requested to join this playdate.')
            elif existing.status == 'ACCEPTED':
                messages.info(request, 'You are already participating in this playdate.')
            elif existing.status == 'INVITED':
                messages.info(request, 'You have been invited to this playdate. Please respond to the invitation.')
            return redirect('playdate-detail', pk=pk)

        # Create request
        PlaydateParticipant.objects.create(
            playdate=playdate,
            user=request.user,
            pet=pet,
            status='REQUESTED'
        )

        messages.success(request, f'Request sent! The organizer will review your request for {pet.name}.')
        return redirect('playdates:playdate-detail', pk=pk)


class ApproveRequestView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View for approving or denying join requests"""

    def test_func(self):
        """Only the organizer can approve requests"""
        playdate = get_object_or_404(Playdate, pk=self.kwargs['pk'])
        return self.request.user == playdate.organizer

    def post(self, request, pk, participant_id):
        """Approve or deny a request"""
        playdate = get_object_or_404(Playdate, pk=pk)
        participant = get_object_or_404(
            PlaydateParticipant,
            id=participant_id,
            playdate=playdate,
            status='REQUESTED'
        )

        action = request.POST.get('action')  # 'approve' or 'deny'

        if action == 'approve':
            if playdate.is_full():
                messages.warning(request, 'Cannot approve - playdate is full.')
                return redirect('playdate-detail', pk=pk)

            participant.status = 'ACCEPTED'
            participant.responded_at = timezone.now()
            participant.save()

            # Update playdate status if first acceptance
            if playdate.status == 'OPEN' and playdate.get_accepted_count() > 0:
                playdate.status = 'CONFIRMED'
                playdate.save()

            messages.success(request, f'Approved {participant.pet.name} to join the playdate!')

        elif action == 'deny':
            participant.status = 'DECLINED'
            participant.responded_at = timezone.now()
            participant.save()
            messages.info(request, f'Declined request from {participant.pet.name}.')

        return redirect('playdates:playdate-detail', pk=pk)


class PlaydateInviteView(LoginRequiredMixin, UserPassesTestMixin, View):
    """View for inviting additional pets to an existing playdate"""

    def test_func(self):
        """Only the organizer can invite pets"""
        playdate = get_object_or_404(Playdate, pk=self.kwargs['pk'])
        return self.request.user == playdate.organizer

    def post(self, request, pk):
        """Handle invitation"""
        playdate = get_object_or_404(Playdate, pk=pk)
        invited_pet_id = request.POST.get('pet_id')

        if not invited_pet_id:
            messages.error(request, 'Please select a pet to invite.')
            return redirect('playdate-detail', pk=pk)

        if playdate.is_full():
            messages.warning(request, 'Playdate is full. Cannot send more invitations.')
            return redirect('playdate-detail', pk=pk)

        try:
            invited_pet = PetProfile.objects.get(id=invited_pet_id, is_playdate_available=True)

            if PlaydateParticipant.objects.filter(playdate=playdate, pet=invited_pet).exists():
                messages.warning(request, f'{invited_pet.name} is already involved with this playdate.')
                return redirect('playdate-detail', pk=pk)

            PlaydateParticipant.objects.create(
                playdate=playdate,
                user=invited_pet.owner,
                pet=invited_pet,
                status='INVITED'
            )
            messages.success(request, f'Invitation sent to {invited_pet.name}\'s owner!')

        except PetProfile.DoesNotExist:
            messages.error(request, 'Pet not found or not available for playdates.')

        return redirect('playdates:playdate-detail', pk=pk)


class PlaydateRespondView(LoginRequiredMixin, View):
    """View for responding to a playdate invitation (accept or decline)"""

    def post(self, request, pk):
        """Handle accept/decline response"""
        playdate = get_object_or_404(Playdate, pk=pk)
        response = request.POST.get('response')  # 'accept' or 'decline'

        try:
            participant = PlaydateParticipant.objects.get(
                playdate=playdate,
                user=request.user,
                status='INVITED'
            )
        except PlaydateParticipant.DoesNotExist:
            messages.error(request, 'You do not have a pending invitation for this playdate.')
            return redirect('playdate-list')

        if response == 'accept':
            if playdate.is_full():
                messages.warning(request, 'Sorry, this playdate is now full.')
                return redirect('playdate-detail', pk=pk)

            participant.status = 'ACCEPTED'
            participant.responded_at = timezone.now()
            participant.save()

            # Update playdate status
            if playdate.status == 'OPEN':
                playdate.status = 'CONFIRMED'
                playdate.save()

            messages.success(request, f'You accepted the playdate invitation for {participant.pet.name}!')

        elif response == 'decline':
            participant.status = 'DECLINED'
            participant.responded_at = timezone.now()
            participant.save()
            messages.info(request, 'You declined the playdate invitation.')

        return redirect('playdates:playdate-detail', pk=pk)


class PlaydateListView(LoginRequiredMixin, ListView):
    """View for listing all playdates"""
    model = Playdate
    template_name = 'playdates/playdate_list.html'
    context_object_name = 'playdates'
    paginate_by = 10

    def get_queryset(self):
        """Filter playdates based on query parameters"""
        queryset = Playdate.objects.select_related(
            'organizer_pet', 'organizer', 'organizer_pet__owner'
        ).prefetch_related('participants__pet').order_by('-scheduled_time')

        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)

        pet_id = self.request.GET.get('pet')
        if pet_id:
            queryset = queryset.filter(organizer_pet_id=pet_id)

        organizer_id = self.request.GET.get('organizer')
        if organizer_id:
            queryset = queryset.filter(organizer_id=organizer_id)

        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            queryset = queryset.filter(scheduled_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(scheduled_time__lte=end_date)

        return queryset

    def get_context_data(self, **kwargs):
        """Add additional context data"""
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.request.GET.get('status', '')
        context['current_pet'] = self.request.GET.get('pet', '')
        return context


class PlaydateDetailView(LoginRequiredMixin, DetailView):
    """View for viewing playdate details"""
    model = Playdate
    template_name = 'playdates/playdate_detail.html'
    context_object_name = 'playdate'

    def get_queryset(self):
        """Optimize query with related objects"""
        return Playdate.objects.select_related(
            'organizer_pet', 'organizer', 'organizer_pet__owner'
        ).prefetch_related('participants__pet', 'participants__user')

    def get_context_data(self, **kwargs):
        """Add participant information and available actions"""
        context = super().get_context_data(**kwargs)
        playdate = self.object

        # Categorize participants
        context['invited_participants'] = playdate.participants.filter(status='INVITED')
        context['requested_participants'] = playdate.participants.filter(status='REQUESTED')
        context['accepted_participants'] = playdate.participants.filter(status='ACCEPTED')

        # Check if current user has invitation
        context['user_invitation'] = playdate.participants.filter(
            user=self.request.user,
            status='INVITED'
        ).first()

        # Check if current user has requested
        context['user_request'] = playdate.participants.filter(
            user=self.request.user,
            status__in=['REQUESTED', 'ACCEPTED']
        ).first()

        # Check if user can request to join
        context['can_request_join'] = (
            playdate.is_public and
            playdate.status == 'OPEN' and
            not playdate.is_full() and
            playdate.organizer != self.request.user and
            not context['user_invitation'] and
            not context['user_request']
        )

        # Available pets for user to join with
        if context['can_request_join']:
            already_joined_pet_ids = playdate.participants.filter(
                user=self.request.user
            ).values_list('pet_id', flat=True)

            context['my_available_pets'] = PetProfile.objects.filter(
                owner=self.request.user,
                is_playdate_available=True
            ).exclude(id__in=already_joined_pet_ids)

        # If user is organizer, show pets available to invite
        if self.request.user == playdate.organizer and not playdate.is_full():
            invited_pet_ids = playdate.participants.values_list('pet_id', flat=True)
            context['available_pets'] = PetProfile.objects.filter(
                is_playdate_available=True
            ).exclude(
                owner=self.request.user
            ).exclude(
                id__in=invited_pet_ids
            ).select_related('owner')

        return context


class PlaydateUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """View for updating a playdate"""
    model = Playdate
    fields = ['scheduled_time', 'location', 'description', 'max_participants', 'is_public', 'status']
    template_name = 'playdates/playdate_form.html'
    success_url = reverse_lazy('playdates:playdate-list')

    def test_func(self):
        """Only allow the organizer to update the playdate"""
        playdate = self.get_object()
        return self.request.user == playdate.organizer

    def form_valid(self, form):
        """Validate before updating"""
        if form.cleaned_data['scheduled_time'] <= timezone.now():
            messages.error(self.request, 'Scheduled time must be in the future.')
            return self.form_invalid(form)

        messages.success(self.request, 'Playdate updated successfully!')
        return super().form_valid(form)

    def handle_no_permission(self):
        """Handle case where user doesn't have permission"""
        messages.error(self.request, 'You can only update your own playdates.')
        return redirect('playdates:playdate-list')


class PlaydateDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View for deleting a playdate"""
    model = Playdate
    template_name = 'playdates/playdate_confirm_delete.html'
    success_url = reverse_lazy('playdates:playdate-list')

    def test_func(self):
        """Only allow the organizer to delete the playdate"""
        playdate = self.get_object()
        return self.request.user == playdate.organizer

    def delete(self, request, *args, **kwargs):
        """Add success message on delete"""
        messages.success(request, 'Playdate cancelled successfully!')
        return super().delete(request, *args, **kwargs)

    def handle_no_permission(self):
        """Handle case where user doesn't have permission"""
        messages.error(self.request, 'You can only delete your own playdates.')
        return redirect('playdates:playdate-list')


class MyPlaydatesView(LoginRequiredMixin, ListView):
    """View for listing the current user's playdates (organized and invited to)"""
    model = Playdate
    template_name = 'playdates/my_playdates.html'
    context_object_name = 'playdates'
    paginate_by = 10

    def get_queryset(self):
        """Get playdates organized by the current user"""
        return Playdate.objects.filter(
            organizer=self.request.user
        ).select_related(
            'organizer_pet', 'organizer_pet__owner'
        ).prefetch_related('participants__pet').order_by('-scheduled_time')

    def get_context_data(self, **kwargs):
        """Add additional context for organized and invited playdates"""
        context = super().get_context_data(**kwargs)
        now = timezone.now()

        # Playdates organized by user
        context['organized_upcoming'] = Playdate.objects.filter(
            organizer=self.request.user,
            scheduled_time__gte=now
        ).select_related('organizer_pet', 'organizer_pet__owner').prefetch_related(
            'participants__pet'
        ).order_by('scheduled_time')

        context['organized_past'] = Playdate.objects.filter(
            organizer=self.request.user,
            scheduled_time__lt=now
        ).select_related('organizer_pet', 'organizer_pet__owner').prefetch_related(
            'participants__pet'
        ).order_by('-scheduled_time')

        # Playdates user is involved in (invited or requested)
        my_participations = PlaydateParticipant.objects.filter(
            user=self.request.user
        ).select_related('playdate', 'pet', 'playdate__organizer', 'playdate__organizer_pet')

        context['invited_pending'] = my_participations.filter(
            status='INVITED',
            playdate__scheduled_time__gte=now
        )

        context['requested_pending'] = my_participations.filter(
            status='REQUESTED',
            playdate__scheduled_time__gte=now
        )

        context['accepted_upcoming'] = my_participations.filter(
            status='ACCEPTED',
            playdate__scheduled_time__gte=now
        )

        return context
