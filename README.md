# Puntomatic

Running `ipython -i puntomatic.py` loads everything that we need.
In each of the examples below, we take two words and their neighbors in the vector space, test the given matching/sequencing algorithm on the cartesian product of the similar word lists and return a list of matches, prioritized by the proximity in the vector space and the score returned by the matching/sequencing algorithm.

### `RhymeMatch`

Matching when the words rhyme - the stressed syllable is the same and the rest is similar-sounding.

```python
In [1]: RhymeMatch.analyze_groups(
   ...:     model.most_similar(positive=[model["word"]], topn=100),
   ...:     model.most_similar(positive=[model["music"]], topn=100),
   ...: )
Out[1]: 
[Prioritized(value=('translation', 'compilation', "['SH', 'AH0', 'N'] ['SH', 'AH0', 'N']"), priority=1.190707282584782),
 Prioritized(value=('description', 'musician', "['P', 'SH', 'AH0', 'N'] [[], 'SH', 'AH0', 'N']"), priority=0.8092952440097605)]
```

### `OrthographicMatch`

Matching when parts of both words are spelt similarly.
This means that we may be able to create a new pseudoword which satisfies one of the following:
- The pseudoword starts with one of the origin words, ends with the other and shares some letters in the middle.
- The pseudoword approximates one of the origin words containing the other one.

```python
In [2]: OrthographicMatch.analyze_groups(
   ...:     model.most_similar(positive=[model["peach"]], topn=100),
   ...:     model.most_similar(positive=[model["beret"]], topn=100),
   ...: )[:20]
Out[2]: 
[Prioritized(value=('banana', 'bandana', "['b', 'a', 'n', [], 'a', 'n', 'a'] ['b', 'a', 'n', 'd', 'a', 'n', 'a'] 0 0"), priority=1.7521752392914536),
 Prioritized(value=('cucumber', 'beret', "['b', 'e', 'r'] ['b', 'e', 'r'] 5 0"), priority=1.600507378578186),
 Prioritized(value=('watermelon', 'sweater', "['w', [], 'a', 't', 'e', 'r'] ['w', 'e', 'a', 't', 'e', 'r'] 0 1"), priority=1.408820312739394),
 Prioritized(value=('banana', 'bandanna', "['b', 'a', 'n', [], 'a', 'n', [], 'a'] ['b', 'a', 'n', 'd', 'a', 'n', 'n', 'a'] 0 0"), priority=1.3995730949305312),
 Prioritized(value=('cucumber', 'berets', "['b', 'e', 'r'] ['b', 'e', 'r'] 5 0"), priority=1.2787667037138561),
 Prioritized(value=('cobbler', 'beret', "['b', 'l', 'e', 'r'] ['b', [], 'e', 'r'] 3 0"), priority=1.2242718935012817),
 Prioritized(value=('peach', 'parachutist', "['p', 'e', [], 'a', 'c', 'h'] ['p', 'a', 'r', 'a', 'c', 'h'] 0 0"), priority=1.2063584573696033),
 Prioritized(value=('olive', 'livery', "['l', 'i', 'v', 'e'] ['l', 'i', 'v', 'e'] 1 0"), priority=1.1066191064437305),
 Prioritized(value=('mango', 'infantryman', "['m', 'a', 'n'] ['m', 'a', 'n'] 0 8"), priority=1.1061496351137272),
 Prioritized(value=('sherbet', 'beret', "[[], 'e', 'r', 'b', 'e', 't'] ['b', 'e', 'r', [], 'e', 't'] 2 0"), priority=1.0987776517868042),
 Prioritized(value=('mango', 'commando', "['m', 'a', 'n', 'g', 'o'] ['m', 'a', 'n', 'd', 'o'] 0 3"), priority=1.0937462144529313),
 Prioritized(value=('quince', 'sequined', "['q', 'u', 'i', 'n', 'c', 'e'] ['q', 'u', 'i', 'n', [], 'e'] 0 2"), priority=1.0907665764470238),
 Prioritized(value=('ripe', 'striped', "['r', 'i', 'p', 'e'] ['r', 'i', 'p', 'e'] 0 2"), priority=1.08471233817734),
 Prioritized(value=('cabbage', 'badge', "['b', 'a', [], 'g', 'e'] ['b', 'a', 'd', 'g', 'e'] 3 0"), priority=1.0840953955584745),
 Prioritized(value=('lemon', 'emblem', "['l', 'e', 'm'] ['l', 'e', 'm'] 0 3"), priority=0.9980275453260354),
 Prioritized(value=('peach', 'checkered', "['c', 'h'] ['c', 'h'] 3 0"), priority=0.9872452005440095),
 Prioritized(value=('ripe', 'pinstriped', "['r', 'i', 'p', 'e'] ['r', 'i', 'p', 'e'] 0 5"), priority=0.9849596686663276),
 Prioritized(value=('ripe', 'pinstripes', "['r', 'i', 'p', 'e'] ['r', 'i', 'p', 'e'] 0 5"), priority=0.9837399806427811),
 Prioritized(value=('pear', 'paratrooper', "['p', 'e', 'a', 'r'] ['p', 'e', [], 'r'] 0 8"), priority=0.9785501784792672),
 Prioritized(value=('cobbler', 'berets', "['b', 'l', 'e', 'r'] ['b', [], 'e', 'r'] 3 0"), priority=0.9781636465137211)]
```

Some of the pseudowords made with the algorithm's suggestions are:
- "cucumberet" (cucumber + beret)
- "sweatermelon" (watermelon + sweater)
- "clobberet" (clobber + beret)
- "olivery" (olive + livery)
- "cabbadge" (cabbage + badge)
- "emblemon" (emblem + lemon)
- "pearatrooper" (pear + paratrooper)

> [!NOTE]
> The words were constructed manually using the output shown above, the program doesn't currently construct the words.

### `PhoneticMatch`

Like `OrthographicMatch`, but running the algorithm on the phonemes, instead of the graphemes of the word - the matched parts of the words are pronounced similarly.

In this example, the second origin in the vector space is represented by three words instead of one.

```python
In [3]: PhoneticMatch.analyze_groups(
   ...:     model.most_similar(positive=[model["wordplay"]], topn=30),
   ...:     model.most_similar(
   ...:         positive=[model["automatic"], model["computer"], model["program"]], topn=100
   ...:     ),
   ...: )[:10]
Out[3]: 
[Prioritized(value=('one-liners', 'online', "[[], 'N', 'L', 'AY1', 'N'] ['AO1', 'N', 'L', 'AY2', 'N'] 2 0"), priority=1.234040661377108),
 Prioritized(value=('sophomoric', 'require', "['R', 'IH0', 'K'] ['R', 'IH0', 'K'] 6 0"), priority=1.1780929696755535),
 Prioritized(value=('one-liners', 'one', "['W', 'AH1', 'N'] ['W', 'AH1', 'N'] 0 0"), priority=1.1619160099705752),
 Prioritized(value=('nonsensical', 'similar', "['S', 'IH0', 'K', 'AH0', 'L'] ['S', 'IH1', 'M', 'AH0', 'L'] 6 0"), priority=1.1580669671242383),
 Prioritized(value=('puns', 'applications', "['P', 'AH1', 'N', 'Z'] [[], 'AH0', 'N', 'Z'] 0 7"), priority=1.1313672180477852),
 Prioritized(value=('rhyming', 'programming', "['R', 'AY1', 'M', 'IH0', 'NG'] ['R', 'AE2', 'M', 'IH0', 'NG'] 0 4"), priority=1.0772763038313826),
 Prioritized(value=('lyricism', 'system', "['S', 'IH2', 'Z', [], 'AH0', 'M'] ['S', 'IH1', 'S', 'T', 'AH0', 'M'] 4 0"), priority=0.9361117530255925),
 Prioritized(value=('rhymes', 'programs', "['R', 'AY1', 'M', 'Z'] ['R', 'AE2', 'M', 'Z'] 0 4"), priority=0.9195497664619481),
 Prioritized(value=('doggerel', 'allows', "['AH0', 'L'] ['AH0', 'L'] 4 0"), priority=0.8909283855176682),
 Prioritized(value=('lyricism', 'systems', "['S', 'IH2', 'Z', [], 'AH0', 'M'] ['S', 'IH1', 'S', 'T', 'AH0', 'M'] 4 0"), priority=0.8856206272858103)]
```

Some of the pseudowords made with the algorithm's suggestions are:
- "onliners" (one-liners + online)
- "sophomorequire" (sophomoric + require)
- "progrhyming" (programming + rhyming)
