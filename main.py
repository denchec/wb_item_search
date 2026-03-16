from openpyxl import Workbook
import asyncio
import aiohttp

from wb_requests import get_basket_info, get_items_from_search


def filter_by_rating(items):
    products = []
    for item in items:
        rating = item['nmReviewRating']
        if rating < 4.5:
            continue

        products.append(item)

    return products


def get_basket():
    data = get_basket_info()

    baskets = {}
    for info in data['origin']['mediabasket_route_map']:
        for h in info['hosts']:
            baskets[f"{h['vol_range_from']}-{h['vol_range_to']}"] = h['host']

    return baskets


async def fetch_json(
        session: aiohttp.ClientSession,
        url: str,
        semaphore: asyncio.Semaphore
):
    async with semaphore:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
            response.raise_for_status()
            return await response.json()


async def fetch_all(urls: list[str], concurrency: int):
    semaphore = asyncio.Semaphore(concurrency)

    connector = aiohttp.TCPConnector(limit=concurrency)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch_json(session, url, semaphore) for url in urls]
        return await asyncio.gather(*tasks)


async def get_item_detail(items):
    urls = []
    for item in items:
        article = str(item['id'])
        urls.append(f'https://{item['basket']}/vol{article[:-5]}/part{article[:-3]}/{article}/info/ru/card.json')

    results = await fetch_all(urls, concurrency=10)

    return results


def get_all_options(items, items_detail):
    options = []
    for item in items:
        article = item['id']

        for option in items_detail[article]['options']:
            option_name = option['name']

            if option_name not in options:
                options.append(option_name)

    return options


def get_item_options(item_options, all_options):
    _options = {}
    for a_option in item_options:
        name = a_option['name']
        value = a_option['value']
        _options[name] = value

    results = []
    for o in all_options:
        if o in _options:
            results.append(_options[o])
            continue

        results.append('')

    return results


def sum_item_info(items, details):
    items_detail = {info['nm_id']: info for info in details}
    options = get_all_options(items, items_detail)

    results = []
    for item in items:
        article = item['id']
        brand_url = f'{item['brandId']}-{item["brand"].lower().replace(" ", "-")}'
        media = [
            f'https://{item["basket"]}/vol{str(article)[:-5]}/part{str(article)[:-3]}/{article}/images/big/{i}.webp'
            for i in range(1, items_detail[article]['media']['photo_count'] + 1)
        ]

        item_info = []
        item_info.extend([
            f'https://www.wildberries.ru/catalog/{article}/detail.aspx',
            article,
            item['name'],
            item['brand'],
            f'https://www.wildberries.ru/brands/{brand_url}',
            item['sizes'][0]['price']['product'] / 100,
            items_detail[article].get('description', ''),
            ','.join(media),
        ])

        size = [size['origName'] for size in item['sizes']]
        item_info.extend([
            ','.join(size),
            item['totalQuantity'],
            item['reviewRating'],
            item['feedbacks'],
        ])

        item_info.extend(get_item_options(items_detail[article]['options'], options))

        results.append(item_info)

    return results, options


def get_info(items):
    baskets = get_basket()

    for b_range, b in baskets.items():
        for item in items:
            vol = str(item['id'])[:-5]
            b_vol = b_range.split('-')

            if int(b_vol[0]) > int(vol) or int(b_vol[1]) < int(vol):
                continue

            item['basket'] = b

    items_detail = asyncio.run(get_item_detail(items))

    return sum_item_info(items, items_detail)


def write_in_file(items, option_headers):
    wb = Workbook()
    ws = wb.active

    headers = [
        'Ссылка на товар', 'Артикул', 'Название', 'Цена', 'Описание', 'Ссылки на изображения',
        *option_headers, 'Название селлера', 'Ссылка на селлера', 'Размеры товара',
        'Остатки по товару', 'Рейтинг', 'Количество отзывов'
    ]
    ws.append(headers)

    for item in items:
        ws.append(item)

    wb.save('wb_item_info.xlsx')


def main():
    search_text = "пальто из натуральной шерсти"
    items = get_items_from_search(search_text)
    items = filter_by_rating(items)
    items, option_headers = get_info(items)
    write_in_file(items, option_headers)


if __name__ == "__main__":
    main()
