from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from django.utils.timezone import now

from jinja2 import Environment

from .apps.bots.utils import reverse_channel
from .apps.logs.templatetags.logs_tags import bbme_urlizetrunc
from .apps.plugins.utils import plugin_docs_as_html


def get_bootstrap_input_type(field):
    """Get the appropriate input type for a form field."""
    from django import forms
    if isinstance(field.field, forms.BooleanField):
        return 'checkbox'
    elif isinstance(field.field, forms.FileField):
        return 'file'
    return 'text'

def environment(**options):
    # Enable autoescape by default for security
    if 'autoescape' not in options:
        from jinja2 import select_autoescape
        options['autoescape'] = select_autoescape(['html', 'xml', 'htm'])

    # Set default extensions if not provided
    if 'extensions' not in options:
        options['extensions'] = [
            'pipeline.jinja2.PipelineExtension',
            'django_jinja.builtins.extensions.CacheExtension',
        ]

    # Create the environment
    env = Environment(**options)

    # Add i18n support
    from django.utils.translation import get_language
    from django.utils.translation import gettext as _
    from django.utils.translation import ngettext as n_

    # Add global variables
    env.globals.update({
        'gettext': _,
        'ngettext': n_,
        'LANGUAGE_CODE': get_language(),
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
        # bootstrap3
        'bootstrap_input_type': get_bootstrap_input_type,
    })
    return env
