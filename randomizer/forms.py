from django import forms

from .logic.flags import FLAGS

MODES = (
    ('open', 'Open'),
    ('classic', 'Classic'),
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
    debug_mode = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for flag in FLAGS:
            self.fields['flag-{0}'.format(flag.value)] = forms.BooleanField(required=False, initial=False)

            # Add choice radio field if any.
            if flag.choices:
                self.fields['flag-{0}-choice'.format(flag.value)] = forms.ChoiceField(
                    choices=[(c.value, c.value) for c in flag.choices], required=False)
