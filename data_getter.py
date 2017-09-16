import requests

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
