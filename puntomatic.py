from orthographic_match import OrthographicMatch
from phonetic_match import PhoneticMatch
from rhyme_match import RhymeMatch

import gensim.downloader as api

model = api.load("glove-wiki-gigaword-100")
