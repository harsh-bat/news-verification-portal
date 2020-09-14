from flask import Flask, request
app = Flask(__name__)
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import pickle

model = load_model('model25epo.h5')
tokenizer = None
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)


@app.route('/check', methods=['POST'])
def checkView():
	body_str = request.values.get('body')

	if int(np.round(model.predict(pad_sequences(tokenizer.texts_to_sequences([body_str]), maxlen=29286)))[0,0]) == 1:
		return "Fake"
	else:
		return "Real"

app.run(debug=True, port=5000)