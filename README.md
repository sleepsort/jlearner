# JLearner

A Python based utility to help learning Japanese. Currently used to memorize Kana characters and Japanese words.

With the help of this tool, I can become <b>proficient</b> with around 80 new Japanese words in one afternoon. Ah, I'm not very quick when learning language, actually.

Personally I prefer this routine for [Ebbinghaus curve](http://en.wikipedia.org/wiki/Forgetting_curve): do a test on Day 1, then repeat on Day 2, Day 4, Day 7, Day 11, Day 13, Day 14.

## Kana learning

    python2 kana.py -h

Four modes are available:

    Hiragana -> Romaji test, i.e.  あ-> a
    Katakana -> Romaji test, i.e.  ア-> a
    Romaji -> Hiragana test, i.e.  a -> あ
    Romaji -> Katakana test, i.e.  a -> ア

There is also a crazy `shuffle` mode, which randomizes the 
character table, making the test more difficult.


## Words learning
   
    python2 dict.py -h

Two modes are available:

    Chinese -> Kana test: 
      Kanji/Romaji solutions are prefered, and a Hiragana solution 
      is accepted only if Kanji doesn't exist for that word.
    
    Chinese -> Kana test:
      tests Hiragana with buttons, I changed the Gojūon a bit so that 
      we can input some special characters.

Before completing the dictionary file you specified, the test will start from last quit, remembering all the passes and fails you did last time.

## Installation

You need to install [Python 2](http://www.python.org/getit/)

Actually the UI is based on [TkInter](https://wiki.python.org/moin/TkInter), but usually you don't need to install it yourself

Remove all files under `log` so that it will keep your own progress.

## Project hierarchy

    .
    ├── data
    │   ├── dict  -> Dictionaries for word tests
    │   └── kana  -> Gojūon and data for kana tests
    ├── log       -> Permanent log files
    ├── tools     -> Development only
    │
    ├── dict.py   -> Word test
    └── kana.py   -> Kana test


## License

[Apache License 2.0](http://www.apache.org/licenses/LICENSE-2.0)
