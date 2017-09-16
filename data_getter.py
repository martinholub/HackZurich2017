import requests, re
import xml.etree.ElementTree as ET
from requests_futures.sessions import FuturesSession

session = FuturesSession(max_workers=10)

'7ac5beb5313d4a19b623d777c4707076'

def r_auth_token():
    resp = requests.get('https://commerce.reuters.com/rmd/rest/xml/login?username=HackZurichAPI&password=8XtQb447')
    xml = ET.fromstring(resp.text)
    global auth_token
    auth_token = xml.text

r_auth_token()

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

def analyze_fut(text):
    return session.post('https://api.thomsonreuters.com/permid/calais',
        headers={'Content-Type': 'text/raw', 'outputFormat': 'application/json',
        'x-ag-access-token': 'Jz5ghWp8LbjYHL83WECGF3AUXV3Xk8Jm'}, data=text.encode('utf-8'))

def analyze_run(fut):
    resp = fut.result()
    json = resp.json()
    return {'entities': entities(json), 'tags': tags(json), 'topics': topics(json)}

def analyze(text):
    return analyze_run(analyze_fut(text))

def r_search(query):
    query_str = 'OR'.join('"{}"'.format(q) for q in query)
    resp = requests.get('https://rmb.reuters.com/rmd/rest/xml/search',
        params={'fieldsRef': 'id', 'channelCategory': 'OLR', 'limit': 15,
        'token': auth_token, 'q': 'body:' + query_str})
    xml = ET.fromstring(resp.text)
    return [r.find('id').text
        for r in xml
        if r.find('id') is not None]

def r_body_fut(id):
    return session.get('https://rmb.reuters.com/rmd/rest/xml/item', params={'token': auth_token, 'id': id})

def r_body_run(fut):
    resp = fut.result()
    xml = ET.fromstring(resp.text)
    ns = {'html': 'http://www.w3.org/1999/xhtml'}
    body = xml.find('.//html:body', ns)
    return body and re.sub('\s+', ' ', ET.tostring(body, encoding='unicode', method='text'))

def r_body(id):
    return r_body_run(r_body_fut(id))

def r_entities_fut(id):
    return session.get('https://rmb.reuters.com/rmd/rest/xml/itemEntities', params={'token': auth_token, 'id': id})

def r_entities_run(fut):
    resp = fut.result()
    xml = ET.fromstring(resp.text)
    ents = xml.findall('*/entity')
    return {'entities': {
        ent.find("*/[name='name']/value").text: float(ent.find('score').text)
        for ent in ents
        if ent.find("*/[name='name']/value") is not None
    }, 'tags': {}, 'topics': {}}

def r_entities(id):
    return r_entities_run(r_entities_fut(id))

def run(text):
    r_auth_token() #In case it timed out
    point = analyze(text)
    entities = point['entities']
    main_actors = sorted(entities, key=entities.get)[-6:]
    related_articles = r_search(main_actors)
    fut_article_bodies = (r_body_fut(id) for id in related_articles)
    article_bodies = map(r_body_run, fut_article_bodies)
    fut_environs = (analyze_fut(body) for body in article_bodies if body)
    environs = list(map(analyze_run, fut_environs))
    return {'point': point, 'environs': environs}

def fastrun(text):
    r_auth_token() #In case it timed out
    point = analyze(text)
    entities = point['entities']
    main_actors = sorted(entities, key=entities.get)[-6:]
    related_articles = r_search(main_actors)
    fut_article_entities = (r_entities_fut(id) for id in related_articles)
    environs = list(map(r_entities_run, fut_article_entities))
    return {'point': point, 'environs': environs}
