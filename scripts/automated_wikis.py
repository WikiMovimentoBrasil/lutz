#! env python
import requests

wiki = "{}wiki"
wikis = [wiki.format(lang) for lang in [
    'pt', 'es', 'fr', 'en', 'de', 'ja', 'ru', 'it', 'zh', 'fa', 'sv',
    'arz', 'pl', 'vi', 'war', 'uk', 'ca']
]

limit = '1000'

for wiki in wikis:
    r = requests.get('https://lutz.toolforge.org/recent', params={
        'limit': limit, 'wiki': wiki})
    print(f"Requested {wiki}: {r}")
    if r.status_code != 200:
        try:
            print(r.json())
        except Exception:
            print(r.text)
