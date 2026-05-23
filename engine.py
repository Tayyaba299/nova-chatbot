import json
import os
import pickle
import random
import re

import numpy as np
from nltk.stem import PorterStemmer

try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except Exception:
    pass

_stemmer = PorterStemmer()

PUNCT = set('?!.,;:\'"')
MATCH_THRESHOLD = 0.45

# Roman Urdu markers — one word is enough to trigger Urdu responses
_URDU_MARKERS = {
    'hai', 'hain', 'kya', 'kab', 'kitni', 'kitna', 'mein', 'ka', 'ki', 'ko',
    'se', 'chahiye', 'batao', 'bata', 'hoga', 'hogi', 'karein', 'karo',
    'aur', 'nahi', 'nahin', 'shukriya', 'assalam', 'salam', 'jazak',
    'khuda', 'alvida', 'daakhla', 'ustad', 'ap', 'aap', 'tum', 'hum',
    'yeh', 'woh', 'iska', 'unka', 'apna', 'mujhe', 'mera', 'teri',
    'zaruri', 'zaroor', 'accha', 'theek', 'bohot', 'bahut', 'sirf',
    'pehle', 'baad', 'abhi', 'kb', 'kahan', 'kon', 'kaun', 'kaise',
}


def _tokenize(text: str) -> list:
    try:
        return nltk.word_tokenize(text)
    except Exception:
        return re.findall(r"[a-zA-Z']+", text)


def _stem(word: str) -> str:
    return _stemmer.stem(word.lower())


def is_urdu(text: str) -> bool:
    words = re.findall(r'[a-zA-Z]+', text.lower())
    return any(w in _URDU_MARKERS for w in words)


def build_vocab(intents: list) -> tuple:
    all_words, classes, docs = [], [], []

    for intent in intents:
        tag = intent['tag']
        if tag not in classes:
            classes.append(tag)
        for pattern in intent['patterns']:
            tokens = _tokenize(pattern)
            all_words.extend(tokens)
            docs.append((tokens, tag))

    vocab = sorted({_stem(w) for w in all_words if w not in PUNCT})
    return vocab, sorted(classes), docs


def build_training_arrays(all_words: list, classes: list, docs: list) -> tuple:
    empty = [0] * len(classes)
    rows = []

    for tokens, tag in docs:
        stemmed = {_stem(w) for w in tokens}
        bag     = [1 if w in stemmed else 0 for w in all_words]
        label   = list(empty)
        label[classes.index(tag)] = 1
        rows.append([bag, label])

    random.shuffle(rows)
    arr = np.array(rows, dtype=object)
    return list(arr[:, 0]), list(arr[:, 1])


class ChatbotEngine:

    def __init__(self, intents_path=None, model_path=None):
        base = os.path.dirname(os.path.abspath(__file__))
        self.intents_path = intents_path or os.path.join(base, 'intents.json')
        self.model_path   = model_path   or os.path.join(base, 'data', 'model.pkl')

        with open(self.intents_path, encoding='utf-8') as f:
            self.intents = json.load(f)['intents']

        if self._stale():
            self._train()

        with open(self.model_path, 'rb') as f:
            saved = pickle.load(f)

        self.words   = saved['words']
        self.classes = saved['classes']

    def _stale(self) -> bool:
        if not os.path.exists(self.model_path):
            return True
        return os.path.getmtime(self.intents_path) > os.path.getmtime(self.model_path)

    def _train(self):
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        words, classes, docs = build_vocab(self.intents)
        train_x, train_y    = build_training_arrays(words, classes, docs)
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'words':   words,
                'classes': classes,
                'train_x': train_x,
                'train_y': train_y,
            }, f)

    def _bow(self, text: str) -> np.ndarray:
        stemmed = {_stem(w) for w in re.findall(r"[a-zA-Z']+", text.lower())}
        return np.array([1.0 if w in stemmed else 0.0 for w in self.words])

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        denom = np.linalg.norm(a) * np.linalg.norm(b)
        return float(np.dot(a, b) / denom) if denom else 0.0

    def _match(self, text: str) -> str:
        qv = self._bow(text)
        best_tag, best_score = 'fallback', 0.0

        for intent in self.intents:
            if not intent['patterns']:
                continue
            score = max(self._cosine(qv, self._bow(p)) for p in intent['patterns'])
            if score > best_score:
                best_tag, best_score = intent['tag'], score

        return best_tag if best_score >= MATCH_THRESHOLD else 'fallback'

    def get_response(self, text: str) -> str:
        text = text.strip()
        if not text:
            return "Please type a question."

        tag   = self._match(text)
        urdu  = is_urdu(text)

        for intent in self.intents:
            if intent['tag'] != tag:
                continue
            if urdu and intent.get('responses_ur'):
                return random.choice(intent['responses_ur'])
            return random.choice(intent.get('responses_en', []))

        return "Sorry, please contact admin: 0629-2880012"
