import unittest
from feedback import evaluate
from game import WordleGame, WON, LOST, QUIT, run_session
from words import WORDS, SUPPORTED_LENGTHS

G, Y, X = "green", "yellow", "gray"


def scripted(lines):
    it = iter(lines)
    return lambda prompt="": next(it)


def play(target, inputs):
    out = []
    g = WordleGame(len(target), target=target, input_fn=scripted(inputs), output_fn=out.append)
    g.play()
    return g, out


class TestFeedback(unittest.TestCase):
    def test_extra_guess_letter_is_gray(self):
        self.assertEqual(evaluate("crane", "eerie"), [X, X, Y, X, G])

    def test_all_green(self):
        self.assertEqual(evaluate("apple", "apple"), [G] * 5)

    def test_all_absent(self):
        self.assertEqual(evaluate("crane", "light"), [X] * 5)

    def test_yellow_limited_by_target_count(self):
        # target has one 'p'; only the first non-exact p gets yellow
        self.assertEqual(evaluate("plant", "apple"), [Y, Y, X, Y, X])

    def test_green_takes_priority_over_earlier_yellow(self):
        self.assertEqual(evaluate("stone", "geese"), [X, X, X, Y, G])  # one e in guess exact

    def test_two_copies_in_target(self):
        self.assertEqual(evaluate("array", "rarer"), [Y, Y, G, X, X])
        self.assertEqual(evaluate("noon", "oooo"), [X, G, G, X])

    def test_lengths(self):
        self.assertEqual(evaluate("book", "boot"), [G, G, G, X])
        self.assertEqual(evaluate("coffee", "effect"), [Y, Y, G, Y, Y, X])
        self.assertEqual(evaluate("summer", "mumble"), [Y, G, G, X, X, Y])
        self.assertEqual(evaluate("little", "tittle"), [X, G, G, G, G, G])

    def test_length_mismatch(self):
        with self.assertRaises(ValueError):
            evaluate("apple", "app")


class TestGame(unittest.TestCase):
    def test_invalid_guesses_do_not_consume_turns(self):
        g, _ = play("apple", ["abc", "toolong", "12345", "", "grape", "apple"])
        self.assertEqual(g.outcome, WON)
        self.assertEqual(len(g.history), 2)

    def test_win_on_final_guess(self):
        g, _ = play("apple", ["stone"] * 5 + ["apple"])
        self.assertEqual(g.outcome, WON)
        self.assertEqual(len(g.history), 6)

    def test_loss_after_six(self):
        g, out = play("apple", ["stone"] * 6)
        self.assertEqual(g.outcome, LOST)
        self.assertTrue(any("APPLE" in line for line in out))

    def test_quit(self):
        g, _ = play("apple", ["stone", "q"])
        self.assertEqual(g.outcome, QUIT)
        self.assertEqual(len(g.history), 1)

    def test_all_lengths_playable(self):
        for n in SUPPORTED_LENGTHS:
            word = next(w for w in WORDS if len(w) == n)
            g, _ = play(word, [word])
            self.assertEqual(g.outcome, WON)

    def test_session_summary(self):
        out = []
        run_session(scripted(["4", "q"]), out.append)
        self.assertTrue(any("Session summary" in l for l in out))


if __name__ == "__main__":
    unittest.main()
