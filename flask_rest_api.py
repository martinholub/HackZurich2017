#!flask/bin/python
import logging

import nltk
from flask import Flask, jsonify, abort, make_response, request
from flask_cors import CORS, cross_origin

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

app = Flask(__name__)
CORS(app)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/frindge-default/v1.0', methods=['POST'])
def frindge():
    if not request.json or not 'input' in request.json:
        abort(400)
    current_article_text = request.json['input']
    print(current_article_text)
    

    return jsonify(
        {'input': current_article_text, "frindge_score": 0.5}), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)