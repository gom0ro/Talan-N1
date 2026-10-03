"""
Аттестация — құжатты сайт ішінде көрсетуге арналған көмекші тегтер.
"""
import urllib.parse

from django import template

register = template.Library()

GOOGLE_VIEWER_URL = 'https://docs.google.com/viewer'

# Браузер осы типтерді өзі көрсете алады — сыртқы сервис қажет емес
DIRECT_TYPES = {'pdf', 'image'}


@register.simple_tag
def doc_embed_url(doc, request):
    """
    Құжатты iframe-те көрсетуге арналған URL қайтарады.

    PDF пен сурет тікелей көрсетіледі, ал Word/Excel/PowerPoint
    үшін Google Docs Viewer қолданылады (файл міндетті түрде
    сілтеме арқылы қолжетімді болуы керек).
    """
    if not doc.file:
        return ''

    absolute_url = request.build_absolute_uri(doc.file.url)

    if doc.file_type in DIRECT_TYPES:
        return absolute_url

    query = urllib.parse.urlencode({'url': absolute_url, 'embedded': 'true'})
    return f'{GOOGLE_VIEWER_URL}?{query}'


@register.simple_tag
def doc_is_embeddable(doc):
    """Құжатты сайт ішінде көрсетуге бола ма."""
    return bool(doc.file)
