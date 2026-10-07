from collections import Counter

GREEN, YELLOW, GRAY = "green", "yellow", "gray"


def evaluate(target, guess):
    
    if len(target) != len(guess):
        raise ValueError("target and guess must be the same length")

    result = [GRAY] * len(guess)
    unmatched = Counter()

    for i, (t, g) in enumerate(zip(target, guess)):
        if t == g:
            result[i] = GREEN
        else:
            unmatched[t] += 1

    for i, g in enumerate(guess):
        if result[i] == GREEN:
            continue
        if unmatched[g] > 0:
            result[i] = YELLOW
            unmatched[g] -= 1

    return result


_SYMBOL = {GREEN: "🟩", YELLOW: "🟨", GRAY: "⬛"}


def render(guess, feedback):
    letters = " ".join(c.upper() for c in guess)
    squares = "".join(_SYMBOL[f] for f in feedback)
    return f"{letters}   {squares}"