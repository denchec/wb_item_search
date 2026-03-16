import datetime

import requests

def get_items_from_search(search_text: str):
    url = 'https://www.wildberries.ru/__internal/u-search/exactmatch/ru/common/v18/search'
    params = {
        'ab_intent_search': 'hml',
        'appType': 1,
        'curr': 'rub',
        'dest': -1257786,
        'f14177451': 15000203,
        'hide_vflags': 4294967296,
        'inheritFilters': False,
        'lang': 'ru',
        'priceU': '100;1000000',
        'query': search_text,
        'resultset': 'catalog',
        'sort': 'popular',
        'spp': 30,
        'suppressSpellcheck': False,
        'page': 1
    }

    headers = {
        'cookie': 'x_wbaas_token=1.1000.404e111fdb4742f1bde2e265a4e76d61.MHwxODguMzIuMTkuMTQ1fE1vemlsbGEvNS4wIChXaW5kb3dzIE5UIDEwLjA7IFdpbjY0OyB4NjQpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS8xNDMuMC4wLjAgU2FmYXJpLzUzNy4zNiBPUFIvMTI3LjAuMC4wIChFZGl0aW9uIFl4IEdYKXwxNzc0NTM1MjkyfHJldXNhYmxlfDJ8ZXlKb1lYTm9Jam9pSW4wPXwwfDN8MTc3MzkzMDQ5Mnwx.MEQCID2oKBwZcX93f8mWzbh9Ou7Mj6kbUe4sGkzuEV2Zk5W3AiBha28lOekQtqUqpRJslBx8ixlYa15oQ/5lmWi1R7cG1Q==',
        'referer': 'https://www.wildberries.ru/catalog/0/search.aspx?',
        'x-userid': '0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 OPR/127.0.0.0 (Edition Yx GX)',
        'deviceid': 'site_1bba4b2b7af64675aa53a4734865c391',
    }

    products = []
    while True:
        response = requests.get(url=url, params=params, headers=headers)

        products.extend(response.json()['products'])

        if len(response.json()['products']) < 100:
            break

        params['page'] += 1

    return products


def get_basket_info():
    t = str(round(datetime.datetime.now().timestamp(), 3)).replace('.', '')
    url = f'https://cdn.wbbasket.ru/api/v3/upstreams?t={t}'

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 OPR/127.0.0.0 (Edition Yx GX)',
    }

    response = requests.get(url, headers=headers)

    return response.json()
