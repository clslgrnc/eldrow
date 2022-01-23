import re
import string
from collections import defaultdict
from enum import Enum
from functools import lru_cache
from random import choice, random
from sys import argv
from typing import Optional

GAME_WORD_REGEX = r"^[a-z]{5}\n?$"


def normalize_word(w: str, sorted_chars: str) -> str:
    return "".join(sorted(set(w), key=lambda w: tuple(sorted_chars.find(c) for c in w)))


def init_words(regexp: str, file: str = "words.txt") -> "set[str]":
    words: "set[str]" = set()
    with open(file, "r") as f:
        for line in f:
            if re.fullmatch(regexp, line.strip().lower()):
                words.add(line.strip().lower())
    return words


def init_word_dict(words: "set[str]", sorted_chars: str) -> "defaultdict[str,set[str]]":
    output: "defaultdict[str,set[str]]" = defaultdict(set)
    for word in words:
        key = normalize_word(word, sorted_chars)
        output[key].add(word)

    return output


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


get_candidates_cache: "dict[str, list[str]]" = {}


def get_candidates(
    word_dict: "defaultdict[str,set[str]]", words: "list[str]", chars: str
) -> "list[str]":
    if chars in get_candidates_cache:
        return get_candidates_cache[chars]
    if len(chars) % 5 != 0:
        return []
    if len(chars) == 0:
        return [""]

    # prefix: str = "\t" * (5 - len(chars) // 5)

    output: "list[str]" = []
    for word in words:
        remaining_chars = "".join(c for c in chars if c not in word)
        remaining_words = []
        if remaining_chars not in get_candidates_cache:
            remaining_words = [w for w in words if not set(w) & set(word)]
        # print(prefix, word, len(remaining_words), remaining_chars)
        sub_candidates = get_candidates(word_dict, remaining_words, remaining_chars)
        for candidate in sub_candidates:
            # print(candidate)
            output.append(f"{word_dict[word]} {candidate}")

    get_candidates_cache[chars] = output
    return output


if __name__ == "__main__":
    all_words = init_words(GAME_WORD_REGEX)

    counts: "dict[str,int]" = {c: 0 for c in string.ascii_lowercase}
    for k in all_words:
        for c in set(k):
            counts[c] += 1

    sorted_chars = sorted(counts.keys(), key=lambda k: counts[k], reverse=True)
    rare_chars = set(sorted_chars[-2:])
    print(sorted_chars)

    sorted_chars = "".join(sorted_chars)
    word_dict = init_word_dict(all_words, sorted_chars)

    vowels = set("aeiou")
    rare_words = {w for k, wl in word_dict.items() for w in wl if not set(k) & vowels}
    print(rare_words)

    order = lambda w: (len(w), *tuple(sorted_chars.find(c) for c in w))

    search_keys = sorted(
        {k for k in word_dict if len(k) == 5 and not set(k) & rare_chars}, key=order
    )
    print(len(search_keys))
    relaxed_search_keys = {
        k for k in word_dict if len(k) > 3 and not set(k) & rare_chars
    }
    print(len(relaxed_search_keys))

    # for word0 in sorted(all_words):
    for word0 in sorted(relaxed_search_keys):
        print(word0)
        if len(word0) == 4:
            candidates: "list[str]" = get_candidates(
                word_dict,
                [w for w in search_keys if not set(w) & set(word0)],
                "".join(
                    c
                    for c in string.ascii_lowercase
                    if c not in rare_chars and c not in word0
                ),
            )
        else:
            assert len(word0) == 5
            candidates = []
            for i in range(5):
                forbidden_chars = "".join(c for c in word0 if c != word0[i])
                candidates.extend(
                    get_candidates(
                        word_dict,
                        [w for w in search_keys if not set(w) & set(forbidden_chars)],
                        "".join(
                            c
                            for c in string.ascii_lowercase
                            if c not in rare_chars and c not in forbidden_chars
                        ),
                    ),
                )

        for candidate in candidates:
            print(word_dict[word0], candidate)

    # # for word0 in sorted(all_words):
    # for word0 in search_keys:
    #     print(word0)
    #     ls0 = set(word0)
    #     relaxed_rw0 = [
    #         w for w in relaxed_search_keys if len(set(w) | ls0) >= 9 or w == word0
    #     ]
    #     i0 = relaxed_rw0.index(word0)
    #     rw0 = [w for w in relaxed_rw0[i0 + 1 :] if not set(w) & set(word0)]
    #     for i1, word1 in enumerate(rw0):
    #         ls1 = ls0 | set(word1)
    #         rw1 = [w for w in rw0[i1 + 1 :] if not set(w) & set(word1)]
    #         relaxed_rw1 = [w for w in relaxed_rw0 if len(set(w) | ls1) >= 14]
    #         for i2, word2 in enumerate(rw1):
    #             ls2 = ls1 | set(word2)
    #             rw2 = [w for w in rw1[i2 + 1 :] if not set(w) & set(word2)]
    #             relaxed_rw2 = [w for w in relaxed_rw1 if len(set(w) | ls2) >= 19]
    #             for word3 in rw2:
    #                 ls3 = ls2 | set(word3)
    #                 rw3 = {
    #                     w
    #                     for wk in relaxed_rw2
    #                     for w in word_dict[wk]
    #                     if len(set(wk) | ls3) >= 24
    #                 }
    #                 if not rw3:
    #                     continue
    #                 print(
    #                     *[word_dict[w] for w in [word0, word1, word2, word3]],
    #                     rw3,
    #                 )

# {'paxes'} {'frown'} {'chimb'} {'klutz'} {'gyved'}
# {'paxes'} {'crwth'} {'zombi'} {'flunk'} {'gyved'}
# {'vegas'} {'crwth'} {'zinky'} {'plumb'} {'foxed'}
# {'vegas'} {'crwth'} {'zinky'} {'flump'} {'boxed'}
# {'fazes'} {'crwth'} {'buxom'} {'plink'} {'gyved'}
# {'fazes'} {'crumb'} {'phlox'} {'twink'} {'gyved'}
# {'faxes'} {'bortz'} {'clink'} {'whump'} {'gyved'}
# {'faxes'} {'brown'} {'chimp'} {'klutz'} {'gyved'}
# {'faxes'} {'crowd'} {'vying'} {'klutz'} {'bumph'}
# {'faxes'} {'crowd'} {'vying'} {'bumph'} {'klutz'}
# {'faxes'} {'brock'} {'zingy'} {'whump'} {'veldt'}
# {'faxes'} {'crwth'} {'zombi'} {'plunk'} {'gyved'}
# {'faxes'} {'crwth'} {'zingy'} {'plumb'} {'vodka'}
# {'faxes'} {'crunk'} {'whomp'} {'blitz'} {'gyved'}
# {'waxes'} {'bortz'} {'chink'} {'flump'} {'gyved'}
# {'waxes'} {'bortz'} {'chimp'} {'flunk'} {'gyved'}
# {'waxes'} {'frock'} {'zingy'} {'bumph'} {'veldt'}
# {'waxes'} {'grift'} {'block'} {'nudzh'} {'vampy'}
# {'waxes'} {'fritz'} {'clonk'} {'bumph'} {'gyved'}
# {'zaxes'} {'croft'} {'blink'} {'whump'} {'gyved'}
# {'zaxes'} {'brown'} {'flick'} {'thump'} {'gyved'}
# {'zaxes'} {'brown'} {'thick'} {'flump'} {'gyved'}
# {'zaxes'} {'frown'} {'thick'} {'plumb'} {'gyved'}
# {'zaxes'} {'crowd'} {'bight'} {'flunk'} {'vampy'}
# {'zaxes'} {'broch'} {'twink'} {'flump'} {'gyved'}
# {'paxes'} {'frown'} {'chimb'} {'klutz'} {'gyved'}
# {'paxes'} {'crwth'} {'zombi'} {'flunk'} {'gyved'}
# {'vegas'} {'crwth'} {'zinky'} {'plumb'} {'foxed'}
# {'vegas'} {'crwth'} {'zinky'} {'flump'} {'boxed'}
# {'fazes'} {'crwth'} {'buxom'} {'plink'} {'gyved'}
# {'fazes'} {'crumb'} {'phlox'} {'twink'} {'gyved'}
# {'faxes'} {'bortz'} {'clink'} {'whump'} {'gyved'}
# {'faxes'} {'brown'} {'chimp'} {'klutz'} {'gyved'}
# {'faxes'} {'crowd'} {'vying'} {'klutz'} {'bumph'}
# {'faxes'} {'crowd'} {'vying'} {'bumph'} {'klutz'}
# {'faxes'} {'brock'} {'zingy'} {'whump'} {'veldt'}
# {'faxes'} {'crwth'} {'zombi'} {'plunk'} {'gyved'}
# {'faxes'} {'crwth'} {'zingy'} {'plumb'} {'vodka'}
# {'faxes'} {'crunk'} {'whomp'} {'blitz'} {'gyved'}
# {'waxes'} {'bortz'} {'chink'} {'flump'} {'gyved'}
# {'waxes'} {'bortz'} {'chimp'} {'flunk'} {'gyved'}
# {'waxes'} {'frock'} {'zingy'} {'bumph'} {'veldt'}
# {'waxes'} {'grift'} {'block'} {'nudzh'} {'vampy'}
# {'waxes'} {'fritz'} {'clonk'} {'bumph'} {'gyved'}
# {'zaxes'} {'croft'} {'blink'} {'whump'} {'gyved'}
# {'zaxes'} {'brown'} {'flick'} {'thump'} {'gyved'}
# {'zaxes'} {'brown'} {'thick'} {'flump'} {'gyved'}
# {'zaxes'} {'frown'} {'thick'} {'plumb'} {'gyved'}
# {'zaxes'} {'crowd'} {'bight'} {'flunk'} {'vampy'}
# {'zaxes'} {'broch'} {'twink'} {'flump'} {'gyved'}
# {'zaxes'} {'brock'} {'flint'} {'whump'} {'gyved'}
# {'zaxes'} {'brock'} {'width'} {'flung'} {'vampy'}
# {'zaxes'} {'brock'} {'width'} {'flump'} {'vying'}
# {'zaxes'} {'brock'} {'vying'} {'flump'} {'width'}

# {'zaxes'} {'brock'} {'flint'} {'whump'} {'gyved'}
# {'zaxes'} {'brock'} {'width'} {'flung'} {'vampy'}
# {'zaxes'} {'brock'} {'width'} {'flump'} {'vying'}
# {'zaxes'} {'brock'} {'vying'} {'flump'} {'width'}
