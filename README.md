My own take on [wordle](https://www.powerlanguage.co.uk/wordle/) (or [lingo](https://en.wikipedia.org/wiki/Lingo_(American_game_show))).

As a weekend project, the code is quite ugly, but it should work.
First you need a file `words.txt` that contains one word per line, the following link may help you find one:  
https://boardgames.stackexchange.com/questions/38366/latest-collins-scrabble-words-list-in-text-file

My initial goal was to develop a wordle solver, instead you'll find:

- `python3 search.py` will return sequences of five five letters words that cover the 24 most frequent letters;
- `python3 wordle.py (easy|normal|cursed)` will let you play wordle with three different difficult levels (it is kind of cheating as it chooses the target word according to your guesses), it turns out the cursed version has already been done by [qntm](https://qntm.org/files/wordle/index.html));
- and finally `python3 eldrow.py` which is, to me, the most interesting (or least pedestrian).

# Eldrow: reversed wordle

There are two players:

- the first one is the hunter (currently played by the computer);
- the second one is the prey.

The prey hides behind five letters words, the hunter tries to guess the word the prey hides behind in up to three guesses.

At each turn the hunter choose any five letters word of the corpus.
The prey must choose a valid word:

- it must be in the corpus (obviously);
- it must not have been used before by the prey;
- it must be compatible with the previous hints.

The prey looses if it makes three mistakes or if no valid word remains.
If there is only one remaining valid word after three round, there is a last bonus round where the prey must find this last word.

```console
user@home:~/src/wordle$ python eldrow.py 
Guess 1:              snare
(3) Your word (9403): prism
                      s..r.

Guess 2:              torsi
(3) Your word (226):  ogres
Invalid word: incompatible with round 0.
	snare snare
	prism ogres
	s..r. s..re
(2) Your word (226):  words
                      .ORs.

Guess 3:              flick
(2) Your word (19):   lords
                      .l...

There is nowhere to run! You get caught!
There are 15 words with the letters {'l', 's', 'r', 'o'}:
['rotls', 'orles', 'loser', 'lords', '...']
Reduced to 3 words with the constraints s..r., .ORs., .l...:
['lords', 'loris', 'lores']
But you could not use any of the eliminated letters {'n', 'e', 't', 'k', 'c', 'i', 'f', 'a'}:
['lords']

```

The first number between parenthesis is the number of lives, you loose one at each mistake, the second one is the number of remaining valid words.

The hunter strategy is not optimal, but pretty good.
