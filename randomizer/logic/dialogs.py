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
            break
    else:
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
    for dialog_id, wish in sorted(zip(dialogs.wish_dialogs, random_wishes), key=lambda x: len(x[1])):
        base = allocate_string(len(wish), free_list)
        if base:
            world.wishes.wishes.append((dialog_id, base, wish))
        else:
            # TODO: Find other funny, in near bank strings...
            world.wishes.wishes.append((dialog_id, 0x24000E, None))

def randomize_quiz(world):
    questions = dialogs.generate_rando_questions(world) + dialogs.quiz_questions
    if len(questions) > len(dialogs.quiz_dialogs):
        random_questions = random.sample(questions, len(dialogs.quiz_dialogs))
    else:
        random_questions = questions
    random_questions += random.sample(dialogs.backfill_questions, len(dialogs.quiz_dialogs) - len(random_questions))

    # Existing Questions and Axem dialog
    free_list = {0x22e082: 3953, 0x22DBA5: 843}
    free_list = {0x22e082: 150, 0x22DBA5: 0}
    cruel_question_pointer = None
    for dialog_id, question in zip(dialogs.quiz_dialogs, random_questions):
        # Double check these
        if 1842 <= dialog_id < 1858:
           correct = 0
        elif 1858 <= dialog_id < 1874:
           correct = 1
        elif 1874 <= dialog_id <= 1881:
           correct = 2
        string = question.get_string(correct)
        base = allocate_string(len(string), free_list)
        if base:
            world.quiz.questions.append((dialog_id, base, string))
        # This is not an ideal way to solve this problem, but there needs to be
        # a mitigation if we run out of memory which is not crashing...
        elif cruel_question_pointer:
            world.quiz.questions.append((dialog_id, cruel_question_pointer, None))
        else:
            base = allocate_string(len(dialogs.cruel_question), free_list)
            if base:
                cruel_question_pointer = base
                string = dialogs.cruel_question
            # Okay, we're really out of memory here...
            # Pretty sure len(first question) >= len(cruel_question)
            else:
                _, cruel_question_pointer, __ = world.quiz.questions[0]
                world.quiz.questions[0] = _, cruel_question_pointer, string
                string = None
            world.quiz.questions.append((dialog_id, cruel_question_pointer, string))
