from django import forms

from .models import REGIONS, MODES
from .logic.main import FLAGS


class GenerateForm(forms.Form):
    region = forms.ChoiceField(required=True, choices=REGIONS)
    seed = forms.Field(required=False)
    mode = forms.ChoiceField(required=True, choices=MODES)
    debug_mode = forms.IntegerField(required=False, initial=0)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for flag in FLAGS:
            self.fields[flag.field] = forms.IntegerField(required=False, initial=0)
