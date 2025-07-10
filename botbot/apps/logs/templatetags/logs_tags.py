"""Near duplicate of Django's `urlizetrunc` with support for image classes"""

from django.template.base import Node
from django.template.library import Library
from django.template.defaultfilters import stringfilter, urlizetrunc
from django.utils.functional import keep_lazy_text
from django.utils.safestring import mark_safe


register = Library()

@register.filter(is_safe=True, needs_autoescape=True)
@stringfilter
def bbme_urlizetrunc(value, limit, autoescape=None):
    """
    Converts URLs into clickable links, truncating URLs to the given character
    limit, and adding 'rel=nofollow' attribute to discourage spamming.

    Argument: Length to truncate URLs to.
    """
    return mark_safe(urlizetrunc(
        value, trim_url_limit=int(limit), nofollow=True, autoescape=autoescape
    ))
bbme_urlizetrunc = keep_lazy_text(bbme_urlizetrunc)

def strip_empty_lines(block):
    return '\n'.join(
        [l.strip() for l in block.splitlines() if l.strip()]).strip()
strip_empty_lines = keep_lazy_text(strip_empty_lines)

class WhiteLinelessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        return strip_empty_lines(self.nodelist.render(context))

@register.tag
def whitelineless(parser, token):
    nodelist = parser.parse(('endwhitelineless',))
    parser.delete_first_token()
    return WhiteLinelessNode(nodelist)
