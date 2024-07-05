from matches import OrthographicMatch, PhoneticMatch, RhymeMatch
from phonetics.phonetics import *

import gensim.downloader as api

model = api.load("glove-wiki-gigaword-100")
