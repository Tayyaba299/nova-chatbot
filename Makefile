.PHONY: install train run

install:
	pip install -r requirements.txt

train:
	python train.py

run:
	python streamlit run app.py
