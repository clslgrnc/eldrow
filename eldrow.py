import re
import string
from enum import Enum
from random import choice, random
from sys import argv
from typing import Iterable, Optional, Tuple

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
    # check if word matches guess and (partial) hint
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


def is_valid_incremental(word: str, hint: str, guess: str) -> bool:
    i = len(hint) - 1
    if i < 0:
        return True
    if hint[i] == "." and guess[i] not in word:
        return True
    if hint[i].islower() and guess[i] in word and guess[i] != word[i]:
        return True
    if hint[i].isupper() and guess[i] == word[i]:
        return True
    return False


def random_guess(words: "list[str]") -> str:
    # return "serai"
    # TODO: limit choice to most frequent letters
    guess = choice(words)
    return guess


def next_hints(
    words: "list[str]", hint: str, guess: str
) -> "tuple[tuple[str, list[str]], ...]":
    assert len(hint) < len(guess)

    index = len(hint)
    char = guess[index].lower()

    hint_dot = hint + "."
    hint_low = hint + char
    hint_up = hint + char.upper()

    words_dot: "list[str]" = []
    words_low: "list[str]" = []
    words_up: "list[str]" = []

    for w in words:
        if char not in w:
            words_dot.append(w)
        elif char == w[index]:
            words_up.append(w)
        else:
            words_low.append(w)

    return ((hint_dot, words_dot), (hint_low, words_low), (hint_up, words_up))


def eval_guess(
    words: "list[str]",
    guess: str,
    hint_prefix: str = "",
    min_score: int = 0,
    max_score: int = 0,
) -> int:
    # returns size of biggest remaining words
    if len(guess) <= len(hint_prefix):
        return len(words)
    if len(words) <= min_score:
        return len(words)
    # if max_score:
    #     nbr_sub_hints = 3 ** (len(guess) - len(hint_prefix))
    #     expected_min_score = (len(words) + nbr_sub_hints - 1) // nbr_sub_hints
    #     if expected_min_score >= max_score:
    #         # Never reached :(
    #         return len(expected_min_score)
    output = 0
    for h, ws in next_hints(words, hint_prefix, guess):
        score = eval_guess(ws, guess, h, output)
        if score > output:
            output = score
        if max_score and output >= max_score:
            break
    return output


def best_guess(
    all_words: "set[str]",
    words: "list[str]",
    max_word_corpus: int = 500,
    max_guess_corpus: int = 2000,
) -> str:
    word_corpus = simplify(words, max_word_corpus / len(words))
    # max_guess_corpus = (max_guess_corpus * max_word_corpus) // len(word_corpus)
    max_in_corpus = max_guess_corpus // 2
    guess_corpus = simplify(word_corpus, max_in_corpus / len(word_corpus))
    max_out_corpus = max_guess_corpus - len(guess_corpus)
    guess_corpus.extend(simplify(all_words, max_out_corpus / len(all_words)))

    best_guess = random_guess(words)
    best_score = eval_guess(word_corpus, best_guess)
    # print(best_guess, eval_guess(words, best_guess))

    guess_corpus = list(set(guess_corpus) - {best_guess})
    # print(len(word_corpus), len(guess_corpus))
    for guess in guess_corpus:
        score = eval_guess(word_corpus, guess, max_score=best_score)
        if score < best_score:
            best_guess = guess
            best_score = score
    return best_guess


def simplify(rem_words: Iterable[str], ratio: float) -> "list[str]":
    output: "list[str]" = []
    for w in rem_words:
        if random() < ratio:
            output.append(w)
    return output or [choice(list(rem_words))]


class Difficulty(Enum):
    EASY = 0
    NORMAL = 1
    CURSED = 2


def get_hint(guess: str, target: str) -> str:
    assert len(guess) == len(target)
    output = ""
    for g, t in zip(guess.lower(), target.lower()):
        if g == t:
            output += g.upper()
        elif g in target:
            output += g
        else:
            output += "."
    return output


def print_explanations(
    all_words: "set[str]",
    game_rounds: "list[tuple[str,str,str]]",
    guessed_letters: "set[str]",
    eliminated_letters: "set[str]",
) -> None:
    words_with_guessed_letters = [w for w in all_words if guessed_letters <= set(w)]
    print(
        f"There are {len(words_with_guessed_letters)} words with the letters {guessed_letters}:"
    )
    extract = words_with_guessed_letters[:6].copy()
    if len(extract) == 6:
        extract[4] = "..."
    print(extract[:5])

    if len(extract) < 6 and set(extract) <= {w for _, w, _ in game_rounds}:
        return

    words_with_masks: "list[str]" = []
    for w in words_with_guessed_letters:
        valid = True
        for _, _, mask in game_rounds:
            if not is_valid(w, mask, mask.lower()):
                valid = False
                break
        if valid:
            words_with_masks.append(w)
    print(
        f"Reduced to {len(words_with_masks)} words with the constraints "
        f"{', '.join(mask for _,_,mask in game_rounds)}:"
    )
    extract = words_with_masks[:6].copy()
    if len(extract) == 6:
        extract[4] = "..."
    print(extract[:5])

    if len(extract) < 6 and set(extract) <= {w for _, w, _ in game_rounds}:
        return

    words_with_full_hints = [
        w for w in words_with_masks if not eliminated_letters & set(w)
    ]
    print(
        f"But you could not use any of the eliminated letters " f"{eliminated_letters}:"
    )
    print(words_with_full_hints)


def play(
    all_words: "set[str]",
    max_len: int,
):
    remaining_words: "list[str]" = list(all_words)
    guessed_letters: "set[str]" = set()
    eliminated_letters: "set[str]" = set()
    untested_letters: "set[str]" = set(string.ascii_lowercase)
    mask = ["-"] * max_len
    nbr_guesses = 1

    known_letters_pos: "list[set[str]]" = [set() for _ in range(max_len)]

    prompt_length = 21

    used_words: "list[str]" = []
    game_rounds: "list[tuple[str,str,str]]" = []

    lives = 3

    while True:
        # assert len(remaining_words) > 0
        if len(game_rounds) > 3:
            print("You managed to escape!")
            break
        if len(remaining_words) == 0:
            print(f"There is nowhere to run! You get caught!")
            print_explanations(
                all_words, game_rounds, guessed_letters, eliminated_letters
            )
            break
        if len(game_rounds) == 3 and len(remaining_words) > 1:
            print("You managed to escape!")
            print("You still could have played any of:", remaining_words)
            break

        # if len(game_rounds) == 2:
        #     print(remaining_words)
        if len(game_rounds) == 3 and len(remaining_words) == 1:
            print("Only one hiding place left...")
            guess = "?" * max_len
        # elif len(game_rounds) == 0:
        #     guess = "rates"
        else:
            guess = best_guess(all_words, remaining_words)
        prompt = f"Guess {nbr_guesses}:"
        if len(prompt) < prompt_length:
            prompt += " " * (prompt_length - len(prompt))
        print(prompt, guess)

        prompt = f"Your word ({len(remaining_words)}):"
        if len(prompt) < prompt_length:
            prompt += " " * (prompt_length - len(prompt) - 3)
        hint_word = ""
        while not hint_word and lives > 0:
            hint_word = input(f"({lives}) {prompt}").strip()
            if hint_word.endswith("!!!"):
                break
            elif hint_word not in all_words:
                print("Invalid word: not a word.")
                lives -= 1
                hint_word = ""
            elif hint_word in used_words:
                print(
                    f"Invalid word: already played on round {used_words.index(hint_word)}."
                )
                lives -= 1
                hint_word = ""
            elif hint_word not in remaining_words:
                for i, (g, w, h) in enumerate(game_rounds):
                    if get_hint(g, hint_word) == h:
                        continue
                    print(
                        f"Invalid word: incompatible with round {i}.\n"
                        f"\t{g} {g}\n"
                        f"\t{w} {hint_word}\n"
                        f"\t{h} {get_hint(g, hint_word)}"
                    )
                    lives -= 1
                    hint_word = ""
                    break

        if lives == 0:
            print("Too many mistakes! You get caught!")
            if len(remaining_words) > 5:
                remaining_words[4] = "..."
            print("You could have played any of:", remaining_words[:5])
            break

        if hint_word.endswith("!!!"):
            hint = hint_word[:-3]
            hint_word = hint
        else:
            hint = get_hint(guess, hint_word)
        nbr_guesses += 1

        remaining_words = [w for w in remaining_words if w != hint_word]
        used_words.append(hint_word)
        game_rounds.append((guess, hint_word, hint))
        if not guess.startswith("?"):
            print(" " * prompt_length, hint)
        print()
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

        # print(sorted(untested_letters))
        # print(sorted(eliminated_letters))
        # print(known_letters_pos)
        # print("".join(mask), sorted(guessed_letters))

        remaining_words = [w for w in remaining_words if is_valid(w, hint, guess)]
        # print(len(remaining_words))
        # if len(remaining_words) < 5:
        #     print(remaining_words)


if __name__ == "__main__":

    all_words = init_word_list(GAME_WORD_REGEX)
    play(all_words, 5)
