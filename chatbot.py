# chatbot.py
# Nova - Core Engine
# Language detection added - auto picks Urdu or English response

import json
import pickle
import random
import re
import os
import time

import numpy as np
from nltk.stem import PorterStemmer

try:
    import nltk
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except Exception:
    pass

stemmer = PorterStemmer()
IGNORE_CHARS = list('?!.,;:"\'')
CONFIDENCE_THRESHOLD = 0.45

# common Roman Urdu words - if user types these, respond in Urdu
URDU_MARKERS = {
    'hai', 'hain', 'kya', 'kab', 'kitni', 'kitna', 'mein', 'ka', 'ki', 'ko',
    'se', 'chahiye', 'batao', 'bata', 'hoga', 'hogi', 'karein', 'karo',
    'aur', 'nahi', 'nahin', 'shukriya', 'assalam', 'salam', 'jazak',
    'khuda', 'alvida', 'daakhla', 'ustad', 'ap', 'aap', 'tum', 'hum',
    'yeh', 'woh', 'iska', 'unka', 'apna', 'mujhe', 'mera', 'teri',
    'zaruri', 'zaroor', 'accha', 'theek', 'bohot', 'bahut', 'sirf',
    'pehle', 'baad', 'abhi', 'kb', 'kahan', 'kon', 'kaun', 'kaise'
}


def detect_language(text):
    words = re.findall(r'[a-zA-Z]+', text.lower())
    urdu_count = sum(1 for w in words if w in URDU_MARKERS)
    # if 1 or more Urdu marker words found -> use Urdu response
    return 'ur' if urdu_count >= 1 else 'en'


def simple_tokenize(text):
    try:
        import nltk
        return nltk.word_tokenize(text)
    except Exception:
        return re.findall(r"[a-zA-Z']+", text)


class ChatbotEngine:

    def __init__(self, intents_path=None, model_path=None):
        # Use absolute paths based on this file's location
        # This ensures the app works from any working directory (e.g. Streamlit Cloud)
        _base = os.path.dirname(os.path.abspath(__file__))
        if intents_path is None:
            intents_path = os.path.join(_base, 'intents.json')
        if model_path is None:
            model_path = os.path.join(_base, 'data', 'model.pkl')
        self.intents_path = intents_path
        self.model_path   = model_path
        self.intents      = []
        self.words        = []
        self.classes      = []

        self._load_intents()
        self._load_model()

    def _load_intents(self):
        with open(self.intents_path, 'r', encoding='utf-8') as f:
            self.intents = json.load(f)['intents']

    def _needs_retrain(self):
        if not os.path.exists(self.model_path):
            return True
        # retrain if intents.json is newer than model.pkl
        return os.path.getmtime(self.intents_path) > os.path.getmtime(self.model_path)

    def _load_model(self):
        if self._needs_retrain():
            self._train()
        with open(self.model_path, 'rb') as f:
            md = pickle.load(f)
        self.words   = md['words']
        self.classes = md['classes']

    def _train(self):
        os.makedirs(os.path.dirname(self.model_path) or '.', exist_ok=True)
        all_words, classes, documents = [], [], []
        for intent in self.intents:
            tag = intent['tag']
            if tag not in classes:
                classes.append(tag)
            for p in intent['patterns']:
                tokens = re.findall(r"[a-zA-Z']+", p)
                all_words.extend(tokens)
                documents.append((tokens, tag))

        all_words = sorted(set(
            stemmer.stem(w.lower()) for w in all_words if w not in IGNORE_CHARS
        ))
        classes = sorted(classes)

        training = []
        empty = [0] * len(classes)
        for tokens, tag in documents:
            stemmed = [stemmer.stem(w.lower()) for w in tokens]
            bag = [1 if w in stemmed else 0 for w in all_words]
            row = list(empty)
            row[classes.index(tag)] = 1
            training.append([bag, row])

        random.shuffle(training)
        arr = np.array(training, dtype=object)

        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'words':   all_words,
                'classes': classes,
                'train_x': list(arr[:, 0]),
                'train_y': list(arr[:, 1])
            }, f)

    def _bow(self, text):
        tokens  = re.findall(r"[a-zA-Z']+", text.lower())
        stemmed = [stemmer.stem(w) for w in tokens]
        return np.array([1 if w in stemmed else 0 for w in self.words], dtype=float)

    def _cosine(self, a, b):
        n = np.dot(a, b)
        d = np.linalg.norm(a) * np.linalg.norm(b)
        return float(n / d) if d else 0.0

    def _classify(self, text):
        qv = self._bow(text)
        scores = []
        for intent in self.intents:
            if not intent['patterns']:
                continue
            best = max(self._cosine(qv, self._bow(p)) for p in intent['patterns'])
            scores.append((intent['tag'], best))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def get_response(self, user_text):
        if not user_text.strip():
            return "Please type a question."

        lang    = detect_language(user_text)
        results = self._classify(user_text)

        if results and results[0][1] >= CONFIDENCE_THRESHOLD:
            tag = results[0][0]
        else:
            tag = 'fallback'

        for intent in self.intents:
            if intent['tag'] == tag:
                # pick language-specific responses if available
                if lang == 'ur' and intent.get('responses_ur'):
                    return random.choice(intent['responses_ur'])
                return random.choice(intent['responses_en'])

        return "Sorry, please contact admin: 0629-2880012"