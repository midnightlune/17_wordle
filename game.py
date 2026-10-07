import random
from words import WORDS, SUPPORTED_LENGTHS
from feedback import evaluate, render

MAX_GUESSES = 6

WON, LOST, QUIT = "won", "lost", "quit"

class WordleGame:
    def __init__(self, length=5, target=None, input_fn=input, output_fn=print):
        if length not in SUPPORTED_LENGTHS:
            raise ValueError(f"length must be one of {SUPPORTED_LENGTHS}")
        self.length = length
        self.target = target or random.choice([w for w in WORDS if len(w) == length])
        self.history = []          # accepted guesses only: (guess, feedback)
        self.outcome = None
        self._in, self._out = input_fn, output_fn

    def _validate(self, guess):
        if not guess.isalpha():
            return "Letters only, please."
        if len(guess) != self.length:
            return f"Guess must be exactly {self.length} letters (got {len(guess)})."
        return None

    def _show_history(self):
        for n, (guess, fb) in enumerate(self.history, 1):
            self._out(f"  {n}/{MAX_GUESSES}  {render(guess, fb)}")

    def play(self):
        self._out(f"\nWordle — {self.length} letters, {MAX_GUESSES} guesses. ('q' to quit)")
        # Loop on accepted guesses, so invalid input never uses up a turn.
        while len(self.history) < MAX_GUESSES:
            try:
                guess = self._in("> ").strip().lower()
            except EOFError:
                guess = "q"
            if guess == "q":
                self.outcome = QUIT
                self._out(f"You quit. The word was: {self.target.upper()}")
                return self.outcome
            error = self._validate(guess)
            if error:
                self._out(error)
                continue

            self.history.append((guess, evaluate(self.target, guess)))
            self._show_history()

            if guess == self.target:      # checked before the loss, so a win on guess 6 counts
                self.outcome = WON
                self._out(f"Solved in {len(self.history)}/{MAX_GUESSES}!")
                return self.outcome

        self.outcome = LOST
        self._out(f"Out of guesses. The word was: {self.target.upper()}")
        return self.outcome


def ask_length(input_fn=input, output_fn=print):
    options = "/".join(map(str, SUPPORTED_LENGTHS))
    while True:
        try:
            choice = input_fn(f"Word length ({options}), or q to quit: ").strip().lower()
        except EOFError:
            return None
        if choice == "q":
            return None
        if choice.isdigit() and int(choice) in SUPPORTED_LENGTHS:
            return int(choice)
        output_fn(f"Please enter one of: {options}.")


def print_summary(games, output_fn=print):
    output_fn("\n=== Session summary ===")
    if not games:
        output_fn("No games played.")
        return
    won = [g for g in games if g.outcome == WON]
    lost = [g for g in games if g.outcome == LOST]
    quit_ = [g for g in games if g.outcome == QUIT]
    output_fn(f"Games: {len(games)}   Won: {len(won)}   Lost: {len(lost)}   Quit: {len(quit_)}")
    if won:
        avg = sum(len(g.history) for g in won) / len(won)
        output_fn(f"Average guesses in won games: {avg:.1f}")
    for i, g in enumerate(games, 1):
        guesses = ", ".join(w.upper() for w, _ in g.history) or "(no guesses)"
        output_fn(f"  Game {i} [{g.length} letters] {g.outcome.upper():<4} "
                  f"word={g.target.upper()}  guesses: {guesses}")


def run_session(input_fn=input, output_fn=print):
    games = []
    while True:
        length = ask_length(input_fn, output_fn)
        if length is None:
            break
        game = WordleGame(length, input_fn=input_fn, output_fn=output_fn)
        game.play()
        games.append(game)
        if game.outcome == QUIT:
            break
        try:
            again = input_fn("Play again? (y/n): ").strip().lower()
        except EOFError:
            again = "n"
        if again != "y":
            break
    print_summary(games, output_fn)
    return games


# Kept for compatibility with the original entry point.
WordleGame.run = lambda self: self.play()
