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
* Freely mix HTML with/without Jinja2 templates and Markdown with TOML frontmatter for metadata (also passed through Jinja2 templates).
* Extra metadata provided to the Jinja templates e.g. for timestamps and to create path navigation.
* Automatic generation of sitemap (both HTML and xml file) from the content (for SEO).
* Hot reloading localhost server, which rebuilds on change before signalling to browser(s) to reload.

The build process works as follows:

1 Clone the content directory into a new output directory.
1 Using only the output directory
1.1 Convert each markdown file (`*.md`) to an HTML (`*.html`) file of same name, optionally applying Jinja2 template specified in the frontmatter.
1.1 Apply Jinja2 templates to all HTML files which do not start with an underscore, and render back in place.
1.1 Delete all source files and directories (anything with a leading underscore in the path segment).

The end result is a clean output directory ready for deployment.

Every build is a clean build. No caching as plenty faster enough without complexity penalty or subtle gotchas.

# TODO

* Content: skills, interests, now page, tools

* Move the explanation into one of the web pages, and link from here.

* Remake favicon.ico
* Find a link to the PDF for my "Choosing an appropriate model for novelty detection" paper.
  See https://ieeexplore.ieee.org/document/607503
* Add Google analytics
* Add a robots.txt file, and add a sitemap.xml
  See https://thatware.co/xml-sitemap-creation-python/
  See https://michael-lisboa.medium.com/automate-your-sitemap-xml-with-python-and-deploy-it-as-a-cron-job-to-google-cloud-c5c4f986c734
  Note also need to submit to search engines (once)
* Typogrify - its added to uv. Do I need it??
