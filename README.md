# README

My home page is built using a simple home grown static site generator.

To update content, rebuild, and deploy:
```
  uv run python main.py
  ...view / review on locally served site
  ...make changes and tool will reload
  ...update git repo and push to github
```

The key features of my approach are:

* Just code i.e. not another static site generator library! (see https://jamstack.org/generators/ ...)
* Support writing and maintaining pages of content. No blog posts, tags, articles, Atom or RSS feeds etc.
* All web artifacts are kept together in one directory tree.
* Markdown rendered to HTML, and then everything rendered with Jinja2
* TODO Automatic generation of sitemap (both HTML and xml file) from the content (for SEO).
* Hot reloading localhost server, which rebuilds on change before signalling to browser(s) to reload.

The build process works as follows:

1 Clone the content directory into a new output directory.
1 Using only the output directory
1.1 Convert each markdown file (`*.md`) to an HTML (`*.html`) file of same name, optionally applying Jinja2 template specified in the frontmatter.
1.1 Apply Jinja2 templates to all HTML files which do not start with an underscore, and render back in place.
1.1 Delete all working files and directories (anything with a leading underscore in the path segment).

The end result is a clean output directory ready for deployment.

Every build is a clean build. No caching as plenty faster enough without complexity penalty or subtle gotchas.

About half of the code is about logging.


# TODO - content

* skills
* now page
* tools
* this website - and link from here
  * explain how I chose colour palette
* Find a link to the PDF for my "Choosing an appropriate model for novelty detection" paper.
  See https://ieeexplore.ieee.org/document/607503
* My computer setup


# TODO - technical

* Use the W3C Validator
* See if it is easy/possible to preserve correct indentation using Jinja, even after includes and extends.
* Remake favicon.ico
* Safari is looking for /apple-touch-icon-precomposed.png and /apple-touch-icon.png
* Add Google analytics
* Add a sitemap.xml and update robots.txt file
  See https://thatware.co/xml-sitemap-creation-python/
  See https://michael-lisboa.medium.com/automate-your-sitemap-xml-with-python-and-deploy-it-as-a-cron-job-to-google-cloud-c5c4f986c734
  Note also need to submit to search engines (once)
* Typogrify - its added to uv. Do I need it??



I'm using the free plan of FontAwesome, which has a monthly limit of 10,000 views. Login to fontawesome.com to see usage.



# Hot Re-loader fun

https://developer.chrome.com/docs/web-platform/page-lifecycle-api

Need to be able to handle:
1 Browser refresh/reload by hand
1 Browser refresh/reload triggered from server following change
1 Navigating away to a page on another site which exists
1 Navigating away to a page on another site which does not exist (404)
1 Navigating to another page on my site which exists
1 Navigating to another page on my site which does not exist (404)
1 Back button
1 Forward button
1 Close tab
1 Close browser

Tools:
1 Server detecting connection has dropped
1 Client detecting connection has dropped
1 Client side localstorage
1 Browser detecting a reload/refresh is about to happen
  event beforeunload
  event pagehide and pageshow
  event visibilitychange
  event freeze and resume

See https://developer.chrome.com/docs/web-platform/page-lifecycle-api
