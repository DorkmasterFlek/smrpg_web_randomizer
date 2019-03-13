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
    debug_mode = forms.BooleanField(required=False, initial=False)

    def _add_fields_from_flag(self, flag):
        """

        Args:
            flag (randomizer.logic.flags.Flag): Flag to add form fields for.

        """
        self.fields['flag-{0}'.format(flag.value)] = forms.BooleanField(required=False, initial=False)

        # Add choice radio field if any.
        if flag.choices:
            self.fields['flag-{0}-choice'.format(flag.value)] = forms.ChoiceField(
                choices=[(c.value, c.value) for c in flag.choices], required=False)

        # Process choices for any suboptions.
        for option in flag.options:
            self._add_fields_from_flag(option)

        # Process suboptions for this flag.
        for option in flag.options:
            self._add_fields_from_flag(option)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for category in CATEGORIES:
            for flag in category.flags:
                self._add_fields_from_flag(flag)
