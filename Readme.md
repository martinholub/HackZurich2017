# HackZurich2017

Repository housing a chrome extension demo developed at [HackZurich2017](www.hackzurich.com). The extension wraps a python script that can be used to analyze text from a news article to determine its _fringiness_ (measure of non-meanstreamness). This is done by comparing the _entites_ extracted from the article by [PermID](https://permid.org/) against entities in real-time stream of articles fetched via Thomson Reuters &reg; [API](https://developers.thomsonreuters.com/all/api-families). 

### Example Usage
```python
text = <few-paragraphs-of-news-text>
res = fastrun(text)

x, y, f = fringiness(res_to_matrix(res_times)[0])
plot = embedding_plot_bokeh(x, y, f, res)

from bokeh.resources import CDN
html = file_html(plot, CDN, title = "my plot")
with open("file.html", "w") as file:
    file.write(html)
```
_See also the [Jupyter Notebook](https://github.com/martinholub/HackZurich2017/blob/master/Hackzurich.ipynb)_ 

-----
### Team Members:
- Nikola Nikolov
- Daniel Keller
- Stan Kerstjens
- [Martin Holub](mailto:martin-holub@outlook.com)

------

Get the word vectors here https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit and change the path in document_similarity.py 


You need the gensim and NLTK libraries: `pip install gensim nltk`
