#!/usr/bin/env python3
"""
Rebuild data/model.pkl from intents.json.

Run once after cloning, or again whenever intents.json changes:
    python train.py
"""
import json
import os
import pickle
import sys

from engine import build_vocab, build_training_arrays


def main():
    base         = os.path.dirname(os.path.abspath(__file__))
    intents_path = os.path.join(base, 'intents.json')
    model_path   = os.path.join(base, 'data', 'model.pkl')

    if not os.path.exists(intents_path):
        sys.exit(f"Error: {intents_path} not found")

    print("Reading intents.json ...")
    with open(intents_path, encoding='utf-8') as f:
        intents = json.load(f)['intents']

    words, classes, docs = build_vocab(intents)
    print(f"  vocab: {len(words)} words  |  intents: {len(classes)}  |  patterns: {len(docs)}")

    train_x, train_y = build_training_arrays(words, classes, docs)

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    with open(model_path, 'wb') as f:
        pickle.dump({
            'words':   words,
            'classes': classes,
            'train_x': train_x,
            'train_y': train_y,
        }, f)

    print(f"Saved → {model_path}")
    print("Done. Run: streamlit run app.py")


if __name__ == '__main__':
    main()
