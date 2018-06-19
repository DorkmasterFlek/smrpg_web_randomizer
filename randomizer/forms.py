from django import forms

from .models import REGIONS, MODES


class GenerateForm(forms.Form):
    region = forms.ChoiceField(required=True, choices=REGIONS)
    seed = forms.Field(required=False)
    mode = forms.ChoiceField(required=True, choices=MODES)
    debug_mode = forms.BooleanField(required=False, initial=False)
    randomize_character_stats = forms.BooleanField(required=False, initial=False)
    randomize_drops = forms.BooleanField(required=False, initial=False)
    randomize_enemy_formations = forms.BooleanField(required=False, initial=False)
    randomize_monsters = forms.BooleanField(required=False, initial=False)
    randomize_shops = forms.BooleanField(required=False, initial=False)
    randomize_equipment = forms.BooleanField(required=False, initial=False)
    randomize_spell_stats = forms.BooleanField(required=False, initial=False)
    randomize_spell_lists = forms.BooleanField(required=False, initial=False)
    randomize_join_order = forms.BooleanField(required=False, initial=False)
