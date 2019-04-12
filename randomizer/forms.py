from django import forms

from .logic.flags import CATEGORIES

MODES = (
    ('open', 'Open'),
    ('linear', 'Linear'),
)

REGIONS = (
    ('US', 'US'),
    # ('JP', 'Japan'),
    ('EU', 'PAL'),
)


class GenerateForm(forms.Form):
    region = forms.ChoiceField(required=True, choices=REGIONS)
    seed = forms.Field(required=False)
    mode = forms.ChoiceField(required=True, choices=MODES)
    flags = forms.Field(required=False, initial='')
    debug_mode = forms.BooleanField(required=False, initial=False)
