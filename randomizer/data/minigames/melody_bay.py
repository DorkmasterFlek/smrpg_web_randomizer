
from __future__ import annotations
from dataclasses import dataclass
from math import floor

from ..variables.variable_names import *
from ..variables.action_script_names import *
from ..variables.event_script_names import *

from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.commands import (
    A_PlaySound as ASPlaySound,
    A_SetWalkingSpeed as ASSetWalkingSpeed,
    A_WalkNortheastSteps as ASWalkNortheastSteps,
    A_WalkSoutheastPixels as ASWalkSoutheastPixels,
    A_WalkSouthwestPixels as ASWalkSouthwestPixels,
    A_TransferToXYZF as ASTransferToXYZF,
    A_ReturnQueue as ASReturn,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import (
    ActionQueueAsync,
    ActionQueueSync,
    ClearBit,
    CopyVarToVar,
    DecVarFrom7000,
    Inc,
    Jmp,
    JmpIfBitClear,
    JmpIfVarEqualsConst,
    JmpIfVarNotEqualsConst,
    JmpToSubroutine,
    Mem7000AndConst,
    Pause,
    PauseActionScript,
    PlayMusicAtCurrentVolume,
    PlaySound,
    Return,
    RunEventAsSubroutine,
    Set7000ToTappedButton,
    SetBit,
    SetSyncActionScript,
    SetVarToConst,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.classes import (
    UsableEventScriptCommand,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.classes import (
    UsableActionScriptCommand,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import (
    MARIO,
    SCREEN_FOCUS,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.directions import *
from smrpgpatchbuilder.datatypes.overworld_scripts.action_scripts.arguments.sequence_speeds import *
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.types import (Flag, ShortVar, AreaObject)
from randomizer.data.variables.overworld_sfx_names import (
    SO000_SILENCE,
    SO036_TADPOLE_POND_STAFF_DO,
    SO037_TADPOLE_POND_STAFF_SO,
    SO038_TADPOLE_POND_STAFF_LA,
    SO039_TADPOLE_POND_STAFF_TI,
    SO040_TADPOLE_POND_STAFF_DO,
    SO041_TADPOLE_POND_STAFF_RE,
    SO042_TADPOLE_POND_STAFF_MI,
)
from randomizer.data.variables.music_names import M0017_TADPOLEPOND


class SongNote:
    val: int = 0
    name: str = ""
    sfx: int = 0


class Fa(SongNote):
    val = 0
    name = "Fa"
    sfx = SO036_TADPOLE_POND_STAFF_DO


class So(SongNote):
    val = 1
    name = "So"
    sfx = SO037_TADPOLE_POND_STAFF_SO


class La(SongNote):
    val = 2
    name = "La"
    sfx = SO038_TADPOLE_POND_STAFF_LA


class Ti(SongNote):
    val = 3
    name = "Ti"
    sfx = SO039_TADPOLE_POND_STAFF_TI


class Do(SongNote):
    val = 4
    name = "Do"
    sfx = SO040_TADPOLE_POND_STAFF_DO


class Re(SongNote):
    val = 5
    name = "Re"
    sfx = SO041_TADPOLE_POND_STAFF_RE


class Mi(SongNote):
    val = 6
    name = "Mi"
    sfx = SO042_TADPOLE_POND_STAFF_MI


@dataclass
class Note:
    """A single note in a song with its duration."""
    note: type[SongNote]
    duration: int


ORIGINAL_TOADOFSKY_CONFIRMATIONS = [
    "EVENT_1074_pause_59",
    "EVENT_1074_pause_64",
    "EVENT_1074_pause_64",
    "EVENT_1074_pause_71",
    "EVENT_1074_pause_71",
    "EVENT_1074_pause_78",
    "EVENT_1074_pause_78",
    "EVENT_1074_pause_85",
    "EVENT_1074_pause_92",
]


class Song:
    """A song for Melody Bay with methods to generate event scripts."""

    def __init__(
        self,
        notes: list[tuple[type[SongNote], int]],
        name: str,
        submitter: str = "Anonymous",
        submitter_credits: str = "ANONYMOUS",
        hint_1: str = "",
        hint_2: str = "",
        hint_3: str = "",
        scroll: str = "",
    ):
        self.notes = [Note(note=n, duration=d) for (n, d) in notes]
        self.name = name
        self.submitter = submitter
        self.submitter_credits = submitter_credits
        self.apprentice_hint_1 = hint_1
        self.apprentice_hint_2 = hint_2
        self.mole_hint = hint_3
        self.scroll_text = scroll

    def generate_starfish_hint(
        self, subscript: list[UsableActionScriptCommand]
    ) -> list[UsableActionScriptCommand]:
        """Generate modified action script subscript with song notes for starfish hint."""
        note_index = 0
        output: list[UsableActionScriptCommand] = []

        for cmd in subscript:
            if isinstance(cmd, ASPlaySound):
                if note_index < len(self.notes):
                    output.append(
                        ASPlaySound(
                            sound=self.notes[note_index].note.sfx,
                            channel=cmd.channel,
                            identifier=str(cmd.identifier) if cmd.identifier else None,
                        )
                    )
                else:
                    output.append(
                        ASPlaySound(
                            sound=SO000_SILENCE,
                            channel=cmd.channel,
                            identifier=str(cmd.identifier) if cmd.identifier else None,
                        )
                    )
                note_index += 1

            else:
                output.append(cmd)

        return output

    def generate_tadpole_hint(self) -> list[UsableEventScriptCommand]:
        """Generate the event script commands for the tadpole hint playback."""
        num_notes_to_hint = floor(len(self.notes) * 5 / 8)
        notes_to_hint = self.notes[:num_notes_to_hint]
        delays = [45 for _ in notes_to_hint]
        delays[0] = 30
        if len(delays) > 1:
            delays[len(delays) - 2] = 75
        delays[len(delays) - 1] = 100

        notes_to_write = list(zip(notes_to_hint, delays))

        output: list[UsableEventScriptCommand] = []

        for index, (note, delay) in enumerate(notes_to_write):
            output.extend([
                PlaySound(
                    sound=note.note.sfx,
                    channel=6,
                    identifier=f"EVENT_1088_play_sound_{index}",
                ),
                Pause(
                    length=delay,
                    identifier=f"EVENT_1088_pause_{index}",
                ),
            ])

        output.append(Return(identifier="EVENT_1088_ret"))

        return output

    def generate_input_script(self, song_order: int) -> list[UsableEventScriptCommand]:
        """Generate the input handling script for the song."""
        def prefix_command_name(cmd_name: str) -> str:
            return f"EVENT_{song_order + 1082}_{cmd_name}"

        note_variable_pairs = list(zip(
            self.notes,
            [SECONDARY_TEMP_7024, TEMP_7026, TEMP_7028, TEMP_702A, TEMP_702C, TEMP_702E, TEMP_7030, TEMP_7032]
        ))

        output: list[UsableEventScriptCommand] = []

        for index, (note, address) in enumerate(note_variable_pairs):
            p = prefix_command_name
            note_input: list[UsableEventScriptCommand] = [
                Set7000ToTappedButton(
                    identifier=p(f"set_7000_to_tapped_button_{index}")
                ),
                Pause(length=1, identifier=p(f"pause_{index}")),
                Mem7000AndConst(
                    value=0x0080,
                    identifier=p(f"mem_7000_and_const_{index}")
                ),
                JmpIfVarEqualsConst(
                    address=PRIMARY_TEMP_7000,
                    value=128,
                    destinations=[p(f"jmp_if_bit_clear_{index}")],
                    identifier=p(f"jmp_if_7000_equals_short_{index}"),
                ),
                Jmp(
                    destinations=[p(f"set_7000_to_tapped_button_{index}")],
                    identifier=p(f"jmp_{index}"),
                ),
                JmpIfBitClear(
                    bit=TEMP_7044_3,
                    destinations=[p(f"set_7000_to_tapped_button_{index}")],
                    identifier=p(f"jmp_if_bit_clear_{index}"),
                ),
                SetSyncActionScript(
                    target=AreaObject(0x14 + index),
                    action_script_id=A0571_MELODY_BAY_TADPOLE_AFFIRMATIVE,
                    identifier=p(f"set_action_script_sync_{index}"),
                ),
                CopyVarToVar(
                    from_var=ShortVar(0x7012),
                    to_var=PRIMARY_TEMP_7000,
                    identifier=p(f"set_7000_to_7000_short_mem_{index}"),
                ),
                JmpToSubroutine(
                    destinations=["EVENT_1074_jmp_if_var_equals_const_123"],
                    identifier=p(f"jmp_to_subroutine_{index}"),
                ),
                DecVarFrom7000(
                    address=ShortVar(0x7010),
                    identifier=p(f"dec_short_mem_{index}"),
                ),
                RunEventAsSubroutine(
                    event_id=E1085_MELODY_BAY_JUMP_ANIMATION,
                    identifier=p(f"jmp_to_subroutine__{index}"),
                ),
            ]

            if index < len(self.notes) - 1:
                note_input.extend([
                    CopyVarToVar(
                        from_var=ShortVar(0x7012),
                        to_var=address,
                        identifier=p(f"copy_var_to_var_{index}"),
                    ),
                    CopyVarToVar(
                        from_var=ShortVar(0x7012),
                        to_var=ShortVar(0x7010),
                        identifier=p(f"copy_var_to_var__{index}"),
                    ),
                    ActionQueueSync(
                        target=SCREEN_FOCUS,
                        subscript=[
                            ASSetWalkingSpeed(VERY_FAST),
                            ASWalkNortheastSteps(steps=2),
                            ASReturn(),
                        ],
                        identifier=p(f"action_queue_sync_13_{index}"),
                    ),
                    ActionQueueAsync(
                        target=AreaObject(0x14 + index + 1),
                        subscript=[
                            ASTransferToXYZF(
                                x=7 + index,
                                y=41 - (index * 2),
                                z=0,
                                direction=EAST
                            ),
                            ASWalkSoutheastPixels(pixels=5),
                            ASWalkSouthwestPixels(pixels=4),
                            ASReturn(),
                        ],
                        identifier=p(f"action_queue_async_{index}"),
                    ),
                    SetSyncActionScript(
                        target=AreaObject(0x14 + index + 1),
                        action_script_id=A0570_MELODY_BAY_TADPOLE_SWIMS,
                        identifier=p(f"set_action_script_sync___{index}"),
                    ),
                    SetVarToConst(
                        address=TEMP_70A9,
                        value=AreaObject(0x14 + index + 1),
                        identifier=p(f"set_{index}"),
                    ),
                    SetSyncActionScript(
                        target=MARIO,
                        action_script_id=A0515_MARIO_DURING_SONGS,
                        identifier=p(f"set_action_script_sync_____{index}"),
                    ),
                ])
            else:
                note_input.extend([
                    PauseActionScript(
                        target=MARIO,
                        identifier=p(f"pause_action_script_{index}"),
                    ),
                    CopyVarToVar(
                        from_var=ShortVar(0x7012),
                        to_var=ShortVar(address),
                        identifier=p(f"copy_var_to_var____{index}"),
                    ),
                    CopyVarToVar(
                        from_var=ShortVar(0x7012),
                        to_var=ShortVar(0x7010),
                        identifier=p(f"copy_var_to_var______{index}"),
                    ),
                    Pause(length=10, identifier=p(f"pause__{index}")),
                    SetVarToConst(
                        address=ShortVar(0x7012),
                        value=3,
                        identifier=p(f"copy_var_to_var_-_{index}"),
                    ),
                    CopyVarToVar(
                        from_var=ShortVar(0x7012),
                        to_var=ShortVar(0x7000),
                        identifier=p(f"set_7000_to_7000_short_mem___{index}"),
                    ),
                    DecVarFrom7000(
                        address=ShortVar(0x7010),
                        identifier=p(f"dec_short_mem___{index}"),
                    ),
                ])

                if len(self.notes) == 8:
                    note_input.append(
                        RunEventAsSubroutine(
                            event_id=E1085_MELODY_BAY_JUMP_ANIMATION,
                            identifier=p("jmp_to_subroutine_end"),
                        )
                    )
                elif len(self.notes) == 7:
                    note_input.append(
                        RunEventAsSubroutine(
                            event_id=E1087_MELODY_BAY_EXIT_WATER_ANIMATION,
                            identifier=p("jmp_to_subroutine_end"),
                        )
                    )
                else:
                    note_input.append(
                        RunEventAsSubroutine(
                            event_id=E1086_MELODY_BAY_SWIM_ANIMATION,
                            identifier=p("jmp_to_subroutine_end"),
                        )
                    )

                note_input.extend([
                    Jmp(
                        destinations=["EVENT_1074_set_bit_0"],
                        identifier=p(f"jmp__{index}"),
                    ),
                    Return(identifier=p(f"ret_{index}")),
                ])

            output.extend(note_input)

        return output

    def generate_playback_script(self, song_order: int) -> list[UsableEventScriptCommand]:
        """Generate the playback validation script for the song."""
        def prefix_command_name(cmd_name: str) -> str:
            return f"EVENT_{song_order + 1079}_{cmd_name}"

        note_variable_pairs = list(zip(
            self.notes,
            [SECONDARY_TEMP_7024, TEMP_7026, TEMP_7028, TEMP_702A, TEMP_702C, TEMP_702E, TEMP_7030, TEMP_7032]
        ))

        toadofsky_confirmations = [ORIGINAL_TOADOFSKY_CONFIRMATIONS[0]]
        for i in range(len(self.notes)):
            ratio = (
                round(len(ORIGINAL_TOADOFSKY_CONFIRMATIONS) * (i + 1) / len(self.notes))
                - 1
            )
            toadofsky_confirmations.append(ORIGINAL_TOADOFSKY_CONFIRMATIONS[ratio])

        script_note_checks: list[UsableEventScriptCommand] = []
        script_correctness_checks: list[UsableEventScriptCommand] = []
        script_toadofsky_reactions: list[UsableEventScriptCommand] = [
            JmpIfVarEqualsConst(
                address=PRIMARY_TEMP_7000,
                value=0,
                destinations=[toadofsky_confirmations[0]],
                identifier=prefix_command_name("jmp_if_7000_equals_reaction_0"),
            )
        ]

        for index, (note, address) in enumerate(note_variable_pairs):
            note_val = note.note.val
            duration = note.duration
            if duration == 0:
                duration = 35

            script_toadofsky_reactions.append(
                JmpIfVarEqualsConst(
                    address=PRIMARY_TEMP_7000,
                    value=index + 1,
                    destinations=[toadofsky_confirmations[index + 1]],
                    identifier=prefix_command_name(f"jmp_if_7000_equals_reaction_{index + 1}"),
                )
            )

            p = prefix_command_name
            note_check: list[UsableEventScriptCommand] = [
                CopyVarToVar(
                    from_var=address,
                    to_var=PRIMARY_TEMP_7000,
                    identifier=p(f"set_7000_to_7000_short_mem_notecheck_{index}"),
                ),
                JmpToSubroutine(
                    destinations=["EVENT_1074_jmp_if_var_equals_const_123"],
                    identifier=p(f"jmp_to_subroutine_notecheck_{index}"),
                ),
                JmpIfVarNotEqualsConst(
                    address=address,
                    value=note_val,
                    destinations=[p(f"set_action_script_sync_notecheck__{index}")],
                    identifier=p(f"jmp_if_var_not_equals_notecheck_{index}"),
                ),
                SetSyncActionScript(
                    target=AreaObject(0x14 + index),
                    action_script_id=A0571_MELODY_BAY_TADPOLE_AFFIRMATIVE,
                    identifier=p(f"set_action_script_sync_notecheck_{index}"),
                ),
                SetBit(
                    bit=Flag(0x7043, index),
                    identifier=p(f"set_bit_notecheck_{index}"),
                ),
                Jmp(
                    destinations=[p(f"pause_notecheck_{index}")],
                    identifier=p(f"jmp_notecheck_{index}"),
                ),
                SetSyncActionScript(
                    target=AreaObject(0x14 + index),
                    action_script_id=A0572_MELODY_BAY_TADPOLE_INCORRECT,
                    identifier=p(f"set_action_script_sync_notecheck__{index}"),
                ),
                ClearBit(
                    bit=Flag(0x7043, index),
                    identifier=p(f"clear_bit_notecheck_{index}"),
                ),
                Pause(
                    length=duration,
                    identifier=p(f"pause_notecheck_{index}"),
                ),
            ]

            script_note_checks.extend(note_check)

            correctness_check: list[UsableEventScriptCommand] = [
                JmpIfVarNotEqualsConst(
                    address=address,
                    value=note_val,
                    destinations=[
                        p(f"jmp_if_var_not_equals_const_correctcheck_{index + 1}")
                        if index < len(self.notes) - 1
                        else str(script_toadofsky_reactions[0].identifier)
                    ],
                    identifier=p(f"jmp_if_var_not_equals_const_correctcheck_{index}"),
                ),
                Inc(
                    address=PRIMARY_TEMP_7000,
                    identifier=p(f"inc_correctcheck_{index}"),
                ),
            ]

            script_correctness_checks.extend(correctness_check)

        final_script: list[UsableEventScriptCommand] = []
        final_script.extend(script_note_checks)
        final_script.extend([
            Pause(length=45, identifier=prefix_command_name("pause_mandatory")),
            PlayMusicAtCurrentVolume(
                music=M0017_TADPOLEPOND,
                identifier=prefix_command_name("play_music_current_volume_mandatory"),
            ),
            SetVarToConst(
                address=ShortVar(0x7000),
                value=0,
                identifier=prefix_command_name("set_mandatory"),
            ),
        ])
        final_script.extend(script_correctness_checks)
        final_script.extend(script_toadofsky_reactions)

        return final_script


all_songs = [
    Song(
        [(Re, 15), (Mi, 100), (Re, 7), (Do, 7), (Ti, 65), (La, 65), (So, 0)],
        "Chrono Cross - Time's Scar",
        hint_1=' When was the start of all this?\n ♪“Re Mi Re Do Ti La So”. When did\n the cogs of fate begin to turn?[await]',
        hint_2=' From deep within the flow of\n time... ♪“Re Mi Re Do Ti La So”.[await]',
        hint_3=' Whilst our laughter echoed,\n “Re Mi Re Do Ti La So”,\n under cerulean skies...[await]',
        scroll='\n[center]Re Mi Re Do Ti La So[await]'),
    Song(
        [(Fa, 20), (Ti, 20), (Re, 40), (Fa, 20), (Ti, 20), (Re, 0)],
        "Song of Soaring",
        submitter="TriumphantBass",
        submitter_credits="TRIUMPHANTBASS",
        hint_1=' My favorite song?[await][page]\n It\'s the Song of Soaring!\n ♪“Fa Ti Re, Fa Ti Re”.\n It gives me a flutter![await]',
        hint_2=' The Moleville miners were singing,\n ♪“Fa Ti Re, Fa Ti Re”.\n Light and breezy![await]',
        hint_3='[center]\nRepeat after me![await][page]\n We\'ll go “FA”r~[delay]\n Build equi“TY”~[delay]\n Get a “RA”ise~[await][page]\n\n Once more![await]',
        scroll='\n[center]Fa Ti Re Fa Ti Re[await]'),
    Song(
        [(Do, 12), (La, 23), (Do, 12), (Ti, 23), (Do, 12), (Ti, 23), (So, 0)],
        "Green Hill Zone",
        hint_1=' Gotta go fast!\n ♪“Do La Do Ti Do Ti So”.[await]',
        hint_2=' ♪“Do La Do Ti Do Ti So”.\n A song that goes great with\n chili dogs.[await]',
        hint_3=' Do La Do Ti Do Ti So.\n You\'re too slow![await]',
        scroll='\n[center]Do La Do Ti Do Ti So[await]'),
    Song(
        [(So, 25), (La, 25), (Ti, 50), (Ti, 25), (Re, 25), (La, 50), (La, 25), (Ti, 0)],
        "Earthbound - Smiles and Tears",
        hint_1=' ♪“So La Ti Ti Re La La Ti”.\n I miss you...[await]',
        hint_2=' ♪“So La Ti Ti Re La La Ti”.\n Now say, “fuzzy pickles!”[await]',
        hint_3='[center] Earthbound?\n “SO” “LA”st year.\n “TI”ck tock![await][page]\n No “TI”me to spa“RE”,\n p“LA”y the “LA”test “TI”tle,\n Mother 3![await]',
        scroll='\n[center]So La Ti Ti Re La La Ti[await]'),
    Song(
        [(So, 40), (Fa, 40), (Mi, 80), (Re, 20), (Mi, 40), (Re, 10), (Ti, 10), (Do, 0)],
        "I See The Light",
        submitter="TriumphantBass",
        submitter_credits="TRIUMPHANTBASS",
        hint_1=' My favorite song?[await][page]\n It\'s “I See The Light!”\n ♪“So Fa Mi Re Mi Re Ti Do”.\n It\'s warm and bright![await]',
        hint_2=' The moles adapted it up from\n somewhere,\n ♪“So Fa Mi Re Mi Re Ti Do”.[await]\n Theirs is somewhat shifted.[await]',
        hint_3=' Our song?[await]\n “SO” “FA”r “ME”, I\'ve been\n “RE”-“MI”, “RE”-“MI”-niscing.[await][page]\n Think I\'ll “RE”-“TI”-re soon, once\n I\'ve made the “DO”ugh![await]',
        scroll='\n[center]So Fa Mi Re Mi Re Ti Do[await]'),
    Song(
        [(La, 18), (La, 35), (Re, 35), (Do, 35), (La, 70), (So, 18), (La, 35), (Do, 0)],
        "TNT",
        submitter="Alex.the.Riddler",
        submitter_credits="ALEX.THE.RIDDLER",
        hint_1=' \'Cause I\'m TNT, Dynamite.\n ♪“La La Re Do La So La Do”.[await]',
        hint_2=' I swam all the way to Australia\n and discovered this cool band.\n ♪“La La Re Do La So La Do”.[await]',
        hint_3=' This is the song we sing when we\n blow up the TNT![delay]\n[center]“So Fa Mi Re Mi Re Ti Do”[await]',
        scroll='\n[center]So Fa Mi Re Mi Re Ti Do[await]'),
    Song(
        [(Fa, 15), (So, 15), (Mi, 42), (Re, 8), (Do, 8), (Ti, 0)],
        "SMB3 Flute",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the SMB3 Flute music,\n ♪“Fa So Mi Re Do Ti”.\n Toadofsky\'s fond of it, too![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the SMB3 Flute song.\n ♪“Fa So Mi Re Do Ti”.[await]\n It makes you feel like you\'re being\n whisked away...[await]',
        hint_3=' Some of us are learnin\' how to play\n the flute. We only know how to play\n the tune from SMB3, though.[await]',
        scroll='\n[center]Fa So Mi Re Do Ti[await]'),
    Song(
        [(La, 80), (Ti, 40), (La, 40), (Fa, 20), (La, 20), (Re, 40), (Ti, 0)],
        "Elegy of Emptiness",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Elegy of Emptiness,\n ♪“La Ti La Fa La Re Ti”.\n Toadofsky\'s fond of it, too![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Elegy of Emptiness.\n ♪“La Ti La Fa La Re Ti”.[await]\n It\'s got...[delay] soul?[await][pause] Wait,[delay] that\'s\n not right...[await]',
        hint_3=' We\'ve been singin\' a new song,\n “Elegy of Emptiness”.[await][pause] Pa\' Mole\n heard it from somewhere.[await]\n It\'s kinda creepy, but it grows\n on ya![await]',
        scroll='\n[center]La Ti La Fa La Re Ti[await]'),
    Song(
        [(Mi, 15), (Ti, 45), (Mi, 15), (Ti, 15), (Re, 15), (Mi, 0)],
        "Prelude of Light",
        submitter="NYRambler",
        submitter_credits="NYRAMBLER",
        hint_1=' I\'ve heard it played on an\n Ocarina before![await]',
        hint_2=' Perhaps it\'s a PRELUDE to\n something that\'s... LIGHT?[await]',
        hint_3=' “MI”gh“TI” fine weather for some\n “MI”gh“TI” “RE”laxing “MI”ning![await]',
        scroll='\n[center]Mi Ti Mi Ti Re Mi[await]'),
    Song(
        [(Ti, 20), (Re, 20), (Do, 40), (La, 20), (Ti, 20), (La, 40), (So, 0)],
        "Free Bird",
        submitter="NYRambler",
        submitter_credits="NYRAMBLER",
        hint_1=' I\'ve heard someone request it\n at a concert many times![await]',
        hint_2=' If I leave here tomorrow, will you\n still remember me?[await]',
        hint_3=' “TI”me to “Re”member how to “Do”\n this... “La”st “Ti”me, “La”st\n “So”und![await]',
        scroll='\n[center]Ti Re Do La Ti La So[await]'),
    Song(
        [
            (Mi, 20),
            (Re, 10),
            (Do, 20),
            (Do, 110),
            (Mi, 20),
            (Re, 10),
            (Do, 20),
            (Re, 0),
        ],
        "Under the Sea",
        submitter="Alex.the.Riddler",
        submitter_credits="ALEX.THE.RIDDLER",
        hint_1=' Darling, it\'s better down where it\'s\n wetter. Take it from me![await]',
        hint_2=' Sometimes I like to think of myself\n as half a mermaid!\n ♪“Mi Re Do Do Mi Re Do Re”.[await]',
        hint_3=' Have you ever seen a mermaid on\n your travels, Mario?[await]',
        scroll='\n[center]Mi Re Do Do Mi Re Do Re[await]'),
    Song(
        [(Ti, 35), (Do, 35), (La, 18), (Do, 18), (Re, 18), (So, 18), (Ti, 18), (Do, 0)],
        "I'm Blue",
        submitter="Alex.the.Riddler",
        submitter_credits="ALEX.THE.RIDDLER",
        hint_1='\n[center]I\'m blue, da ba dee da ba daa.[await]',
        hint_2=' What if the whole world was blue\n like the ocean?[await]',
        hint_3=' Yo listen up, here\'s the story,\n about a little guy that lives in a\n blue world! Ti Do La Do Re So Ti Do[await]',
        scroll='\n[center]Ti Do La Do Re So Ti Do[await]'),
    Song(
        [
            (So, 60),
            (La, 100),
            (La, 60),
            (Ti, 60),
            (Re, 10),
            (Do, 10),
            (Ti, 10),
            (So, 0),
        ],
        "Never Gonna Give You Up",
        submitter="Alex.the.Riddler",
        submitter_credits="ALEX.THE.RIDDLER",
        hint_1=' Bet you aren\'t expecting to get\n Rickrolled![await]',
        hint_2=' Never gonna give you up!\n Never gonna let you down![await]',
        hint_3=' Never gonna run around, and\n desert you!\n So La La Ti Re Do Ti So~[await]',
        scroll='\n[center]So La La Ti Re Do Ti So[await]'),
    Song(
        [(Fa, 40), (So, 20), (Fa, 20), (Ti, 40), (La, 40), (Fa, 0)],
        "Requiem of Spirit",
        submitter="Mr. Thee",
        submitter_credits="MR. THEE",
        hint_1=' I got Silver Gauntlets!\n I can finally play that darn song!!\n ♪“Fa So Fa Ti La Fa”.[await]',
        hint_2=' My favorite song?[await][page]\n It\'s the song that saves me from\n having to enter Wasteland to get\n into the Spirit Temple.[await]\n ♪“Fa So Fa Ti La Fa”.[await]',
        hint_3=' Have you ever heard a song that\n can warp you to the desert?[await]\n I don\'t think it works in our world.[delay]\n You have to go through the sewers\n to warp to our desert.[await]',
        scroll='\n[center]Fa So Fa Ti La Fa[await]'),
    Song(
        [(La, 35), (Re, 70), (La, 35), (Re, 35), (Ti, 70), (La, 35), (So, 35), (La, 0)],
        "Apache (Jump on it)",
        submitter="Alex.the.Riddler",
        submitter_credits="ALEX.THE.RIDDLER",
        hint_1=' Mario! Jump on it! That\'s like\n what you do, right?[await]',
        hint_2=' Think of this song when you\'re\n doing super jumps!\n ♪“La Re La Re Ti La So La”.[await]',
        hint_3=' “LA”y me to “RE”st. “LA”y me to\n “RE”st.[await][pause] “TI”s “LA”ter than you\n think.[await][pause] “SO” much “LA”ter than\n you think.~[await]',
        scroll='\n[center]La Re La Re Ti La So La[await]'),
    Song(
        [(So, 35), (Do, 35), (Re, 35), (Mi, 35), (So, 35), (Do, 35), (Ti, 35), (Do, 0)],
        "Mother 3 Love Theme",
        submitter="CousinCatnip",
        submitter_credits="COUSINCATNIP",
        hint_1=' My favorite song?[await][page]\n I think it\'s called the\n “Theme of Hearts”.[await]\n No,[delay] wait,[delay] that\'s not right.[await]\n Maybe it was “Glove Team”?[await]\n No, no,[delay] I got it![await][page]\n It\'s “Love Theme”.\n ♪“So Do Re Mi So Do Ti Do”.[await]\n Toadofsky may like it,\n but let\'s make him LOVE it![await]',
        hint_2=' My favorite song?[await][page]\n I think it\'s called the\n “Theme of Hearts”.[await]\n No,[delay] wait,[delay] that\'s not right.[await]\n Maybe it was “Glove Team”?[await]\n No, no,[delay] I got it![await][page]\n It\'s “Love Theme”.\n ♪“So Do Re Mi So Do Ti Do”.[await]\n Toadofsky may like it,\n but let\'s make him LOVE it![await]',
        hint_3=' “Love Theme” is all the rage. Check\n it out:[await][page]\n\n[center]We feel it in our “SO”ul~[await][page]\n\n[center]With everything we “DO”~[await][page]\n\n[center]My heart is still a w“RE”ck~[await][page]\n\n[center]So it\'s “MI”ghty time to change~[await][page]\n\n[center]I\'m diggin\' up to re“SO”il~[await][page]\n\n[center]“DO” you know it\'s me?~[await][page]\n\n[center]Feelin\' kinda “TI”red~[await][page]\n\n[center]But I “DO”n\'t want it to end!~[await]',
        scroll='\n[center]So Do Re Mi So Do Ti Do[await]'),
    Song(
        [(Mi, 35), (Re, 18), (Mi, 42), (Re, 18), (Mi, 35), (So, 18), (La, 0)],
        "SMB3 Overworld bar 1",
        submitter="SeanCass",
        submitter_credits="SEANCASS",
        hint_1=' My favorite song?[await][page]\n It\'s “SMB3 Overworld Bar 1”.\n ♪“Mi Re Mi Re Mi So La”.\n Toadofsky\'s fond of it, too![await]',
        hint_2=' The time signature for the song is\n 1-1.[await][pause] At least, according to\n “Super Mario Bros. 3.”[await]',
        hint_3=' It\'s the Moleville “MI”nes!\n “RE”ad all about it![await][page]\n I wish I had a Bambino Bomb for\n these “MI”nes, “RE”ally I wish!\n Don\'t “MI”nd if I do![await][page]\n “SO” you gotta find that bomb,\n I hope it\'s not your “LA”st\n key item![await]',
        scroll='\n[center]Mi Re Mi Re Mi So La[await]'),
    Song(
        [(Mi, 35), (Re, 18), (Mi, 24), (Mi, 24), (Do, 18), (Re, 0)],
        "SMB3 Overworld bar 2",
        submitter="SeanCass",
        submitter_credits="SEANCASS",
        hint_1=' My favorite song?[await][page]\n It\'s “SMB3 Overworld Bar 2”.\n ♪“Mi Re Mi Mi Do Re”.\n Toadofsky\'s fond of it, too![await]',
        hint_2=' My favorite song? It\'s...[await][page]\n [delay]Wait,[delay] I thought this song was from\n Mario 3, but it\'s the second part?[await][page]\n OH![await][pause] It\'s the 2nd bar of 1-1![await][pause]\n I get it now.[await]',
        hint_3=' Moles “MI”ne! We “RE”ally dig![await]\n Moles “MI”ne for “MI”nerals![await]\n Wait, “DO” we “RE”ally?[await]',
        scroll='\n[center]Mi Re Mi Mi Do Re[await]'),
    Song(
        [(Mi, 35), (Re, 18), (Mi, 24), (So, 24), (La, 24), (Do, 0)],
        "SMB3 Overworld bar 4",
        submitter="SeanCass",
        submitter_credits="SEANCASS",
        hint_1=' My favorite song?[await][page]\n It\'s “SMB3 Overworld Bar 4”.\n ♪“Mi Re Mi So La Do”.\n Toadofsky\'s fond of it, too![await]',
        hint_2=' What a nice closing bar to Grass\n Land, a 1 to 1 representation if I\n do say so myself.[await]\n I don\'t mean the Juice Bar, though![await]',
        hint_3=' We live in the “MI”nes, “RE”ad between the lines![await][pause] These “MI”nes\n are ours![await][pause] “SO” make like a “LA”ke\n and “DO”n\'t quake![await]',
        scroll='\n[center]Mi Re Mi So La Do[await]'),
    Song(
        [(Mi, 35), (Mi, 35), (Re, 35), (Do, 35), (Ti, 35), (La, 35), (So, 35), (Fa, 0)],
        "I'm falling down all these stairs",
        submitter="GoodMorningCrono",
        submitter_credits="GOODMORNINGCRONO",
        hint_1=' I warned you about stairs bro!\n I told you dog![await]',
        hint_2=' I told you man!\n I TOLD you about stairs![await]',
        hint_3=' I love to “ME” “ME”, yes I\n “RE”ally “DO”![await][pause] Oh no, it\'s “TI”me\n for work, I\'m “LA”te, “SO” please\n “FA”hgive me dude![await]',
        scroll='\n[center]Mi Mi Re Do Ti La So Fa[await]'),
    Song(
        [(La, 15), (Ti, 15), (Do, 15), (Re, 15), (Ti, 30), (So, 15), (La, 15)],
        "The Lick",
        submitter="frozenspade",
        submitter_credits="FROZENSPADE",
        hint_1=' My favorite song?[await][page]\n It\'s “The Lick”.\n ♪“La Ti Do Re Ti So La”.\n Toadofsky\'s a fan of Jazz.[await]',
        hint_2=' My favorite song?[await][page]\n It\'s “The Lick”.\n ♪“La Ti Do Re Ti So La”.\n Ya like Jazz?[await]',
        hint_3=' La Ti Do Re Ti So La~[delay]\n Hmm,[delay] where have I heard this\n before?[await]',
        scroll='\n[center]La Ti Do Re Ti So La[await]'),
    Song(
        [(La, 15), (Fa, 15), (La, 15), (Ti, 15), (So, 15), (La, 15), (Ti, 15), (Re, 0)],
        "Pekora BGM",
        submitter="SushiKishi",
        submitter_credits="SUSHIKISHI",
        hint_1=' For some reason, I have a craving\n for almonds.[await][pause] And...[delay] explosions?[await]\n ♪“La Fa La Ti So La Ti Re”.[await]\n Say,[delay] did you just hear laughing?[await]',
        hint_2=' I was watching this rabbit on TV\n earlier today, and now I can\'t get\n the song out of my head.[await][page]\n ♪ U-sa-da Pe![delay] Ko![delay] Ra![delay]\n[center]U-sa-da Pe![delay] Ko![delay] Ra![delay]\n[center]U-sa-da PEKO-PEKO-CHAN![delay]\n[center]PEKO-PEKO-CHAN![await]',
        hint_3=' D-DIG, D-DIG DIG DIG! What\'s the\n cutest song in the entire game?[await]\n D-DIG, D-DIG DIG DIG!\n It\'s Pekora\'s BGM![await][page]\n D-DIG, D-DIG DIG DIG!\n And how does that song go?[await]\n D-DIG, D-DIG DIG DIG! It goes\n “LA FA LA TI SO LA TI RE”![await]',
        scroll='\n[center]La Fa La Ti So La Ti Re[await]'),
    Song(
        [(So, 30), (La, 15), (Fa, 30), (So, 75), (Ti, 30), (La, 15), (Fa, 30), (So, 0)],
        "John Cena Trumpets",
        submitter="SushiKishi",
        submitter_credits="SUSHIKISHI",
        hint_1=' I have a date today, but I lost my\n watch. Do you have the time?[await]\n ♪“So La Fa So Ti La Fa So”.[await]\n What time was my date again...?\n OH NO! THE TIME IS NOW![await]',
        hint_2=' Someone gave me some sheet\n music to pass on to Toadofsky.[await]\n Unfortunately, I dropped the scroll\nin the water, the ink washed off,\n and I can\'t read the notes.[await]\n Even with the five-second rule, my\n time was up. Your time is now! Go\n find those notes for me, please![await]',
        hint_3=' All our kids\'re gettin\' to that age\n where they\'re really into pro\n wrestling.[await][pause] They can\'t stop singin\'\n John Cena\'s entrance music![await]\n I promise you kids, I can see ya!\n And I can DEFINITELY hear ya![await]\n (So La Fa So Ti La Fa So~...)[await]',
        scroll='\n[center]So La Fa So Ti La Fa So[await]'),
    Song(
        [(Ti, 70), (Re, 35), (La, 88), (Ti, 70), (Re, 35), (La, 0)],
        "Zelda's Lullaby",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s Zelda\'s Lullaby,\n ♪“Ti Re La Ti Re La”.\n Toadofsky\'s fond of it, too![await]',
        hint_2=' My favorite song?[await][page]\n It\'s Zelda\'s Lullaby.\n ♪“Ti Re La Ti Re La”.[await]\n It\'s comforting, isn\'t it?[await]',
        hint_3=' I swear, if these fellas don\'t stop\n singin\' lullabies, we\'re all gonna\n fall asleep on the job![await]',
        scroll='\n[center]Ti Re La Ti Re La[await]'),
    Song(
        [(Re, 18), (Ti, 18), (La, 70), (Re, 18), (Ti, 18), (La, 0)],
        "Epona's Song",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s Epona\'s Song,\n ♪“Re Ti La Re Ti La”.\n Toadofsky\'s fond of it, too![await]',
        hint_2=' My favorite song?[await][page]\n It\'s Epona\'s Song.\n It fills me with joy![await]',
        hint_3=' What\'s that? You wanna hear\n Epona\'s Song? Well, alright then![await][page]\n\n[center]Standing here, I “RE”member~[await][page]\n\n[center]That “TI”me when~[await][page]\n\n[center]My mother wrote for you~[await][page]\n\n[center]This bal“LA”d~[await][page]\n [delay].[delay].[delay].[delay]Whoa, I gotta get back to work![await]\n But the song repeats that part.[await]',
        scroll='\n[center]Re Ti La Re Ti La[await]'),
    Song(
        [(Re, 60), (Mi, 60), (Re, 60), (Mi, 60), (Re, 60), (Mi, 60), (Ti, 0)],
        "The Brink of Time",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s The Brink of Time,\n ♪“Re Mi Re Mi Re Mi Ti”.\n Toadofsky\'s fond of it, too![await]',
        hint_2=' My favorite song?[await][page]\n It\'s The Brink of Time.\n ♪“Re Mi Re Mi Re Mi Ti”.[await]\n It\'s quite melancholic.[await]',
        hint_3=' Feels like I\'m gonna be workin\'\n here \'til the end of time![await]',
        scroll='\n[center]Re Mi Re Mi Re Mi Ti[await]'),
    Song(
        [(Fa, 18), (La, 18), (Ti, 35), (Fa, 18), (La, 18), (Ti, 0)],
        "Saria's Song",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s Saria\'s Song,\n ♪“Fa La Ti Fa La Ti”.\n It\'s got a hot beat![await]',
        hint_2=' My favorite song?[await][page]\n It\'s Saria\'s Song.[await]\n A song like that is sure to cheer\n you up when you\'re feeling down![await]',
        hint_3=' ♪(Fa La Ti, Fa La Ti...)[await]\n I visited the forest,[delay] an\' now I\n can\'t get this tune outta my head![await]',
        scroll='\n[center]Fa La Ti Fa La Ti[await]'),
    Song(
        [(Ti, 12), (So, 12), (Mi, 60), (Ti, 12), (So, 12), (Mi, 0)],
        "Sun's Song",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Sun\'s Song,\n ♪“Ti So Mi Ti So Mi”.\n Toadofsky\'s fond of it, too![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Sun\'s Song.\n ♪“Ti So Mi Ti So Mi”.\n I wonder what it means?[await]',
        hint_3=' I tell ya, I can\'t wait for the work\n day to be over.[await][pause] I wish there was a\n way to make the day pass quicker![await]',
        scroll='\n[center]Ti So Mi Ti So Mi[await]'),
    Song(
        [(Ti, 35), (Fa, 70), (So, 35), (Ti, 35), (Fa, 70), (So, 0)],
        "Song of Time",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Song of Time,\n ♪“Ti Fa So Ti Fa So”.\n It makes me reflect...[await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Song of Time.\n ♪“Ti Fa So Ti Fa So”.\n It\'s mysterious, isn\'t it?[await]',
        hint_3=' Have ya ever wished you could\n just give the day a do-over,\n Mario?[await]',
        scroll='\n[center]Ti Fa So Ti Fa So[await]'),
    Song(
        [(So, 35), (Fa, 70), (Ti, 35), (So, 35), (Fa, 70), (Ti, 0)],
        "Inverted Song of Time",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Inverted Song of Time,\n ♪“So Fa Ti So Fa Ti”.\n A watched pot never boils.[await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Inverted Song of Time.\n ♪“So Fa Ti So Fa Ti”.\n Does it make the day drag on?[await]',
        hint_3=' Today\'s going so slow... It feels like somebody slowed down the clock![await]',
        scroll='\n[center]So Fa Ti So Fa Ti[await]'),
    Song(
        [(Ti, 20), (Ti, 15), (Fa, 10), (Fa, 10), (So, 10), (So, 0)],
        "Song of Double Time",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Song of Double Time,\n ♪“Ti Ti Fa Fa So So”.\n It makes the day go by quickly![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Song of Double Time.\n ♪“Ti Ti Fa Fa So So”.[await][page]\n Is it me, or did it just get darker out?[await]',
        hint_3=' It\'d be mighty handy if I could just jump 12 hours into the future and be outta here![await]',
        scroll='\n[center]Ti Ti Fa Fa So So[await]'),
    Song(
        [(Fa, 12), (So, 12), (Re, 55), (Fa, 12), (So, 12), (Re, 0)],
        "Song of Storms",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Song of Storms,\n ♪“Fa So Re Fa So Re”.\n It\'s wily![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Song of Storms.[await][pause] But I\'m\n worried if I recite it here, it\'ll\n cause a flood.[await]',
        hint_3=' ♪(Fa So Re, Fa So Re...)[await]\n This tune makes my head spin, but\n I can\'t get it outta my head![await]',
        scroll='\n[center]Fa So Re Fa So Re[await]'),
    Song(
        [(Fa, 18), (Re, 18), (Ti, 80), (La, 18), (Ti, 18), (La, 0)],
        "Minuet of Forest",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Minuet of Forest,\n ♪“Fa Re Ti La Ti La”.\n Isn\'t it cute?[await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Minuet of Forest.[await][pause] Such a\n cute and sprightly song![await]',
        hint_3='\n[center]“FA”r away in a fo“RE”st~[await][page]\n\n[center]“TI”me seems to stand still~[await][page]\n\n Wood“LA”nd creatures so “TI”mid~[await][page]\n\n[center]Live among “LA”vish green hills~[await][page]\n Oops![delay] I reckon that\'s about all I\n can remember from that song...[await]',
        scroll='\n[center]Fa Re Ti La Ti La[await]'),
    Song(
        [(So, 15), (Fa, 15), (So, 15), (Fa, 15), (Ti, 15), (La, 15), (Ti, 15), (La, 0)],
        "Bolero of Fire",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Bolero of Fire,\n ♪“So Fa So Fa Ti La Ti La”.\n What a great rhythm![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Bolero of Fire.[await]\n It makes me want to just start\n dancing, and I don\'t have legs![await]',
        hint_3=' ♪(So Fa So Fa Ti La Ti La...)[await]\n I swear, this tune\'s a hot beat![await]\n Does it feel a little warm in here?[await]',
        scroll='\n[center]So Fa So Fa Ti La Ti La[await]'),
    Song(
        [(Fa, 40), (So, 40), (La, 40), (La, 40), (Ti, 40)],
        "Serenade of Water",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Serenade of Water,\n ♪“Fa So La La Ti”.\n It\'s so breezy![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Serenade of Water.\n ♪“Fa So La La Ti”.\n It gives me the chills![await]',
        hint_3=' Boy howdy, I sure wish I was\n somewhere a little colder\n right now!',
        scroll='\n[center]Fa So La La Ti[await]'),
    Song(
        [(Ti, 35), (La, 35), (La, 18), (Fa, 18), (Ti, 18), (La, 18), (So, 18)],
        "Nocturne of Shadow",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Nocturne of Shadow,\n ♪“Ti La La Fa Ti La So”.\n It\'s unsettling![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Nocturne of Shadow.[await]\n Something about it just draws me\n right in.[await]',
        hint_3=' ♪(Ti La La Fa Ti La So...)[await]\n Y\'know, workin\' in these mines can\n be mighty creepy sometimes...[await]',
        scroll='\n[center]Ti La La Fa Ti La So[await]'),
    Song(
        [(Re, 18), (Ti, 18), (Re, 18), (Ti, 35), (Fa, 35), (La, 70), (Fa, 0)],
        "Sonata of Awakening",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Sonata of Awakening,\n ♪“Re Ti Re Ti Fa La Fa”.\n Toadofsky\'s font of it, too![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Sonata of Awakening.[await]\n I\'m afraid that if I hum it,\n something weird will happen.[await]',
        hint_3=' ♪(Re Ti Re Ti Fa La Fa...)[await]\n Y\'know, it\'s weird, but I\'ve been\n havin\' some trouble sleeping.[await]',
        scroll='\n[center]Re Ti Re Ti Fa La Fa[await]'),
    Song(
        [(Ti, 35), (La, 35), (Fa, 35), (Ti, 35), (La, 35), (Fa, 0)],
        "Song of Healing",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Song of Healing,\n ♪“Ti La Fa Ti La Fa”.\n Toadofsky\'s font of it, too![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Song of Healing.[await]\n I feel so clean and refreshed\n every time I hear it.[await]',
        hint_3='\n[center]When the “TI”me comes~[await][page]\n\n[center]To “LA”y down to rest~[await][page]\n\n[center]I will “FA”ll asleep~[await][page]\n\n[center]And my soul will refresh~![await][page]\n If you sing that song twice in\n a row...[delay] well, you\'ll be feelin\'\n much better![await]',
        scroll='\n[center]Ti La Fa Ti Ta Fa[await]'),
    Song(
        [(Fa, 35), (La, 35), (Ti, 35), (Fa, 35), (La, 35), (Ti, 35), (La, 35), (Fa, 0)],
        "Goron Lullaby",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Goron Lullaby,\n ♪“Fa La Ti Fa La Ti La Fa”.\n Toadofsky\'s font of it, too![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Goron Lullaby.\n ♪“Fa La Ti Fa La Ti La Fa”.\n Don\'t fall asleep![await]',
        hint_3=' I swear, if these fellas don\'t stop\n singin\' lullabies, we\'re all gonna\n fall asleep on the job![await]',
        scroll='\n[center]Fa La Ti Fa La Ti La Fa[await]'),
    Song(
        [(Ti, 60), (Re, 12), (Do, 12), (La, 60), (Fa, 12), (Ti, 12), (La, 0)],
        "New Wave Bossa Nova",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the New Wave Bossa Nova,\n ♪“Ti Re Do La Fa Ti La”.\n Toadofsky\'s font of it, too![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the New Wave Bossa Nova.[await]\n It\'d be cool if a giant turtle\n appeared in our pond, too.[await]',
        hint_3=' ♪(Ti Re Do La Fa Ti La...)[await]\n I\'m tellin ya, I could use a\n vacation![await]',
        scroll='\n[center]Ti Re Do La Fa Ti La[await]'),
    Song(
        [(Ti, 80), (La, 40), (Fa, 40), (La, 40), (Ti, 40), (Re, 60)],
        "Oath to Order",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n It\'s the Oath to Order,\n ♪“Ti La Fa La Ti Re”.\n Toadofsky\'s font of it, too![await]',
        hint_2=' My favorite song?[await][page]\n It\'s the Oath to Order.[await]\n I heard that song carries great\n power in a far-off land.[await]',
        hint_3=' Wassat? You wanna hear our\n song?[await][pause] Well, here goes![await][page]\n\n[center]Through the passage of “TI”me~[await][page]\n\n[center]And in “LA”nds “FA”r apart~[await][page]\n\n[center]We shall always be friends~[await][page]\n\n[center]I dec“LA”re this with heart~[await][page]\n\n[center]I will s“TI”ll heed your call~[await][page]\n\n[center]If you need me, my friend~[await][page]\n\n[center]I will always be the“RE”~[await][page]\n\n[center]Until the very end~![await]',
        scroll='\n[center]Ti La Fa La Ti Re[await]'),
    Song(
        [(Fa, 12), (So, 12), (Ti, 12), (Re, 12), (Ti, 12), (Do, 12)],
        "For the Animals of the Forest",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=' My favorite song?[await][page]\n ♪“Fa So Ti Re Ti Do”.\n I heard it in a forest once. I\n suspected the flutist was a ghost.[await]',
        hint_2=' My favorite song?[await][page]\n ♪“Fa So Ti Re Ti Do”.\n Most animals love that song.\n Especially birds.[await]',
        hint_3=' Don\'t ya wish sometimes that you\n could just fly anywhere ya wanted?[await]',
        scroll='\n[center]Fa So Ti Re Ti Do[await]'),
    # Song(
    #     [(So, 20), (Re, 20), (Do, 20), (La, 20), (Ti, 30), (Ti, 30), (Do, 30)],
    #     "UNDERTALE - His Theme",
    #     submitter="Kim Delicious",
    #     submitter_credits="KIM DELICIOUS",
    #     hint_1=' Hey, Toby, I forget. Who\'s theme is\n this, again?[await]',
    #     hint_2=' I heard that monsters that hear\n this song are filled with\n determination![await]',
    #     hint_3=' Oh yeah, the Moleville Blues![await][page]\n Even if it\'s His Theme, those cute\n bells make me cry every time I listen\n to it.[await]',
    #     scroll='\n[center]So Re Do La Ti Ti Do[await]'),
    Song(
        [(So, 35), (La, 11), (Re, 100), (La, 11), (Do, 11), (Re, 35), (Mi, 11), (Ti, 0)],
        "Chasing a Dream",
        submitter="Liquid Cat",
        submitter_credits="LIQUID CAT",
        hint_1=""" My favorite song?[await][page]\n It's Chasing a Dream.\n ♪“So La Re La Do Re Mi Ti”.[await][page]\n Every time it plays in Rayman\n Origins/Legends...the feels![await]""",
        hint_2=""" My favorite song?[await][page]\n It's Chasing a Dream.\n ♪“So La Re La Do Re Mi Ti”.[await][page]\n Perfect song for a mad dash\n through the underworld![await]""",
        hint_3=""" The Moleville Blues.[await]\n “So La Re La Do Re Mi Ti”.[await][page]\n *sniff* Hearing it, I just want to\n chase my dream![await]""",
        scroll='\n[center]So La Re La Do Re Mi Ti[await]'),
    Song(
        [(Mi, 25), (Do, 75), (Ti, 25), (Do, 75), (Mi, 25), (Do, 75), (Ti, 25), (Do, 0)],
        "All the Small Things",
        submitter="WEFFJEBSTER",
        submitter_credits="WEFFJEBSTER",
        hint_1=" My favorite song?[await][page]\n It's All the Small Things.\n ♪“Mi Do Ti Do Mi Do Ti Do”.\n Toadofsky says it's not real punk![await]",
        hint_2=" My favorite song?[await][page]\n It's All the Small Things.\n ♪“Mi Do Ti Do Mi Do Ti Do”.\n Blink and you'll miss it![await]",
        hint_3=" Say it ain't so![delay]\n I will not go![delay]\n Turn the lights off![delay]\n Carry me home![await]",
        scroll='\n[center]Mi Do Ti Do Mi Do Ti Do[await]'),
    Song(
        [(La, 20), (Mi, 20), (La, 20), (Do, 100), (Fa, 20), (Mi, 20), (Fa, 20), (Do, 0)],
        "One",
        submitter="WEFFJEBSTER",
        submitter_credits="WEFFJEBSTER",
        hint_1=" My favorite song?[await][page]\n It's One.\n ♪“La Mi La Do Fa Mi Fa Do”.\n It's from before Toadofsky\n cut his hair![await]",
        hint_2=" My favorite song?[await][page]\n It's One.[await]\n You can't really hear the bass\n tadpoles, though...[await]",
        hint_3=" The Moleville Blues?\n La Mi La Do... [await]\n Fa Mi Fa Do... [await][page]\n Sure, it's a bit of a bummer, but wait'll ya get to the fast part![await]",
        scroll='\n[center]La Mi La Do Fa Mi Fa Do[await]'),
    Song(
        [(Do, 20), (Ti, 20), (La, 20), (So, 20), (La, 20)],
        "All I Want",
        submitter="WEFFJEBSTER",
        submitter_credits="WEFFJEBSTER",
        hint_1=" My favorite song?[await][page]\n It's All I Want!\n ♪“Do Ti La So La.”\n It gives Toadofsky road rage![await]",
        hint_2=" My favorite song?[await][page]\n It's All I Want!\n ♪“Do Ti La So La.”\n Yeah yeah yeah yeah yeah![await]",
        hint_3=" We been thinkin' of takin' that ol' minecart outta the mines and runnin' a taxi service![await]",
        scroll='\n[center]Do Ti La So La[await]'),
    Song(
        [(La, 25), (Ti, 25), (Do, 25), (Mi, 25), (Do, 100), (Ti, 25), (La, 25), (Ti, 0)],
        "Terra's Theme",
        submitter="WEFFJEBSTER",
        submitter_credits="WEFFJEBSTER",
        hint_1=" My favorite song?[await][page]\n It's Terra's Theme!\n ♪“La Ti Do Mi Do Ti La Ti”.[await]\n Toadofsky's no Nobuo![await]",
        hint_2=" My favorite song?[await][page]\n It's Terra's Theme!\n ♪“La Ti Do Mi Do Ti La Ti”.[await]\n Is Mallow half Esper?[await]",
        hint_3=" Back before there was a star piece here...[await][page]\n We were hidin' some big ol' frozen bird thing in these mines![await]",
        scroll='\n[center]La Ti Do Mi Do Ti La Ti[await]'),
    Song(
        [(La, 28), (Ti, 28), (Do, 28), (Mi, 28), (Re, 14), (Mi, 14), (Re, 14), (Ti, 0)],
        "Creative Exercise",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=" I've gotten really into Mario Paint\n lately. Is that weird?\n I don't have arms.[await]",
        hint_2=" My favorite song?[await][page]\n It's “Creative Exercise.”\n ♪“La Ti Do Mi Re Mi Re Ti”.[await][page]\n It makes me want to paint\n something, but I don't have arms.[await]",
        hint_3=" When I'm done workin' for the day,\n I'm goin' home and playin' Mario\n Paint.[await][page]\n ♪“La Ti Do Mi Re Mi Re Ti”...[await]",
        scroll='\n[center]La Ti Do Mi Re Mi Re Ti[await]'),
    Song(
        [(Re, 10), (Re, 20), (Re, 20), (Do, 10), (Re, 20), (Mi, 40), (So, 0)],
        "SMB Overworld",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=" My favourite song?[await][page]\n It's the SMB Overworld theme,\n ♪“Re Re Re Do Re Mi So”.\n Makes me want to jump up high![await]",
        hint_2=" My favourite song?[await][page]\n It's the SMB Overworld theme.\n ♪“Re Re Re Do Re Mi So”.\n It's a classic![await]",
        hint_3="I tell ya, I just wanna get done for\n the day, go home, and play\n Nintendo.\n ♪“Re Re Re Do Re Mi So...”[await]",
        scroll='\n[center]Re Re Re Do Re Mi So[await]'),
    Song(
        [(Ti, 30), (Fa, 42), (Ti, 15), (Ti, 10), (Ti, 7), (Do, 7), (Re, 7), (Mi, 0)],
        "Zelda Overworld Theme",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=" My favourite song?[await][page]\n It's the Zelda Overworld Theme.\n ♪“Ti Fa Ti Ti Ti Do Re Mi”.\n It's adventurous![await]",
        hint_2=" My favourite song?[await][page]\n It's the Zelda Overworld Theme.\n ♪“Ti Fa Ti Ti Ti Do Re Mi”.\n I wanna be a hero when I grow up![await]",
        hint_3=" I like to pretend I'm that Link fella, discovering a new cave or somethin'.[await][page]\n It makes the day go by a lil' faster.[await][page]\n ♪“Ti Fa Ti Ti Ti Do Re Mi...”[await]",
        scroll='\n[center]Ti Fa Ti Ti Ti Do Re Mi[await]'),
    Song(
        [(Ti, 30), (Fa, 30), (Ti, 30), (Mi, 30), (Re, 0)],
        "Hyrule Field",
        submitter="pidgezero_one",
        submitter_credits="PIDGEZERO_ONE",
        hint_1=" My favourite song?[await][page]\n It's the Hyrule Field theme.\n ♪“Ti Fa Ti Mi Re...”\n ♪“Ti Fa Ti Mi Re...”[await]",
        hint_2=" My favourite song?[await][page]\n It's the Hyrule Field theme.\n ♪“Ti Fa Ti Mi Re...”\n ♪“Ti Fa Ti Mi Re...”[await]",
        hint_3="It's good, honest work, but\n sometimes I wish I got a bit more\n sunshine.[await][page]\n Somewhere like a big, open field,\n y'know what I mean?[await][page]\n ♪“Ti Fa Ti Mi Re...”\n ♪“Ti Fa Ti Mi Re...”[await]",
        scroll='\n[center]Ti Fa Ti Mi Re[await]'),
    Song(
        [(So, 15), (So, 15), (So, 30), (Mi, 45), (Re, 15), (Re, 45), (Do, 15), (Re, 0)],
        "Believe",
        submitter="katstasaph",
        submitter_credits="KATSTASAPH",
        hint_1="' Check out my new vocoder!\n♪“So So So Mi Re Re Do Re”[await]\nWhat do you mean,\nhow can a tadpole\nuse a vocoder?'[await]",
        hint_2="' After some practice, I am now\nthe best tadpole to ever\nuse a vocoder.[await]\n♪“So So So Mi Re Re Do Re”[delay]\nOh barnacles,\nit fell in the pond.'[await]",
        hint_3="'Of course we're gonna dig out\nthe rest of the mines.\nWe just need a karaoke break first.[await]\n♪Do you believe in life after love?'[await]",
        scroll='\n[center]So So So Mi Re Re Do Re[await]'),
    Song(
        [(Mi, 22), (Do, 64), (Ti, 22), (Do, 64), (Mi, 22), (Do, 64), (Ti, 22), (Do, 0)],
        "All the Small Things",
        submitter="katstasaph",
        submitter_credits="KATSTASAPH",
        hint_1="' My favorite song? (blink) You\n know,\nit's the one that goes,\nNa-na, na-na, na-na, na-na, na, na\nna-na, na-na, na-na, na-na, na,\n na.[delay]\nYeah, I don't know how you're\nsupposed to do that either.[await]\nThere aren't enough tadpoles\nfor the chorus.[await]'[await]",
        hint_2="' Hey, Mario or whoever!\nI'm writing a pop-punk song![await]\n♪“Mi Do Ti Do Mi Do Ti Do\nMi Do Ti Do Mi Do Ti Do”[await]\nMaybe I should change\nup the melody.[await]'[await]",
        hint_3="' Go mine,\ncome home.[await]\nYou're stuck?\nOh, no![await]'[await]",
        scroll='\n[center]Mi Do Ti Do Mi Do Ti Do[await]'),
    Song(
        [(Ti, 30), (Re, 25), (Re, 5), (Ti, 15), (So, 45), (So, 60), (La, 15), (Ti, 0)],
        "Flower Garden",
        submitter="katstasaph",
        submitter_credits="KATSTASAPH",
        hint_1="' My favorite song?[await][page]\n It's from, uh, Yo'ster Isle.\n ♪“Ti Re Re Ti So So La Ti”.[await]\nThe next part's too high for me.[await]'[await]",
        hint_2="' I love Flower Garden![await]\nBut I can never hear it\nover baby Mario's crying.[delay]\nOh! You're...[delay]\nI'm gonna go swim some laps.[await]\n...underwater.[await]'[await]",
        hint_3="' All together now, y'all!\n ♪“Ti Re Re Ti So So La Ti”[await]\nWish I was sittin'\nin a flower garden.[await]'[await]",
        scroll='\n[center]Ti Re Re Ti So So La Ti[await]'),
    Song(
        [(Do, 55), (Do, 65), (Ti, 15), (Do, 15), (Re, 15), (Do, 15), (La, 15), (Do, 0)],
        "Memory",
        submitter="katstasaph",
        submitter_credits="KATSTASAPH",
        hint_1=" ' My favorite song?[await][page]\n It's “Memory” from “Cats”.\n ♪“Do Do Ti Do Re Do La Do”.[await]\n I wish cats were real.[await]'[await]",
        hint_2=" ' My favorite song?[await][page]\n It's “Memory” from “Cats”.\n ♪“Do Do Ti Do Re Do La Do”.[await]\n But not even Frogfucius has\\seen a\n real cat before.[await]'[await]",
        hint_3=" 'Cats? No memory of 'em.\n I reckon there ain't one\n cat in this entire world.[delay]\n Belome?\n Why, he's a dog!'[await]",
        scroll='\n[center]Do Do Ti Do Re Do La Do[await]'),
]
