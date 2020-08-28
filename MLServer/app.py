from flask import Flask, request
app = Flask(__name__)
import os, json, re
import numpy as np
import pandas as pd
import gensim
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from keras.models import model_from_json

stop_words = set(stopwords.words('english'))
gmodel = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary = True, limit=250000) 


def vectCalc(text):
    a = [word.lower() for word in word_tokenize(text) if word.isalpha()]
    b = np.array([gmodel[w] for w in a if w in gmodel and w not in stop_words])
    if len(b)>0:
        return np.mean(b, axis=0).reshape(1,300)
    else:
        return np.zeros(300).reshape(1,300)



@app.route('/check', methods=['POST'])
def checkView():
	headline = request.values.get('headline')
	body = request.values.get('body')
	headline = vectCalc(headline)
	body = vectCalc(body)
	
	json_headline_file = open('headlineModel.json', 'r')
	loaded_headline_model_json = json_headline_file.read()
	json_headline_file.close()
	loaded_headline_model = model_from_json(loaded_headline_model_json)
	loaded_headline_model.load_weights("headlineModel.h5")

	json_body_file = open('bodyModel.json', 'r')
	loaded_body_model_json = json_body_file.read()
	json_body_file.close()
	loaded_body_model = model_from_json(loaded_body_model_json)
	loaded_body_model.load_weights("bodyModel.h5")

	a = loaded_headline_model.predict(headline)
	b = loaded_body_model.predict(body)

	if a>0.65 and b>0.65:
		return "Fake"
	else:
		return "Real"
	return str(a)+str(b)


app.run(debug=True, port=5000)