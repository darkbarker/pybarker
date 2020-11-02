import random
from collections import defaultdict

# file_ = open('/home/dimon/temp/lt1.txt')
# import markov
# mar = markov.Markov(file_)
# mar.generate_markov_text(size=10)


class Markov(object):

    def __init__(self, open_file):
        self.words = self._file_to_words(open_file)
        self.word_size = len(self.words)
        self.cache = self._database()

    def _file_to_words(self, open_file):
        open_file.seek(0)
        data = open_file.read()
        return data.split()

    # string to word-triples
    def _triples(self):
        if len(self.words) < 3:
            return
        for i in range(self.word_size - 2):
            yield (self.words[i], self.words[i + 1], self.words[i + 2])

    def _database(self):
        cache = defaultdict(list)
        for w1, w2, w3 in self._triples():
            cache[(w1, w2)].append(w3)
        return dict(cache)

    def generate_text(self, size=25):
        seed = random.randint(0, self.word_size - 3)
        seed_word, next_word = self.words[seed], self.words[seed + 1]
        gen_words = []
        for _ in range(size):
            gen_words.append(seed_word)
            seed_word, next_word = next_word, random.choice(self.cache[(seed_word, next_word)] if (seed_word, next_word) in self.cache else self.words)
        return " ".join(gen_words)
