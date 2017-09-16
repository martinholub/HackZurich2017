#!flask/bin/python
import logging

from bokeh.plotting import figure
from bokeh.resources import CDN
from bokeh.embed import file_html, components
from flask import Flask, jsonify, abort, make_response, request
from flask_cors import CORS, cross_origin
from fringiness import *
from data_getter import * 
import traceback

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

app = Flask(__name__)
CORS(app)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


"""@app.route('/fringe-default/v1.0', methods=['POST'])
def frindge():
    if not request.json or not 'input' in request.json:
        abort(400)
    current_article_text = request.json['input']
    logging.info(current_article_text)
    
    res = run(current_article_text)
    logging.info(res)
    x, y, f = fringiness(res_to_matrix(res))
    logging.info(f)
    
    try: 
        f_input_score = f[0]
    except: 
        f_input_score = -1.
    
    return jsonify(
        {'input': current_article_text, "fringe_score": f_input_score}), 201
"""


@app.route('/fringe-plots/v1.0', methods=['POST'])
def frindge():
    if not request.json or not 'input' in request.json:
        abort(400)
    current_article_text = request.json['input']
    logging.info(current_article_text)
    
    res = fastrun(current_article_text)
    logging.info(res)
    try:
        x, y, f = fringiness(res_to_matrix(res)[0])
    except Exception as e:
        traceback.print_exc()
        return jsonify({"fringe_score": str(e)}), 200
    logging.info(f)
    
    plot = embedding_plot_bokeh(x, y, f, res)
    histogram = histogram_bokeh(f)
    
    plot_html = components(plot, wrap_script=False, wrap_plot_info=False)
    histogram_html = ''
    #histogram_html = file_html(plot, CDN, "Scatter")
    #s = open("scatter.html", "w")
    #s.write(plot_html)
    #s.close
    
    #h = open("scatter.html", "w")
    #h.write(histogram_html)
    #h.close
    
    try: 
        f_input_score = f[0]
    except: 
        f_input_score = -1.
    
    return jsonify(
        {'input': current_article_text, "fringe_score": f_input_score, "scatter_html": plot_html, 
         "histogram_html":histogram_html}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)