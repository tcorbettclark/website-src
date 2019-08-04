AUTHOR = 'Timothy Corbett-Clark'
SITENAME = 'Dr Timothy Corbett-Clark'
SITEURL = 'https://www.corbettclark.com'
OUTPUT_PATH = "../tcorbettclark.github.io/"
DEFAULT_LANG = 'en'
TIMEZONE = 'Europe/London'
DEFAULT_PAGINATION = False
RELATIVE_URLS = False

ADDTHIS_PROFILE = 'ra-5d3f3e0f6b76330d'
ADDTHIS_FACEBOOK_LIKE = False

FAVICON = 'img/favicon.ico'
SITELOGO = 'img/tcc1.jpg'
SITELOGO_SIZE = 36

PATH = 'content'
PAGE_PATHS = ['pages', ]
ARTICLE_PATHS = ['articles', ]
STATIC_PATHS = ['img', 'pdf', ]
PLUGIN_PATHS = ['plugins', ]
# Only publish articles and pages if explicit "Status: published"
DEFAULT_METADATA = {
    'status': 'draft',
}

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
BOOTSTRAP_THEME = 'readable'
# BOOTSTRAP_THEME = 'cerulean'
# BOOTSTRAP_THEME = 'paper'
# BOOTSTRAP_THEME = 'yeti'
PYGMENTS_STYLE = 'monokai'
TYPOGRIFY = True

MENUITEMS = [
    # ['', "/feeds/all.atom.xml", 'fa-rss']
]

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

FEED_DOMAIN = SITEURL
# FEED_ALL_ATOM = 'feeds/all.atom.xml'
# AUTHOR_FEED_ATOM = None
# TAG_FEED_ATOM = None
# CATEGORY_FEED_ATOM = None
# TRANSLATION_FEED_ATOM = None

# FEED_ALL_RSS = None
# AUTHOR_FEED_RSS = None
# TAG_FEED_RSS = None
# CATEGORY_FEED_RSS = None
# TRANSLATION_FEED_RSS = None

import os
if not os.environ.get("PUBLISH_PELICAN"):
    SITEURL = ''
    OUTPUT_PATH = 'output'