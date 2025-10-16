from django.contrib import admin
from .models import PetProfile, PetPhoto, PetTrait

# Register your models here.

class PetPhotoInline(admin.TabularInline):
    model = PetPhoto
    extra = 1
    fields = ['photo', 'is_primary', 'uploaded_at']
    readonly_fields = ['uploaded_at']

class PetTraitInline(admin.TabularInline):
    model = PetTrait
    extra = 1
    fields = ['trait']

@admin.register(PetProfile)
class PetProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'species', 'breed', 'owner', 'age', 'is_playdate_available', 'is_adoptable', 'created_at']
    list_filter = ['species', 'general_size', 'energy_level', 'is_playdate_available', 'is_adoptable', 'privacy_settings']
    search_fields = ['name', 'breed', 'owner__username', 'owner__profile_name']
    inlines = [PetPhotoInline, PetTraitInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'species', 'breed', 'age')
        }),
        ('Physical Characteristics', {
            'fields': ('general_size', 'weight', 'color_markings')
        }),
        ('Behavior & Availability', {
            'fields': ('energy_level', 'description', 'is_playdate_available', 'is_adoptable')
        }),
        ('Settings', {
            'fields': ('privacy_settings',)
        }),
    )

@admin.register(PetPhoto)
class PetPhotoAdmin(admin.ModelAdmin):
    list_display = ['pet', 'is_primary', 'uploaded_at']
    list_filter = ['is_primary', 'uploaded_at']
    search_fields = ['pet__name']

@admin.register(PetTrait)
class PetTraitAdmin(admin.ModelAdmin):
    list_display = ['pet', 'trait']
    search_fields = ['pet__name', 'trait']
