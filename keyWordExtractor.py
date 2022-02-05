from nltk import tokenize
from operator import itemgetter
import math
from nltk.corpus import stopwords
from collections import defaultdict


class KeyWordExtractor:

    def __init__(self):
        self.stop_words = set(stopwords.words('english'))

    def check_sent(self, word, sentences):
        final = [all([w in x for w in word]) for x in sentences]
        sent_len = [sentences[i] for i in range(0, len(final)) if final[i]]
        return int(len(sent_len))

    def compute_tf_score(self, words):
        total_word_len = len(words)
        tf_score = defaultdict(int)
        for word in words:
            word = word.replace('.', '')
            if word not in self.stop_words:
                tf_score[word] += 1

        # Dividing by total_word_length for each dictionary element
        tf_score.update((x, y / int(total_word_len)) for x, y in tf_score.items())
        return tf_score

    def compute_idf_score(self, words, sentences):
        idf_score = {}
        total_sent_len = len(sentences)
        for word in words:
            word = word.replace('.', '')
            if word not in self.stop_words:
                if word in idf_score:
                    idf_score[word] = self.check_sent(word, sentences)
                else:
                    idf_score[word] = 1

        # Performing a log and divide
        idf_score.update((x, math.log(int(total_sent_len) / y)) for x, y in idf_score.items())
        return idf_score

    def compute_tf_idf_score(self, tf_score, idf_score):
        tf_idf_score = {key: idf_score.get(key, 0) * tf_score[key] for key in tf_score.keys()}
        result = dict(sorted(tf_idf_score.items(), key=itemgetter(1), reverse=True))
        return result

    def extract_keywords(self, text):
        words = text.split()
        sentences = tokenize.sent_tokenize(text)
        tf_score = self.compute_tf_score(words)
        idf_score = self.compute_idf_score(words, sentences)
        return self.compute_tf_idf_score(tf_score, idf_score)
