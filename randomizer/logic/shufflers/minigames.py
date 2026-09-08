"""Minigame randomization logic."""
from __future__ import annotations
from randomizer.utils.debug_output import debug_print
from copy import deepcopy
import random
from typing import TYPE_CHECKING, Optional, cast

from smrpgpatchbuilder.datatypes.overworld_scripts.event_scripts.commands import (
    RunDialog,
    Return,
    JmpIfVarNotEqualsConst,
    Inc,
    ActionQueueAsync,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import NPC_0
from ...data.variables.variable_names import (
    SECONDARY_TEMP_7024,
    TEMP_7026,
    TEMP_7028,
    TEMP_702A,
    TEMP_702C,
    TEMP_702E,
    TEMP_70AC,
)
from smrpgpatchbuilder.datatypes.overworld_scripts.arguments.area_objects import NPC_14
from smrpgpatchbuilder.datatypes.minecart import (
    EAST, MAP_H, MAP_W, NORTH, SOUTH, WEST, MinecartTrack, TrackColor,
    TrackType, build_minecart_patch, track_type_for,
)
from smrpgpatchbuilder.datatypes.minecart.constants import BLOCK_BASE, WINDOW_SIZE
from ...data.minigames.moleville_track import Maze
from ...data.minigames.melody_bay import all_songs
from ...data.variables.event_script_names import (E1082_MELODY_BAY_SONG_1_INPUT, E1079_MELODY_BAY_SONG_1_VALIDATOR, E1083_MELODY_BAY_SONG_2_INPUT, E1080_MELODY_BAY_SONG_2_VALIDATOR, E1084_MELODY_BAY_SONG_3_INPUT, E1081_MELODY_BAY_SONG_3_VALIDATOR, E3132_MOLEVILLE_MINERS_SONG, E1088_MELODY_BAY_THIRD_SONG_HINT)
from ...data.variables.dialog_names import (
        DI2718_SONG_1_SCROLL_HINT,
        DI2664_TADPOLE_SONG_1_HINT,
        DI2665_TADPOLE_SONG_2_HINT,
        DI1615_MOLEVILLE_BLUES_8,
    )
from ...data.minigames.ship_password import (
        pool as password_pool,
        suggest_letter_bank,
        box_dialog_ids,
        recitation_ids,
        hint_authors,
    )
from ...data.variables.event_script_names import E3411_SHIP_PASSWORD_CORRECTNESS_CHECK
from ...data.variables.dialog_names import (
        DI1664_TROOPA_PUZZLE_HINT,
        DI1665_TRAMPOLINE_PUZZLE_HINT,
        DI1666_MAZE_PUZZLE_HINT,
        DI1667_SNAKE_PUZZLE_HINT,
        DI1668_CANNONBALL_PUZZLE_HINT,
        DI1669_BARREL_PUZZLE_HINT,
        DI1673_SHIP_ENTRANCE_NOTE,
        DI1674_SHIP_SAVEROOM_NOTE,
        DI1675_SHIP_GREAPER_1_NOTE,
        DI1676_SHIP_GREAPER_2_NOTE,
        DI1656_SLEEPING_DRY_BONES,
    )

if TYPE_CHECKING:
    from ...types.gameworld import GameWorld


def randomize_tadpole_pond(world: GameWorld) -> None:
    """Randomize the Melody Bay song minigame."""

    selection = random.sample(all_songs, 3)
    world.event_scripts.get_script_by_id(E1082_MELODY_BAY_SONG_1_INPUT).set_contents(
        selection[0].generate_input_script(0)
    )
    world.event_scripts.get_script_by_id(
        E1079_MELODY_BAY_SONG_1_VALIDATOR
    ).set_contents(selection[0].generate_playback_script(0))
    world.update_dialog(
        DI2718_SONG_1_SCROLL_HINT, selection[0].scroll_text
    )
    world.update_dialog(
        DI2664_TADPOLE_SONG_1_HINT, selection[0].apprentice_hint_1
    )

    world.event_scripts.get_script_by_id(E1083_MELODY_BAY_SONG_2_INPUT).set_contents(
        selection[1].generate_input_script(1)
    )
    world.event_scripts.get_script_by_id(
        E1080_MELODY_BAY_SONG_2_VALIDATOR
    ).set_contents(selection[1].generate_playback_script(1))
    world.update_dialog(
        DI2665_TADPOLE_SONG_2_HINT, selection[1].apprentice_hint_2
    )
    world.update_dialog(
        DI1615_MOLEVILLE_BLUES_8, selection[1].mole_hint
    )
    world.event_scripts.get_script_by_id(E3132_MOLEVILLE_MINERS_SONG).set_contents(
        [
            RunDialog(
                DI1615_MOLEVILLE_BLUES_8,
                NPC_0,
                closable=True,
                sync=False,
                multiline=True,
                use_background=True,
            ),
            Return(),
        ]
    )
    world.event_scripts.get_script_by_id(E3132_MOLEVILLE_MINERS_SONG).set_contents(
        [
            RunDialog(dialog_id=DI1615_MOLEVILLE_BLUES_8, above_object=NPC_14, closable=True, sync=False, multiline=True, use_background=False),
	        Return()
        ]
    )

    world.event_scripts.get_script_by_id(E1084_MELODY_BAY_SONG_3_INPUT).set_contents(
        selection[2].generate_input_script(2)
    )
    world.event_scripts.get_script_by_id(
        E1081_MELODY_BAY_SONG_3_VALIDATOR
    ).set_contents(selection[2].generate_playback_script(2))
    cast(
        ActionQueueAsync,
        world.event_scripts.get_command_by_identifier("starfish_dance_hint"),
    ).set_subscript(
        selection[2].generate_starfish_hint(
            cast(
                ActionQueueAsync,
                world.event_scripts.get_command_by_identifier("starfish_dance_hint"),
            ).subscript.contents
        )
    )
    world.event_scripts.get_script_by_id(
        E1088_MELODY_BAY_THIRD_SONG_HINT
    ).set_contents(selection[2].generate_tadpole_hint())

    world.song_1 = selection[0].scroll_text
    world.song_2 = selection[1].scroll_text
    world.song_3 = selection[2].scroll_text

    world.song_authors = list(
        dict.fromkeys(
            [selection[0].submitter_credits,
            selection[1].submitter_credits,
            selection[2].submitter_credits]
        )
    )


def randomize_password(world: GameWorld) -> None:
    """Randomize the ship password minigame."""

    password = random.choice(password_pool)
    world.password = password.word
    decoy_word = random.choice([p for p in password_pool if p != password])
    password = deepcopy(password)
    correct_positions = []

    # create password submission logic
    for index, letter in enumerate(list(password.word)):
        letters = suggest_letter_bank(password.word, index, decoy_word.word)
        correct_position = letters.index(password.word[index])
        correct_positions.append(correct_position)

        # generate the dialogs that display your letter selection when you stand under the boxes
        box_dialogs = []
        box_dialogs.append(
            """[page]\n Key letter%i  <%s> %s  %s  %s  %s[end]"""
            % (
                index + 1,
                letters[0],
                letters[1],
                letters[2],
                letters[3],
                letters[4],
            )
        )
        box_dialogs.append(
            """[page]\n Key letter%i   %s <%s> %s  %s  %s[end]"""
            % (
                index + 1,
                letters[0],
                letters[1],
                letters[2],
                letters[3],
                letters[4],
            )
        )
        box_dialogs.append(
            """[page]\n Key letter%i   %s  %s <%s> %s  %s[end]"""
            % (
                index + 1,
                letters[0],
                letters[1],
                letters[2],
                letters[3],
                letters[4],
            )
        )
        box_dialogs.append(
            """[page]\n Key letter%i   %s  %s  %s <%s> %s[end]"""
            % (
                index + 1,
                letters[0],
                letters[1],
                letters[2],
                letters[3],
                letters[4],
            )
        )
        box_dialogs.append(
            """[page]\n Key letter%i   %s  %s  %s  %s <%s>[end]"""
            % (
                index + 1,
                letters[0],
                letters[1],
                letters[2],
                letters[3],
                letters[4],
            )
        )
        box_dialog_pairs = zip(box_dialogs, box_dialog_ids[index])
        for dialog_content, dialog_id in box_dialog_pairs:
            world.update_dialog(dialog_id, dialog_content)
        recitation_pairs = zip(letters, recitation_ids[index])
        for letter, dialog_id in recitation_pairs:
            world.update_dialog(dialog_id, """%s[end]""" % letter)

    # calibrate correctness checker
    world.event_scripts.get_script_by_id(
        E3411_SHIP_PASSWORD_CORRECTNESS_CHECK
    ).set_contents(
        [
            JmpIfVarNotEqualsConst(
                SECONDARY_TEMP_7024, correct_positions[0], ["ship_password_check_2"]
            ),
            Inc(TEMP_70AC),
            JmpIfVarNotEqualsConst(
                TEMP_7026,
                correct_positions[1],
                ["ship_password_check_3"],
                identifier="ship_password_check_2",
            ),
            Inc(TEMP_70AC),
            JmpIfVarNotEqualsConst(
                TEMP_7028,
                correct_positions[2],
                ["ship_password_check_4"],
                identifier="ship_password_check_3",
            ),
            Inc(TEMP_70AC),
            JmpIfVarNotEqualsConst(
                TEMP_702A,
                correct_positions[3],
                ["ship_password_check_5"],
                identifier="ship_password_check_4",
            ),
            Inc(TEMP_70AC),
            JmpIfVarNotEqualsConst(
                TEMP_702C,
                correct_positions[4],
                ["ship_password_check_6"],
                identifier="ship_password_check_5",
            ),
            Inc(TEMP_70AC),
            JmpIfVarNotEqualsConst(
                TEMP_702E,
                correct_positions[5],
                ["ship_password_check_end"],
                identifier="ship_password_check_6",
            ),
            Inc(TEMP_70AC),
            Return(identifier="ship_password_check_end"),
        ]
    )

    # populate hint dialogs
    hint_authors_copy = list(hint_authors)
    random.shuffle(hint_authors_copy)
    # guarantee that the hint submitter will get their name on one of the hints
    writers = [password.submitter_hint_prefix] + hint_authors_copy
    RWRITER = "%RANDOM_WRITER%"
    number_of_writers = len(
        [
            h
            for h in [
                password.troopa_hint,
                password.trampoline_hint,
                password.maze_hint,
                password.snake_hint,
                password.cannonball_hint,
                password.barrel_hint,
                password.entrance_hint,
                password.saveroom_hint,
                password.greaper_hint_2,
                password.greaper_hint,
                password.drybones_hint,
            ]
            if h is not None and RWRITER in h
        ]
    )
    writers = writers[:number_of_writers]
    random.shuffle(writers)
    for s in writers:
        if RWRITER in password.troopa_hint:
            password.troopa_hint = password.troopa_hint.replace(RWRITER, s)
            continue
        if RWRITER in password.trampoline_hint:
            password.trampoline_hint = password.trampoline_hint.replace(RWRITER, s)
            continue
        if RWRITER in password.maze_hint:
            password.maze_hint = password.maze_hint.replace(RWRITER, s)
            continue
        if RWRITER in password.snake_hint:
            password.snake_hint = password.snake_hint.replace(RWRITER, s)
            continue
        if RWRITER in password.cannonball_hint:
            password.cannonball_hint = password.cannonball_hint.replace(RWRITER, s)
            continue
        if RWRITER in password.barrel_hint:
            password.barrel_hint = password.barrel_hint.replace(RWRITER, s)
            continue
        if password.entrance_hint and RWRITER in password.entrance_hint:
            password.entrance_hint = password.entrance_hint.replace(RWRITER, s)
            continue
        if password.saveroom_hint and RWRITER in password.saveroom_hint:
            password.saveroom_hint = password.saveroom_hint.replace(RWRITER, s)
            continue
        if password.greaper_hint and RWRITER in password.greaper_hint:
            password.greaper_hint = password.greaper_hint.replace(RWRITER, s)
            continue
        if password.greaper_hint_2 and RWRITER in password.greaper_hint_2:
            password.greaper_hint_2 = password.greaper_hint_2.replace(RWRITER, s)
            continue
        if password.drybones_hint and RWRITER in password.drybones_hint:
            password.drybones_hint = password.drybones_hint.replace(RWRITER, s)
            continue
    world.update_dialog(
        DI1664_TROOPA_PUZZLE_HINT, password.troopa_hint
    )
    world.update_dialog(
        DI1665_TRAMPOLINE_PUZZLE_HINT, password.trampoline_hint
    )
    world.update_dialog(
        DI1666_MAZE_PUZZLE_HINT, password.maze_hint
    )
    world.update_dialog(
        DI1667_SNAKE_PUZZLE_HINT, password.snake_hint
    )
    world.update_dialog(
        DI1668_CANNONBALL_PUZZLE_HINT, password.cannonball_hint
    )
    world.update_dialog(
        DI1669_BARREL_PUZZLE_HINT, password.barrel_hint
    )
    if password.entrance_hint is not None:
        world.update_dialog(
            DI1673_SHIP_ENTRANCE_NOTE, password.entrance_hint
        )
    if password.saveroom_hint is not None:
        world.update_dialog(
            DI1674_SHIP_SAVEROOM_NOTE, password.saveroom_hint
        )
    if password.greaper_hint is not None:
        world.update_dialog(
            DI1675_SHIP_GREAPER_1_NOTE, password.greaper_hint
        )
    if password.greaper_hint_2 is not None:
        world.update_dialog(
            DI1676_SHIP_GREAPER_2_NOTE, password.greaper_hint_2
        )
    if password.drybones_hint is not None:
        world.update_dialog(
            DI1656_SLEEPING_DRY_BONES, password.drybones_hint
        )

    world.password_author = password.submitter_credits


_MC_DIR = {">": EAST, "<": WEST, "v": NORTH, "^": SOUTH}
_MC_STEP = {NORTH: (0, -1), SOUTH: (0, 1), EAST: (1, 0), WEST: (-1, 0)}
_MC_REV = {NORTH: SOUTH, SOUTH: NORTH, EAST: WEST, WEST: EAST}
_MC_CORNERS = (TrackType.CORNER_SE, TrackType.CORNER_SW,
               TrackType.CORNER_NE, TrackType.CORNER_NW)
_MC_RED_LATE_CHANCE = 0.05    # sometimes redden the later corner instead of the earlier
_MC_STUB_LEN = 3              # straight tiles at the start before any turn/fork may appear
_MC_RUNOUT_LEAD = 1          # straight tile(s) between the last turn and the BLUE end
_MC_RUNOUT_AFTER_BLUE = 48   # straight tiles the camera scrolls into past the BLUE end
_MC_RUNOUT_LEN = _MC_RUNOUT_LEAD + 1 + _MC_RUNOUT_AFTER_BLUE
_MC_MAX_ATTEMPTS = 50        # re-rolls


def _mc_screen(x, y):
    """Maze cell (x=row, y=col) -> Mode7 (col, row). Rows are flipped and
    the bottom _MC_STUB_LEN rows are reserved for the fixed straight start
    stub, so the maze origin lands just above the stub at the bottom-left."""
    return (y, MAP_H - 1 - _MC_STUB_LEN - x)


def _mc_runout_dirs(in_dir):
    """Run-out directions to try from a cell entered going in_dir - straight
    ahead first, then the two perpendicular turns (never a 180° reversal)."""
    perpendicular = [d for d in (NORTH, SOUTH, EAST, WEST)
                     if d not in (in_dir, _MC_REV[in_dir])]
    return [in_dir, *perpendicular]


def _mc_line_clear(col, row, direction, length, occupied):
    """True if length cells straight in direction from (col, row) are
    all in-bounds and not in occupied."""
    delta_col, delta_row = _MC_STEP[direction]
    for step in range(1, length + 1):
        cell = (col + delta_col * step, row + delta_row * step)
        if not (0 <= cell[0] < MAP_W and 0 <= cell[1] < MAP_H) or cell in occupied:
            return False
    return True


def _build_minecart_track(path) -> Optional[MinecartTrack]:
    """Convert a solved maze path into a MinecartTrack: a fixed
    _MC_STUB_LEN-tile straight start stub, the maze interior, and a straight
    run-out (a lead tile, the BLUE stage-end marker, then
    _MC_RUNOUT_AFTER_BLUE straight tiles) attached in clear space near the
    end. Returns None on a 180° reversal the rails can't express, or if no
    run-out fits."""
    cells = [(*_mc_screen(x, y), _MC_DIR[d]) for (x, y, d) in path]  # (col, row, out_dir)
    stub = [(0, MAP_H - 1 - k) for k in range(_MC_STUB_LEN)]         # start straight tiles

    # Truncate at the latest cell from which the run-out fits in clear space,
    # preferring to continue straight, else turning a corner into it.
    chosen = None
    for last in range(len(cells) - 1, -1, -1):
        in_dir = cells[last - 1][2] if last else NORTH          # cell 0 enters from the stub
        occupied = {(cells[i][0], cells[i][1]) for i in range(last + 1)}
        occupied.update(stub)
        col, row = cells[last][0], cells[last][1]
        for direction in _mc_runout_dirs(in_dir):
            if _mc_line_clear(col, row, direction, _MC_RUNOUT_LEN, occupied):
                chosen = (last, direction)
                break
        if chosen is not None:
            break
    if chosen is None:
        return None
    last, runout_dir = chosen

    placed = []                                                 # (col, row, type, is_corner)
    for index in range(last + 1):
        col, row, out_dir = cells[index]
        in_dir = cells[index - 1][2] if index else NORTH
        if index == last:
            out_dir = runout_dir                                # leave the last cell into the run-out
        try:
            track_type = track_type_for(in_dir, out_dir)
        except ValueError:
            return None
        placed.append((col, row, track_type, track_type in _MC_CORNERS))

    colors = [TrackColor.GREEN] * len(placed)
    for index, (_, _, _, is_corner) in enumerate(placed):
        if not is_corner:
            continue
        for ahead in range(index + 1, min(index + 3, len(placed))):
            if placed[ahead][3]:
                late = random.random() < _MC_RED_LATE_CHANCE
                colors[ahead if late else index] = TrackColor.RED
                break

    track = MinecartTrack()
    for col, row in stub:
        track.set_track(col, row, TrackType.STRAIGHT_NS, TrackColor.GREEN)
    for (col, row, track_type, _), color in zip(placed, colors):
        track.set_track(col, row, track_type, color)

    # Run-out: lead straight tile(s), the BLUE stage-end marker, then the
    # straight tiles the Mode7 camera scrolls into as the stage changes.
    col, row = cells[last][0], cells[last][1]
    delta_col, delta_row = _MC_STEP[runout_dir]
    straight = (TrackType.STRAIGHT_NS if runout_dir in (NORTH, SOUTH)
                else TrackType.STRAIGHT_EW)
    for step in range(1, _MC_RUNOUT_LEN + 1):
        color = TrackColor.BLUE if step == _MC_RUNOUT_LEAD + 1 else TrackColor.GREEN
        track.set_track(col + delta_col * step, row + delta_row * step, straight, color)
    return track


def _generate_minecart_track() -> Optional[MinecartTrack]:
    """One course: re-roll until a maze solves and yields a legal track. The
    reduced grid (bottom rows reserved for the start stub) fails to solve()
    fairly often, hence the retries."""
    for _ in range(_MC_MAX_ATTEMPTS):
        maze = Maze(MAP_H - _MC_STUB_LEN, MAP_W)
        path = maze.solve()
        if path is None:
            continue
        track = _build_minecart_track(path)
        if track is not None:
            return track
    return None


def get_minecart_track_patch(world: GameWorld) -> dict[int, bytes]:
    """Generate both Mode7 courses and return the minecart ROM patch.

    Deterministic per seed (an independent RNG stream derived from
    world.seed so it never perturbs the rest of randomization). Returns an
    empty patch - leaving the vanilla courses intact - if no track compresses
    within the minigame's fixed data window after several re-rolls.
    """
    saved_state = random.getstate()
    try:
        random.seed("moleville_minecart:%s" % world.seed)
        for attempt in range(1, _MC_MAX_ATTEMPTS + 1):
            track_a = _generate_minecart_track()
            track_b = _generate_minecart_track()
            if track_a is None or track_b is None:
                continue
            try:
                patch = build_minecart_patch(track_a, track_b, 0, MAP_H - 1)
            except ValueError:
                continue  # too dense to compress in budget; re-roll both
            block = len(patch[BLOCK_BASE])
            debug_print(
                "[moleville_track] seed %s: SUCCESS - generated 2 Mode7 "
                "courses, minigame window %d/%d bytes (%d free) on attempt "
                "%d/%d" % (world.seed, block, WINDOW_SIZE, WINDOW_SIZE - block,
                           attempt, _MC_MAX_ATTEMPTS)
            )
            return patch
        debug_print(
            "[moleville_track] seed %s: FELL BACK to vanilla minecart - no "
            "in-budget track after %d attempts" % (world.seed, _MC_MAX_ATTEMPTS)
        )
        return {}
    finally:
        random.setstate(saved_state)
