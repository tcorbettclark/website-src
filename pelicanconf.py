AUTHOR = 'Timothy Corbett-Clark'
SITENAME = 'Timothy Corbett-Clark'
SITEURL = ''

PATH = 'content'
PAGE_PATHS = ['pages', ]
ARTICLE_PATHS = ['articles', ]
STATIC_PATHS = ['img', 'pdf', ]
PLUGIN_PATHS = ['plugins', ]

OUTPUT_PATH = 'output'

ARTICLE_URL = 'articles/{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = 'articles/{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'
PAGE_URL = 'pages/{slug}/'
PAGE_SAVE_AS = 'pages/{slug}/index.html'
CATEGORY_URL = 'category/{slug}'
CATEGORY_SAVE_AS = 'category/{slug}/index.html'
TAG_URL = 'tag/{slug}'
TAG_SAVE_AS = 'tag/{slug}/index.html'

THEME = 'themes/pelican-bootstrap3'
PLUGINS = ['i18n_subsites', ]

JINJA_ENVIRONMENT = {
    'extensions': ['jinja2.ext.i18n'],
}

BOOTSTRAP_THEME = 'cerulean'
# BOOTSTRAP_THEME = 'paper'
# BOOTSTRAP_THEME = 'yeti'

PYGMENTS_STYLE = 'monokai'

DEFAULT_LANG = 'en'
TIMEZONE = 'Europe/London'

LINKS = (
    ('Cmed', 'https://www.cmedresearch.com'),
    ('Encapsia', 'https://www.encapsia.com'),
)

SOCIAL = (
    ('Twitter', 'https://twitter.com/tcorbettclark'),
    ('Github', 'https://github.com/tcorbettclark'),
    ('LinkedIn', 'https://www.linkedin.com/in/tcorbettclark'),
    ('Quora', 'https://www.quora.com/profile/Timothy-Corbett-Clark'),
)

# Only publish articles and pages if explicit "Status: published"
DEFAULT_METADATA = {
    'status': 'draft',
}

DEFAULT_PAGINATION = False
RELATIVE_URLS = False

# No feeds during development
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

import os
if os.environ.get("PUBLISH_PELICAN"):
    SITEURL = 'https://www.corbettclark.com'
    OUTPUT_PATH = "../tcorbettclark.github.io/"

    FEED_ALL_ATOM = 'feeds/all.atom.xml'
    CATEGORY_FEED_ATOM = 'feeds/{slug}.atom.xml'

    # DISQUS_SITENAME = ""
    # GOOGLE_ANALYTICS = ""
