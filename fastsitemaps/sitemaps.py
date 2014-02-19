from django.contrib.sitemaps import Sitemap, Site
from django.core.exceptions import ImproperlyConfigured


class RequestSitemap(Sitemap):
    def __init__(self, request=None):
        self.request = request
        
    def __get(self, name, obj, default=None):
        try:
            attr = getattr(self, name)
        except AttributeError:
            return default
        if callable(attr):
            return attr(obj)
        return attr

    _get = __get

    def _get_urlinfo(self, item, site):
        loc = self.__get('location', item)
        if not loc.startswith('http'):
            loc = "http://%s%s" % (site.domain, loc)
        priority = self.__get('priority', item, None)
        url_info = {
            'item':       item,
            'location':   loc,
            'lastmod':    self.__get('lastmod', item, None),
            'changefreq': self.__get('changefreq', item, None),
            'priority':   str(priority is not None and priority or ''),
        }
        return url_info

    def get_urls(self, page=1, site=None):
        "Returns a generator instead of a list, also prevents http: doubling up"
        if site is None:
            if Site._meta.installed:
                try:
                    site = Site.objects.get_current()
                except Site.DoesNotExist:
                    pass
            if site is None:
                raise ImproperlyConfigured("In order to use Sitemaps you must either use the sites framework or pass in a Site or RequestSite object in your view code.")
        for item in self.paginator.page(page).object_list:
            yield self._get_urlinfo(item, site)

    @classmethod
    def get_namespaces(self):
        return {}


class VideoSitemapMixin(object):
    def _get_urlinfo(self, item, site):
        url_info = super(VideoSitemapMixin, self)._get_urlinfo(item, site)
        url_info["videos"] = self._get("videos", item, None)
        return url_info

    @classmethod
    def get_namespaces(self):
        namespaces = super(VideoSitemapMixin, self).get_namespaces()
        namespaces["xmlns:video"] = "http://www.google.com/schemas/sitemap-video/1.1"
        return namespaces


class ImageSitemapMixin(object):
    def _get_urlinfo(self, item, site):
        url_info = super(ImageSitemapMixin, self)._get_urlinfo(item, site)
        url_info["images"] = self._get("images", item, None)
        return url_info

    @classmethod
    def get_namespaces(self):
        namespaces = super(ImageSitemapMixin, self).get_namespaces()
        namespaces["xmlns:image"] = "http://www.google.com/schemas/sitemap-image/1.1"
        return namespaces


class TranslationSitemapMixin(object):
    """
    Your sitemap objects will execute translations function or attribute.

    translations must return a dict with languages as keys and url as value.
    """
    def _get_urlinfo(self, item, site):
        url_info = super(TranslationSitemapMixin, self)._get_urlinfo(item, site)
        url_info["translations"] = {
            lang:  uri if uri.startswith('http') else "http://%s%s" % (site.domain, uri)
            for lang, uri in self._get("translations", item, {}).items()
        }
        return url_info

    @classmethod
    def get_namespaces(self):
        namespaces = super(TranslationSitemapMixin, self).get_namespaces()
        namespaces["xmlns:xhtml"]="http://www.w3.org/1999/xhtml"
        return namespaces