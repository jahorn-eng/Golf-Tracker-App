from dataclasses import dataclass
from drafter import *


@dataclass
class Round:
    """A single round of golf played by the user.

    Fields:
        course_name: name of the course played
        score: total strokes for the round
        fairways_hit: number of fairways hit in regulation
        greens_hit: number of greens hit in regulation
        putts: total putts taken
        longest_drive: longest drive in yards
        longest_putt: longest made putt in feet
    """
    course_name: str
    score: int
    fairways_hit: int
    greens_hit: int
    putts: int
    longest_drive: int
    longest_putt: int


@dataclass
class State:
    """The website's saved data, shared by every route.

    Fields:
        golfer_name: the golfer's name
        rounds: every Round the golfer has logged
        status: a message shown on the home page
        handicap: average strokes over par across all rounds
        favorite_course: the course the golfer plays or likes most
    """
    golfer_name: str
    rounds: list[Round]
    status: str
    handicap: float
    favorite_course: str


# Global CONSTANT (allowed): the course par used for handicap math
COURSE_PAR = 72


def calculate_handicap(rounds: list[Round]) -> float:
    """Calculate a simple handicap from the logged rounds.

    Purpose: measure how far over par the golfer scores on average.

    Args:
        rounds: the list of Round objects to average over.

    Returns:
        The average of (score - COURSE_PAR), rounded to 1 decimal.
        Returns 0.0 if the list is empty.
    """
    if len(rounds) == 0:
        return 0.0
    total_over = 0
    for r in rounds:                      # loop over an attribute of the Round list
        total_over += r.score - COURSE_PAR
    return round(total_over / len(rounds), 1)


def find_favorite(rounds: list[Round]) -> str:
    """Find the course the golfer has played the most.

    Purpose: pick the favorite course automatically from the round history.

    Args:
        rounds: the list of Round objects to count.

    Returns:
        The course_name with the most rounds, or "" if there are no rounds.
    """
    counts = {}
    for r in rounds:
        # dict.get(key, 0) returns 0 if the key is not in the dictionary yet
        counts[r.course_name] = counts.get(r.course_name, 0) + 1
    best = ""
    best_count = 0
    for course, count in counts.items():
        if count > best_count:
            best = course
            best_count = count
    return best


# ---------- Route 1: home ----------
@route
def index(state: State) -> Page:
    """Show the home page with a greeting, the status message and navigation buttons.

    Purpose: main menu that links to every other page.

    Args:
        state: the current State (read only here).

    Returns:
        A Page for the home screen.
    """
    if state.golfer_name == "":
        welcome = "Welcome! Set up your golfer profile to begin."
    else:
        welcome = "Welcome back, " + state.golfer_name + "!"
    return Page(state, [
        Header("Golf Tracker"),
        welcome,
        "Status: " + state.status,
        Button("Set Up Profile", profile),
        Button("Add a Round", add_round_page),
        Button("View Rounds", rounds_page),
        Button("Statistics", stats_page),
    ])


# ---------- Route 2: profile form ----------
@route
def profile(state: State) -> Page:
    """Show a form where the golfer enters their name.

    Purpose: collect the golfer's name with a TextBox.

    Args:
        state: the current State; golfer_name pre-fills the TextBox.

    Returns:
        A Page containing the profile form.
    """
    return Page(state, [
        Header("Golfer Profile"),
        "Your name:",
        TextBox("name", state.golfer_name),
        Button("Save", save_profile),
        Button("Back", index),
    ])


# ---------- Route 3: save profile ----------
@route
def save_profile(state: State, name: str) -> Page:
    """Save the golfer's name after checking it is not blank.

    Purpose: update the profile.
    Modifies: state.golfer_name and state.status.

    Args:
        state: the current State.
        name: text typed into the "name" TextBox.

    Returns:
        The home Page showing the result in the status line.
    """
    if name.strip() == "":
        state.status = "Please enter a name."
        return index(state)
    state.golfer_name = name.strip()
    state.status = "Profile saved."
    return index(state)


# ---------- Route 4: add-round form ----------
@route
def add_round_page(state: State) -> Page:
    """Show the form for entering a new round.

    Purpose: collect every Round field with TextBoxes plus a CheckBox.

    Args:
        state: the current State (not changed here).

    Returns:
        A Page containing the add-round form.
    """
    return Page(state, [
        Header("Add a Round"),
        "Course name:", TextBox("course", ""),
        "Score:", TextBox("score", "90"),
        "Fairways hit:", TextBox("fairways", "7"),
        "Greens hit:", TextBox("greens", "9"),
        "Putts:", TextBox("putts", "32"),
        "Longest drive (yards):", TextBox("drive", "250"),
        "Longest putt (feet):", TextBox("putt", "15"),
        CheckBox("fav", False),
        "Mark this course as my favorite",
        Button("Save Round", save_round),
        Button("Back", index),
    ])


# ---------- Route 5: save round ----------
@route
def save_round(state: State, course: str, score: str, fairways: str,
               greens: str, putts: str, drive: str, putt: str,
               fav: bool) -> Page:
    """Validate the form, create a Round and add it to the state.

    Purpose: record a new round and refresh the stats that depend on it.
    Modifies: state.rounds, state.handicap, state.favorite_course, state.status.

    Args:
        state: the current State.
        course: course name from the "course" TextBox.
        score: score text (converted to int after validation).
        fairways: fairways hit text.
        greens: greens hit text.
        putts: putts text.
        drive: longest drive text.
        putt: longest putt text.
        fav: True if the favorite CheckBox was ticked.

    Returns:
        The home Page with a success or error message in the status.
    """
    values = [score, fairways, greens, putts, drive, putt]
    for v in values:
        # str.isdigit() is True only if the text is all digits
        if not v.strip().isdigit():
            state.status = "All numeric fields must be whole numbers."
            return index(state)
    if course.strip() == "":
        state.status = "Course name is required."
        return index(state)

    new_round = Round(course.strip(), int(score), int(fairways), int(greens),
                      int(putts), int(drive), int(putt))
    state.rounds.append(new_round)
    state.handicap = calculate_handicap(state.rounds)
    if fav:
        state.favorite_course = course.strip()
    else:
        state.favorite_course = find_favorite(state.rounds)
    state.status = "Round saved at " + new_round.course_name + "."
    return index(state)


# ---------- Route 6: list rounds ----------
@route
def rounds_page(state: State) -> Page:
    """List every logged round and offer a way to delete one.

    Purpose: let the golfer review their history.

    Args:
        state: the current State; state.rounds is looped over.

    Returns:
        A Page listing the rounds, or a "No rounds yet." message.
    """
    content = [Header("Your Rounds")]
    if len(state.rounds) == 0:
        content.append("No rounds yet.")
    else:
        # enumerate() gives both the index (i) and the item (r) in each loop
        for i, r in enumerate(state.rounds):
            content.append(str(i + 1) + ". " + r.course_name + " - score " +
                           str(r.score) + ", putts " + str(r.putts))
        content.append(Header("Delete a round", 3))
        content.append("Round number:")
        content.append(TextBox("number", "1"))
        content.append(Button("Delete", delete_round))
    content.append(Button("Back", index))
    return Page(state, content)


# ---------- Route 7: delete round ----------
@route
def delete_round(state: State, number: str) -> Page:
    """Delete the round at the given list position.

    Purpose: remove a mistaken round and recompute dependent stats.
    Modifies: state.rounds, state.handicap, state.favorite_course, state.status.

    Args:
        state: the current State.
        number: the 1-based round number typed into the "number" TextBox.

    Returns:
        The home Page with a success or error message in the status.
    """
    # Chained comparison: 1 <= x <= n means x is between 1 and n inclusive
    if number.isdigit() and 1 <= int(number) <= len(state.rounds):
        removed = state.rounds.pop(int(number) - 1)
        state.handicap = calculate_handicap(state.rounds)
        state.favorite_course = find_favorite(state.rounds)
        state.status = "Deleted round at " + removed.course_name + "."
    else:
        state.status = "Invalid round number."
    return index(state)


# ---------- Route 8: statistics ----------
@route
def stats_page(state: State) -> Page:
    """Show summary statistics across all rounds.

    Purpose: display best score, average putts, longest drive, handicap
    and favorite course.

    Args:
        state: the current State; state.rounds is looped over.

    Returns:
        A Page of statistics, or a prompt to add a round if none exist.
    """
    if len(state.rounds) == 0:
        return Page(state, [Header("Statistics"), "Add a round first.",
                            Button("Back", index)])
    best = state.rounds[0].score
    total_putts = 0
    longest_drive = 0
    for r in state.rounds:
        if r.score < best:
            best = r.score
        total_putts += r.putts
        if r.longest_drive > longest_drive:
            longest_drive = r.longest_drive
    avg_putts = round(total_putts / len(state.rounds), 1)
    return Page(state, [
        Header("Statistics for " + state.golfer_name),
        "Rounds played: " + str(len(state.rounds)),
        "Handicap (vs par " + str(COURSE_PAR) + "): " + str(state.handicap),
        "Best score: " + str(best),
        "Average putts: " + str(avg_putts),
        "Longest drive: " + str(longest_drive) + " yards",
        "Favorite course: " + state.favorite_course,
        Button("Back", index),
    ])

set_website_title("Golf Tracker")
set_site_information(
author="Josh Horning",
description="Tracks a round of golf and stores the stats.",
sources="Thanks to the Drafter docs, Friends, and LLM's.",
planning=["plan.pdf", "design.pdf"],
links=["https://github.com/jahorn-eng/Golf-Tracker-App"]
)
hide_debug_information()
set_website_framed(False)


start_server(State("", [], "Ready.", 0.0, ""))

