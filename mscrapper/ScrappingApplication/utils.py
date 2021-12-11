import re


def remove_duplicates(lst):
    return list(dict.fromkeys(lst))


def clean(lst_or_str, join=False, dedupe=False):
    clean_r = re.compile(r'\s+')
    _clean = lambda s: clean_r.sub(' ', s)

    if isinstance(lst_or_str, list):
        lst_or_str = [_clean(str).strip() for str in lst_or_str if str and _clean(str or '').strip()]

        if dedupe:
            lst_or_str = remove_duplicates(lst_or_str)

        lst_or_str = ' '.join(lst_or_str) if join else lst_or_str
    else:
        lst_or_str = _clean(lst_or_str or '').strip()

    return lst_or_str


def next_request_or_item(item):
    if not item.get('meta', {}).get('requests_queue'):
        item.pop('meta', None)
        return item

    request = item['meta']['requests_queue'].pop()
    request.meta.setdefault('item', item)
    request.priority += 1
    return [request]
