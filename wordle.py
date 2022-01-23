import re
import string
from enum import Enum
from random import choice, random
from sys import argv
from typing import Optional

GAME_WORD_REGEX = r"^[a-z]{5}\n?$"


def init_word_list(
    regexp: str, nbr_uniq: "Optional[set[int]]" = None, file: str = "words.txt"
) -> "set[str]":
    output: "set[str]" = set()
    with open(file, "r") as f:
        for line in f:
            if re.fullmatch(regexp, line.strip().lower()):
                output.add(line.strip().lower())

    if nbr_uniq is None:
        return output

    return {w for w in output if len(set(w)) in nbr_uniq}


def is_valid(word: str, hint: str, guess: str) -> bool:
    # check if word marches guess and hint
    if len(word) < len(hint) or len(word) != len(guess):
        return False

    for i in range(len(hint)):
        if hint[i] == "." and guess[i] not in word:
            continue
        if hint[i].islower() and guess[i] in word and guess[i] != word[i]:
            continue
        if hint[i].isupper() and guess[i] == word[i]:
            continue
        return False
    return True


def random_hint(words: "set[str]", guess: str) -> str:
    candidate = choice(list(words - {guess}))
    hint = "".join(
        c.upper() if guess[i] == candidate[i] else c.lower() if c in candidate else "."
        for i, c in enumerate(guess)
    )
    return hint


def hint_score(hint: str) -> int:
    return len({c.lower() for c in hint if c != "."}) + len(
        {c for c in hint if c != "." and c.isupper()}
    )


def choose_hint(words: "set[str]", guess: str, min_hints: int = 0) -> str:
    best_hint = random_hint(words, guess)
    best_value = (
        min(min_hints, hint_score(best_hint)),
        len({w for w in words if is_valid(w, best_hint, guess)}),
    )
    # print(f"choosing worst hint: {best_hint} ({best_value})")

    def aux(remaining_words: "set[str]", hint_prefix: str):
        nonlocal best_hint
        nonlocal best_value
        nonlocal guess
        nbr_remaining_words = len(remaining_words)
        if nbr_remaining_words == 0:
            return
        sc, nw = (min(min_hints, hint_score(hint_prefix)), nbr_remaining_words)
        value = sc, nw
        best_expected_value = (
            min(min_hints, sc + 2 * (len(best_hint) - len(hint_prefix))),
            nw,
        )
        # print(value, best_expected_value, best_value)
        if best_expected_value < best_value:
            return
        if len(hint_prefix) == len(guess):
            if not value >= best_value:
                return
            if value == best_value and hint_score(hint_prefix) < hint_score(best_hint):
                return
            best_hint = hint_prefix
            best_value = value
            # print(f"choosing worst hint: {best_hint} ({best_value})")
            return

        g_char = guess[len(hint_prefix)]
        for h_char in [".", g_char.lower(), g_char.upper()]:
            # for h_char in [g_char.upper(), g_char.lower(), "."]:
            new_hint = hint_prefix + h_char
            new_words = {w for w in remaining_words if is_valid(w, new_hint, guess)}
            aux(new_words, new_hint)

    aux(words - {guess}, "")
    return best_hint


def simplify(rem_words: "set[str]", ratio: float) -> "set[str]":
    output: "set[str]" = set()
    for w in rem_words:
        if random() < ratio:
            output.add(w)
    return output or {choice(list(rem_words))}


class Difficulty(Enum):
    EASY = 0
    NORMAL = 1
    CURSED = 2


def play(
    all_words: "set[str]",
    target_words: "set[str]",
    difficulty: Difficulty,
    max_len: int,
):
    remaining_words = target_words
    guessed_letters: "set[str]" = set()
    eliminated_letters: "set[str]" = set()
    untested_letters: "set[str]" = set(string.ascii_lowercase)
    mask = ["-"] * max_len
    nbr_guesses = 1

    known_letters_pos: "list[set[str]]" = [set() for _ in range(max_len)]

    while True:
        guess = input(f"Guess {nbr_guesses}: ").strip()
        if guess not in all_words:
            print("invalid guess")
            continue

        nbr_guesses += 1
        if remaining_words == {guess}:
            print("You won!")
            break

        if difficulty == Difficulty.EASY:
            hint = choose_hint(remaining_words, guess, choice([1, 2, 2, 3]))
        elif difficulty == Difficulty.NORMAL:
            hint = choose_hint(remaining_words, guess, choice([0, 1, 1, 2]))
        else:
            hint = choose_hint(remaining_words, guess, 0)

        print(hint)
        for i, c in enumerate(hint):
            untested_letters.discard(guess[i])
            if c == ".":
                eliminated_letters.add(guess[i])
                continue
            if c.lower() not in guessed_letters:
                guessed_letters.add(c.lower())
                for index, s in enumerate(known_letters_pos):
                    if mask[index] == "-":
                        s.add(c.lower())
            if c.isupper():
                mask[i] = c
                known_letters_pos[i] = {c}
            else:
                known_letters_pos[i].discard(c.lower())
            if len(guessed_letters) == len(mask):
                for k in mask:
                    if k == "-":
                        continue
                    for s in known_letters_pos:
                        s.discard(k.lower())

        if difficulty != Difficulty.CURSED:
            print(sorted(untested_letters))
            print(sorted(eliminated_letters))
            if difficulty == Difficulty.EASY:
                print(known_letters_pos)
        print("".join(mask), sorted(guessed_letters))

        remaining_words = {w for w in remaining_words if is_valid(w, hint, guess)}
        print(list(remaining_words)[:5])
        # print(len(remaining_words))
        # if len(remaining_words) < 5:
        #     print(remaining_words)


if __name__ == "__main__":
    diff = "NORMAL"
    if len(argv) > 1:
        diff = argv[1].upper()

    if diff == "EASY":
        all_words = init_word_list(GAME_WORD_REGEX, {5})
    else:
        all_words = init_word_list(GAME_WORD_REGEX)

    if diff == "EASY":
        words = simplify(all_words, 0.6)
        difficulty = Difficulty.EASY
    elif diff == "CURSED":
        words = simplify(all_words, 0.6)
        difficulty = Difficulty.CURSED
    else:
        words = simplify(all_words, 0.4)
        difficulty = Difficulty.NORMAL

    if diff != "CHEATS":
        play(all_words, words, difficulty, 5)
    else:

        counts: "dict[str,int]" = {c: 0 for c in string.ascii_lowercase}

        for w in all_words:
            for c in set(w):
                counts[c] += 1

        for key, value in counts.items():
            if value < 250:
                print(key, value)
        rare_chars = {"j", "q"}

        vowels = set("aeiou")
        rare_words = {w for w in all_words if not set(w) & vowels}

        print(rare_words)

        # for word0 in sorted(all_words):
        for word0 in sorted(rare_words):
            if len(set(word0)) < 5 or set(word0) & rare_chars:
                continue
            print(word0)
            ls0 = set(word0)
            # rrw0 = {w for w in rare_words if word0 < w and not set(w) & ls0}
            # if len(vowels - ls0) < 4 and not rrw0:
            #     continue
            rw0 = {w for w in all_words if word0 < w and not set(w) & ls0}
            if not rw0:
                continue
            for word1 in rw0:
                if len(set(word1)) < 5 or set(word1) & rare_chars:
                    continue
                ls1 = ls0 | set(word1)
                # rrw1 = {w for w in rrw0 if word1 < w and not set(w) & ls1}
                # if len(vowels - ls1) < 3 and not rrw1:
                #     continue
                rw1 = {w for w in rw0 if word1 < w and not set(w) & ls1}
                if len(rw1) < 2 or len({c for w in rw1 for c in w}) < 10:
                    continue
                for word2 in rw1:
                    if len(set(word2)) < 5 or set(word2) & rare_chars:
                        continue
                    ls2 = ls1 | set(word2)
                    # rrw = {w for w in rare_words if word2 < w and not set(w) & ls2}
                    # if len(vowels - ls2) < 2 and not rrw:
                    #     continue
                    rw2 = {w for w in rw1 if word2 < w and not set(w) & ls2}
                    if len(rw2) < 1 or len({c for w in rw2 for c in w}) < 5:
                        continue
                    # print(word0, word1, word2, rw2)
                    for word3 in rw2:
                        if len(set(word3)) < 5 or set(word3) & rare_chars:
                            continue
                        ls3 = ls2 | set(word3)
                        rw3 = {w for w in all_words if len(set(w) | ls3) >= 24}
                        if not rw3:
                            continue
                        for word4 in rw3:
                            print("!!!", word0, word1, word2, word3, word4)


# !!! picky swang thumb voxel fjord
# !!! packs thumb voxel wingy fjord
# !!! prove thumb wacks zingy fjeld
# !!! prove thumb wacky zings fjeld
# !!! pings thumb voxel wacky fjord
# !!! proxy veldt whack zings jumbo
# !!! proxy veldt whack zings bumfs
# !!! proxy thumb wacke zings fjeld
# !!! proxy thumb waved zings fleck
# !!! proxy thumb waved zings flick
# !!! proxy thumb waved zings flock
# !!! proxy thumb waved zings flack
# !!! proxy thumb vegan wicks fjeld
# !!! proxy quick veldt whang jambs
# !!! proxy quick veldt whang bumfs
# !!! pluck thewy vangs zombi fjord
# !!! pluck vixen womby zarfs dight
# !!! pluck sixth vegan womby fjord
# !!! pluck thegn womby zarfs jived
# !!! pluck thing womby zaxes fjord
# !!! pluck thing womby zarfs vexed
# !!! pluck thing womby zarfs jived
# !!! pluck tombs wharf zingy vexed
# !!! pluck tombs wharf zingy jived
# !!! pluck rhomb wafts zingy vexed
# !!! pluck rhomb wafts zingy jived
# !!! pluck voted wharf zingy jambs
