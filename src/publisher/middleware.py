import json
from collections import OrderedDict
from django.conf import settings
import logging
from .utils import lmap

LOG = logging.getLogger(__name__)

# temporarily borrowed from bot-lax-adaptor...
def visit(data, pred, fn, coll=None):
    "visits every value in the given data and applies `fn` when `pred` is true "
    if pred(data):
        if coll is not None:
            data = fn(data, coll)
        else:
            data = fn(data)
        # why don't we return here after matching?
        # the match may contain matches within child elements (lists, dicts)
        # we want to visit them, too
    if isinstance(data, OrderedDict):
        results = OrderedDict()
        for key, val in data.items():
            results[key] = visit(val, pred, fn, coll)
        return results
    elif isinstance(data, dict):
        return {key: visit(val, pred, fn, coll) for key, val in data.items()}
    elif isinstance(data, list):
        return [visit(row, pred, fn, coll) for row in data]
    # unsupported type/no further matches
    return data

def downgrade(content):
    "returns v1-compliant content"

    def pred(element):
        return True

    def fn(element):
        return element

    return visit(content, pred, fn)

def upgrade(content):
    "returns v2-compliant content"

    def pred(element):
        if isinstance(element, dict):
            return 'additionalFiles' in element or element.get('type') == 'figure'

    def doit(item):
        if not 'label' in item:
            item['label'] = item['title']
        return item

    def fn(element):
        for target in ['additionalFiles', 'assets']:
            if target in element:
                element[target] = lmap(doit, element[target])
        return element

    return visit(content, pred, fn)

TRANSFORMS = {
    '1': downgrade,
    '2': upgrade,
    '*': upgrade, # accept ll: */*
}

def transformable(response):
    "exclude everything but api requests"
    if settings.API_V12_TRANSFORMS:
        # target any response of content type:
        # * application/vnd.elife.article-poa+json
        # * application/vnd.elife.article-vor+json
        target = ['application/vnd.elife.article-poa+json',
                  'application/vnd.elife.article-vor+json']
        return getattr(response, 'content_type', False) and \
            response.content_type.split(';')[0] in target

# adapted from https://djangosnippets.org/snippets/1042/
def parse_accept_header(accept):
    "returns a list of triples, (media, key, val)"
    result = []
    for media_range in accept.split(","):
        parts = media_range.split(";")
        media_type = parts.pop(0).strip().lower()
        for part in parts:
            key, val = part.lstrip().split("=", 1)
            result.append((media_type, key, val))
    return result

def requested_version(request):
    "figures out which content version was requested. "
    targets = [
        'application/vnd.elife.article-poa+json',
        'application/vnd.elife.article-vor+json',
    ]
    bits = parse_accept_header(request.META.get('HTTP_ACCEPT', '*/*'))
    bits.sort(key=lambda row: row[-1], reverse=True) # sorts rows by parameter values, highest first
    for row in bits:
        if row[0] in targets:
            return row[-1][0] # last element, last character
    return '*'

def deprecated(request):
    targets = [
        ('application/vnd.elife.article-poa+json', 'version', '1'),
        ('application/vnd.elife.article-vor+json', 'version', '1'),
    ]
    accepts = parse_accept_header(request.META.get('HTTP_ACCEPT', '*/*'))
    for target in targets:
        if target in accepts:
            return True

#
# middleware
#

def apiv12transform(get_response_fn):
    def middleware(request):
        response = get_response_fn(request)
        if transformable(response):
            version = requested_version(request)
            if version in TRANSFORMS:
                content = json.loads(response.content.decode('utf-8'))
                response.content = bytes(json.dumps(TRANSFORMS[version](content), ensure_ascii=False), 'utf-8')
        return response
    return middleware

def apiv1_deprecated(get_response_fn):
    def middleware(request):
        response = get_response_fn(request)
        if deprecated(request):
            response['warning'] = "Deprecation: Support for version 1 will be removed"
        return response
    return middleware
