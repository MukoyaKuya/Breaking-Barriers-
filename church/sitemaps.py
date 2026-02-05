from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import NewsItem, WordOfTruth, ChildrensBread, ManTalk, Book, CalendarEvent

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['home', 'about', 'donate', 'contact', 'beliefs', 'ministries']

    def location(self, item):
        return reverse(item)

class NewsItemSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return NewsItem.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.created_at

class WordOfTruthSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return WordOfTruth.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

class ChildrensBreadSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return ChildrensBread.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

class ManTalkSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return ManTalk.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at
