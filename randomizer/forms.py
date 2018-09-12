from django import forms

from .models import REGIONS, MODES

# List of option checkbox fields for dynamic page generation.
FLAGS = (
    ('randomize_character_stats', 'Character Stats', 'Shuffles the starting stats for each character, as well as how much each stat grows by when levelling up, and how much the level-up bonuses are worth.'),
    ('randomize_drops', 'Drops', 'Shuffles the item reward received from battles.'),
    ('randomize_enemy_formations', 'Enemy Formations', 'Shuffles the potential enemies that can be encountered in normal battles.'),
    ('randomize_monsters', 'Monsters', 'Shuffles the stats of monsters, as well as potential status effects of their attacks.'),
    ('randomize_shops', 'Shops', 'Shuffles the items available in shops and their prices (including frog coin shops).'),
    ('randomize_equipment', 'Equipment Stats & Allowed Characters', 'Shuffles the stats granted by equipment (could be positive or negative) and which characters can equip them.'),
    ('randomize_buffs', 'Equipment Buffs', 'Shuffles special protections (elemental and status immunities) and attack/defense buffs for equipment.'),
    ('randomize_spell_stats', 'Character Spell Stats', 'Shuffles the FP cost, attack power and hit rate of spells, plus starting FP.'),
    ('randomize_spell_lists', 'Character Spell Lists', 'Shuffles which spells each character learns, and at what level they learn them.'),
    ('randomize_join_order', 'Character Join Order', 'Shuffles the order in which characters join the part. The spots at which a new character joins that party are unchanged.The character that joins the party will be the appropriate starting level for balance.'),
)


class GenerateForm(forms.Form):
    region = forms.ChoiceField(required=True, choices=REGIONS)
    seed = forms.Field(required=False)
    mode = forms.ChoiceField(required=True, choices=MODES)
    debug_mode = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for flag in FLAGS:
            self.fields[flag[0]] = forms.BooleanField(required=False, initial=False)
