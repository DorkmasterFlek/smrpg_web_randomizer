import random

from randomizer.data import dialogs
from . import flags


# There's a way to do perfect allocations with DYNAMIC PROGRAMMING,
# but I'm not doing that.
def allocate_string(string_length, free_list):
    for base in sorted(free_list, key=lambda x: free_list[x]):
        if free_list[base] >= string_length:
            size = free_list[base]
            del free_list[base]
            free_list[base+string_length] = size - string_length
            return base

    # If we get this far, we couldn't find space for the string.
    return None


def randomize_all(world):
    # Check flag?
    randomize_wishes(world)
    if world.settings.is_flag_enabled(flags.QuizShuffle):
        randomize_quiz(world)


def randomize_wishes(world):
    random_wishes = random.sample(dialogs.wish_strings, len(dialogs.wish_dialogs))

    # These are the existing wishes.
    free_list = {0x240958: 415, 0x243e32: 80, 0x24344d: 32}
    for dialog_id, wish in zip(dialogs.wish_dialogs, random_wishes):
        base = allocate_string(len(wish), free_list)
        # Wish strings should be short enough that this doesn't happen, but give us a traceback if it does.
        if not base:
            raise ValueError("Unable to allocate space for wish: {!r}".format(wish))
        world.wishes.wishes.append((dialog_id, base, wish))


def randomize_quiz(world):
    questions = dialogs.generate_rando_questions(world) + dialogs.quiz_questions
    if len(questions) > len(dialogs.quiz_dialogs):
        random_questions = random.sample(questions, len(dialogs.quiz_dialogs))
    else:
        random_questions = questions
    random_questions += random.sample(dialogs.backfill_questions, len(dialogs.quiz_dialogs) - len(random_questions))
    random.shuffle(random_questions)

    free_list = {
        0x22E082: 3953,  # Existing Questions
        0x22DBA5: 843,  # Axem dialog
    }
    for dialog_id, question in zip(dialogs.quiz_dialogs, random_questions):
        # Randomize order of incorrect answers for some extra variety.
        random.shuffle(question.wrong_answers)

        # Double check these
        if 1842 <= dialog_id < 1858:
            correct = 0
        elif 1858 <= dialog_id < 1874:
            correct = 1
        else:
            correct = 2
        string = question.get_string(correct)
        base = allocate_string(len(string), free_list)
        # Questions should be short enough that this doesn't happen, but give us a traceback if it does.
        if not base:
            raise ValueError("Unable to allocate space for question: {!r}".format(string))
        world.quiz.questions.append((dialog_id, base, string))
