# Register your models here.

from django.contrib import admin
from django.utils.html import format_html
from .models import Seed, Patch


@admin.register(Seed)
class SeedAdmin(admin.ModelAdmin):
    readonly_fields = ('permalink',)

    # Custom field for permalink to seed.
    @admin.display(description="Permalink")
    def permalink(self, obj: Seed) -> str:
        return format_html('<a href="{}" target="_blank">Permalink</a>', obj.permalink)


@admin.register(Patch)
class PatchAdmin(admin.ModelAdmin):
    readonly_fields = ('permalink',)

    # Custom field for permalink to patch.
    @admin.display(description="Permalink")
    def permalink(self, obj: Patch) -> str:
        return format_html('<a href="{}" target="_blank">Permalink</a>', obj.permalink)
