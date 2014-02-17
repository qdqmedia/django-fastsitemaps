try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
from django.utils.xmlutils import SimplerXMLGenerator
from django.conf import settings
from sitemaps import RequestSitemap

def sitemap_generator(request, maps, page, current_site):
    output = StringIO()
    xml = SimplerXMLGenerator(output, settings.DEFAULT_CHARSET)
    xml.startDocument()
    namespaces = {'xmlns':'http://www.sitemaps.org/schemas/sitemap/0.9'}
    for site in maps:
        ns_getter = getattr(site, "get_namespaces", lambda: {})
        namespaces.update(ns_getter())
    xml.startElement('urlset', namespaces)
    yield output.getvalue()
    pos = output.tell()
    for site in maps:
        if callable(site):
            if issubclass(site, RequestSitemap):
                site = site(request=request)
            else:
                site = site()
        elif hasattr(site, 'request'):
            site.request = request
        for url in site.get_urls(page=page, site=current_site):
            xml.startElement('url', {})
            xml.addQuickElement('loc', url['location'])
            try:
                if url['lastmod']:
                    xml.addQuickElement('lastmod', url['lastmod'].strftime('%Y-%m-%d'))
            except (KeyError, AttributeError):
                pass
            try:
                if url['changefreq']:
                    xml.addQuickElement('changefreq', url['changefreq'])
            except KeyError:
                pass
            try:
                if url['priority']:
                    xml.addQuickElement('priority', url['priority'])
            except KeyError:
                pass

            # Translations
            translations = url.get("translations", None)
            if translations:
                for lang, uri in translations.items():
                    xml.addQuickElement("xhtml:link", attrs={
                        "rel": "alternate",
                        "hreflang": lang,
                        "href": uri
                    })

            # Video extension
            videos = url.get("videos", [])
            if videos:
                for video in videos:
                    xml.startElement("video:video", {})
                    for tag, value in video.items():
                        xml.addQuickElement("video:%s" % tag, value)
                    xml.endElement("video:video")

            # Image extension
            images = url.get("images", [])
            if images:
                for image in images:
                    xml.startElement("image:image", {})
                    for tag, value in image.items():
                        xml.addQuickElement("image:%s" % tag, value)
                    xml.endElement("image:image")

            xml.endElement('url')
            output.seek(pos)
            yield output.read()
            pos = output.tell()
    xml.endElement('urlset')
    xml.endDocument()
    output.seek(pos)
    last = output.read()
    output.close()
    yield last
