# train.py
# Run this once before starting the chatbot
# It reads intents.json, trains the model, and saves the data to data/model.pkl
# Usage: python train.py

import json
import pickle
import random
import re
import numpy as np

import nltk
from nltk.stem import PorterStemmer

# try to download punkt data, works fine when internet is available
try:
    nltk.download('punkt', quiet=True)
    nltk.download('punkt_tab', quiet=True)
except Exception:
    pass

stemmer = PorterStemmer()

# characters we want to ignore during tokenizing
IGNORE_CHARS = ['?', '!', '.', ',', ';', ':', "'", '"']


def simple_tokenize(text):
    # split on whitespace and punctuation - works without any NLTK data files
    try:
        return nltk.word_tokenize(text)
    except Exception:
        return re.findall(r"[a-zA-Z']+", text)


def load_intents(path='intents.json'):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data['intents']


def build_vocab(intents):
    all_words = []
    classes = []
    documents = []   # list of (word_tokens, tag) pairs

    for intent in intents:
        tag = intent['tag']

        if tag not in classes:
            classes.append(tag)

        for pattern in intent['patterns']:
            tokens = simple_tokenize(pattern)
            all_words.extend(tokens)
            documents.append((tokens, tag))

    # stem and clean the words
    all_words = [stemmer.stem(w.lower()) for w in all_words if w not in IGNORE_CHARS]
    all_words = sorted(list(set(all_words)))
    classes = sorted(classes)

    return all_words, classes, documents


def make_training_data(all_words, classes, documents):
    training = []
    output_empty = [0] * len(classes)

    for (tokens, tag) in documents:
        # bag of words for this pattern
        stemmed = [stemmer.stem(w.lower()) for w in tokens]
        bag = [1 if w in stemmed else 0 for w in all_words]

        # output row: 1 for the correct class, 0 for everything else
        output_row = list(output_empty)
        output_row[classes.index(tag)] = 1

        training.append([bag, output_row])

    random.shuffle(training)
    training = np.array(training, dtype=object)

    train_x = list(training[:, 0])
    train_y = list(training[:, 1])

    return train_x, train_y


def main():
    print("Loading intents.json ...")
    intents = load_intents()

    print("Building vocabulary ...")
    all_words, classes, documents = build_vocab(intents)

    print(f"  Total words in vocab : {len(all_words)}")
    print(f"  Total intent classes : {len(classes)}")
    print(f"  Total patterns       : {len(documents)}")

    print("Building training data ...")
    train_x, train_y = make_training_data(all_words, classes, documents)

    # save everything to a pickle file so chatbot.py can load it quickly
    model_data = {
        'words': all_words,
        'classes': classes,
        'train_x': train_x,
        'train_y': train_y
    }

    with open('data/model.pkl', 'wb') as f:
        pickle.dump(model_data, f)

    print("Model data saved to data/model.pkl")
    print("Training complete. You can now run: streamlit run app.py")


if __name__ == '__main__':
    main()
