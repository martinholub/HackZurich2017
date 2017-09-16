import requests
import xml.etree.ElementTree as ET

def topics(json):
    return {v['name']: v.get('score', 0)
        for v in json.values()
        if v.get('_typeGroup', '') == 'topics'}

def tags(json):
    return {v['name']: 1 / float(v.get('importance', '10'))
        for v in json.values()
        if v.get('_typeGroup', '') == 'socialTag'}

def entities(json):
    return {v['name']: v.get('relevance')
        for v in json.values()
        if v.get('_typeGroup', '') == 'entities'
        and v.get('forenduserdisplay', '') == 'true'}

def analyze(text):
    resp = requests.post('https://api.thomsonreuters.com/permid/calais',
        headers={'Content-Type': 'text/raw', 'outputFormat': 'application/json',
        'x-ag-access-token': 'Jz5ghWp8LbjYHL83WECGF3AUXV3Xk8Jm'}, data=text.encode('utf-8'))
    json = resp.json()
    return {'entities': entities(json), 'tags': tags(json), 'topics': topics(json)}

def r_auth_token():
    resp = requests.get('https://commerce.reuters.com/rmd/rest/xml/login?username=HackZurichAPI&password=8XtQb447')
    xml = ET.fromstring(resp.text)
    global auth_token
    auth_token = xml.text

r_auth_token()

def r_search(query):
    query_str = 'OR'.join('"{}"'.format(q) for q in query)
    resp = requests.get('https://rmb.reuters.com/rmd/rest/xml/search',
        params={'fieldsRef': 'id', 'token': auth_token, 'q': 'body:' + query_str})
    xml = ET.fromstring(resp.text)
    return [r.find('id').text
        for r in xml
        if r.find('id') is not None]

def r_body(id):
    resp = requests.get('https://rmb.reuters.com/rmd/rest/xml/item', params={'token': auth_token, 'id': id})
    xml = ET.fromstring(resp.text)
    ns = {'html': 'http://www.w3.org/1999/xhtml'}
    body = xml.find('.//html:body', ns)
    return body and ET.tostring(body, encoding='unicode', method='text')

def run(text):
    point = analyze(text)
    entities = point['entities']
    main_actors = sorted(entities, key=entities.get)[-4:]
    related_articles = r_search(main_actors)
    article_bodies = [r_body(id) for id in related_articles]
    environs = [analyze(body) for body in article_bodies if body]
    return {'point': point, 'environs': environs}
