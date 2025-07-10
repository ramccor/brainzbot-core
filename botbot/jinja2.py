from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext

from jinja2 import Environment

from .apps.bots.utils import reverse_channel
from .apps.logs.templatetags.logs_tags import bbme_urlizetrunc
from .apps.plugins.utils import plugin_docs_as_html

from bootstrap_toolkit.templatetags.bootstrap_toolkit import bootstrap_input_type


def environment(**options):
    options['extensions'] = [
        "jinja2.ext.autoescape",
        "jinja2.ext.with_",
        "jinja2.ext.i18n",
        'pipeline.jinja2.PipelineExtension',
        'django_jinja.builtins.extensions.CacheExtension',
    ]
    env = Environment(**options)
    env.globals.update({
        'gettext': gettext,
        # django
        'static': staticfiles_storage.url,
        'url': reverse,
        'now': now,
        # bots
        'channel_url': reverse_channel,
        # logs
        'bbme_urlizetrunc': bbme_urlizetrunc,
        # plugins
        'plugin_docs': plugin_docs_as_html,

        # bootstrap_toolkit
        'bootstrap_input_type': bootstrap_input_type,
    })
    return env
