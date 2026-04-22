from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.core.cache import cache
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from easy_thumbnails.files import get_thumbnailer

from ..models import (
    Verse,
    NewsItem,
    NewsLine,
    CalendarEvent,
    Testimonial,
    GalleryImage,
    InfoCard,
    FAQ,
    Partner,
    NewsletterSubscriber,
    SchoolMinistryEnrollment,
    PageView,
    WordOfTruth,
    ChildrensBread,
    ManTalk,
)
from ..middleware import get_client_ip


def _resolve_article_title_url(content_type, object_id):
    """Return (title, url) for a PageView content_type/object_id, or (None, None) if not found."""
    from django.urls import reverse
    if content_type == 'wordoftruth':
        obj = WordOfTruth.objects.filter(pk=object_id).first()
        if obj:
            return obj.title, reverse('word_of_truth_detail', args=[obj.slug])
    elif content_type == 'childrensbread':
        obj = ChildrensBread.objects.filter(pk=object_id).first()
        if obj:
            return obj.title, reverse('childrens_bread_detail', args=[obj.slug])
    elif content_type == 'news':
        obj = NewsItem.objects.filter(pk=object_id).first()
        if obj:
            return obj.title, reverse('news_detail', args=[obj.slug])
    elif content_type == 'newsline':
        obj = NewsLine.objects.filter(pk=object_id).first()
        if obj:
            return obj.title, reverse('news_line_detail', args=[obj.slug])
    return None, None


@staff_member_required
def analytics_view(request):
    """Platform analytics dashboard (staff only) with 10-minute caching for performance."""
    cache_key = 'platform_analytics_data'
    context = cache.get(cache_key)
    
    if not context:
        today = timezone.now().date()
        # Content stats
        stats = {
            'verses_total': Verse.objects.count(),
            'verses_active': Verse.objects.filter(is_active=True).count(),
            'news_total': NewsItem.objects.count(),
            'news_published': NewsItem.objects.filter(is_published=True).count(),
            'word_of_truth_total': WordOfTruth.objects.count(),
            'word_of_truth_published': WordOfTruth.objects.filter(is_published=True).count(),
            'childrens_bread_total': ChildrensBread.objects.count(),
            'childrens_bread_published': ChildrensBread.objects.filter(is_published=True).count(),
            'gallery_images': GalleryImage.objects.count(),
            'testimonials': Testimonial.objects.count(),
            'info_cards_active': InfoCard.objects.filter(is_active=True).count(),
            'common_questions': FAQ.objects.filter(is_active=True).count(),
            'partners': Partner.objects.filter(is_active=True).count(),
            'calendar_events_total': CalendarEvent.objects.count(),
            'calendar_events_upcoming': CalendarEvent.objects.filter(event_date__gte=today).count(),
            'newsletter_subscribers': NewsletterSubscriber.objects.count(),
            'school_enrollments': SchoolMinistryEnrollment.objects.count(),
        }

        # Page views vs page visits (unique IPs)
        stats['unique_visitors_today'] = PageView.objects.filter(
            viewed_at__date=timezone.now().date(),
            ip_address__isnull=False,
        ).values('ip_address').distinct().count()
        stats['unique_visitors_last_30_days'] = PageView.objects.filter(
            viewed_at__gte=timezone.now() - timezone.timedelta(days=30),
            ip_address__isnull=False,
        ).values('ip_address').distinct().count()

        # Visits per month (last 12 months)
        twelve_months_ago = timezone.now() - timezone.timedelta(days=365)
        visits_by_month = (
            PageView.objects.filter(viewed_at__gte=twelve_months_ago)
            .annotate(month=TruncMonth('viewed_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        unique_by_month = (
            PageView.objects.filter(viewed_at__gte=twelve_months_ago, ip_address__isnull=False)
            .annotate(month=TruncMonth('viewed_at'))
            .values('month')
            .annotate(count=Count('ip_address', distinct=True))
            .order_by('month')
        )
        month_to_unique = {row['month']: row['count'] for row in unique_by_month}
        visits_per_month_labels = []
        visits_per_month_data = []
        visits_per_month_unique_data = []
        for row in visits_by_month:
            visits_per_month_labels.append(row['month'].strftime('%b %Y'))
            visits_per_month_data.append(row['count'])
            visits_per_month_unique_data.append(month_to_unique.get(row['month'], 0))

        # Most read articles
        most_read_qs = (
            PageView.objects.filter(content_type__isnull=False, object_id__isnull=False)
            .values('content_type', 'object_id')
            .annotate(read_count=Count('id'))
            .order_by('-read_count')[:20]
        )
        most_read_articles = []
        most_read_titles = []
        most_read_counts = []
        for row in most_read_qs:
            title, url = _resolve_article_title_url(row['content_type'], row['object_id'])
            if title:
                most_read_articles.append({
                    'title': title,
                    'url': url,
                    'read_count': row['read_count'],
                    'content_type': row['content_type'],
                })
                most_read_titles.append((title[:40] + '…') if len(title) > 40 else title)
                most_read_counts.append(row['read_count'])
        
        stats['total_page_views'] = PageView.objects.count()
        stats['page_views_last_30_days'] = PageView.objects.filter(
            viewed_at__gte=timezone.now() - timezone.timedelta(days=30)
        ).count()

        # Recent activity
        recent_news = NewsItem.objects.order_by('-created_at')[:5]
        recent_wot = WordOfTruth.objects.order_by('-updated_at')[:5]
        recent_cb = ChildrensBread.objects.order_by('-updated_at')[:5]
        upcoming_events = CalendarEvent.objects.filter(event_date__gte=today).order_by('event_date')[:5]

        context = {
            'stats': stats,
            'visits_per_month_labels': visits_per_month_labels,
            'visits_per_month_data': visits_per_month_data,
            'visits_per_month_unique_data': visits_per_month_unique_data,
            'most_read_articles': most_read_articles,
            'most_read_titles': most_read_titles,
            'most_read_counts': most_read_counts,
            'recent_news': recent_news,
            'recent_word_of_truth': recent_wot,
            'recent_childrens_bread': recent_cb,
            'upcoming_events': upcoming_events,
        }
        # Cache for 10 minutes
        cache.set(cache_key, context, 600)

    return render(request, 'church/analytics.html', context)


@staff_member_required
def analytics_reset_view(request):
    """Resets all analytics data (PageViews)."""
    if request.method == 'POST':
        PageView.objects.all().delete()
        cache.delete('platform_analytics_data')
        messages.success(request, 'Analytics data has been successfully reset.')
    return redirect('analytics')


def calendar_event_create_view(request):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    if request.method == 'POST':
        try:
            event = CalendarEvent.objects.create(
                title=request.POST.get('title', ''),
                description=request.POST.get('description', ''),
                event_date=request.POST.get('event_date'),
                event_type=request.POST.get('event_type', 'Other'),
                location=request.POST.get('location', ''),
                color=request.POST.get('color', '#990030'),
                is_published=request.POST.get('is_published', 'true').lower() == 'true',
            )
            return JsonResponse({'success': True, 'event': {'id': event.id, 'title': event.title, 'event_date': str(event.event_date), 'color': event.color}})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


def calendar_event_detail_view(request, event_id):
    event = get_object_or_404(CalendarEvent, id=event_id, is_published=True)
    if request.method == 'GET':
        image_url = event.image.url if event.image else None
        if event.image and event.image_cropping:
             image_url = get_thumbnailer(event.image).get_thumbnail({'size': (800, 600), 'box': event.image_cropping, 'crop': True, 'detail': True}).url
        return JsonResponse({'id': event.id, 'title': event.title, 'description': event.description, 'event_date': str(event.event_date), 'event_type': event.event_type, 'location': event.location, 'color': event.color, 'image_url': image_url})
    return JsonResponse({'error': 'Invalid method'}, status=405)


def calendar_event_edit_view(request, event_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    event = get_object_or_404(CalendarEvent, id=event_id)
    if request.method == 'POST':
        try:
            event.title = request.POST.get('title', event.title); event.description = request.POST.get('description', event.description); event.event_date = request.POST.get('event_date', event.event_date); event.event_type = request.POST.get('event_type', event.event_type); event.location = request.POST.get('location', event.location); event.color = request.POST.get('color', event.color); event.is_published = request.POST.get('is_published', 'true').lower() == 'true'; event.save()
            return JsonResponse({'success': True, 'event': {'id': event.id, 'title': event.title, 'event_date': str(event.event_date), 'color': event.color}})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    elif request.method == 'GET':
        return JsonResponse({'id': event.id, 'title': event.title, 'description': event.description, 'event_date': str(event.event_date), 'event_type': event.event_type, 'location': event.location, 'color': event.color, 'is_published': event.is_published})
    return JsonResponse({'error': 'Invalid method'}, status=405)


def calendar_event_delete_view(request, event_id):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    event = get_object_or_404(CalendarEvent, id=event_id)
    if request.method == 'POST':
        event.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid method'}, status=405)


def newsletter_subscribe_view(request):
    """Handle newsletter email subscriptions from the footer form."""
    from ..forms import NewsletterSubscribeForm
    from django.utils.http import url_has_allowed_host_and_scheme
    next_url = request.META.get('HTTP_REFERER') or '/'
    if not url_has_allowed_host_and_scheme(url=next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        next_url = '/'
    if request.method == 'POST':
        form = NewsletterSubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            last_sub = NewsletterSubscriber.objects.filter(email=email).order_by('-date_subscribed').first()
            if last_sub and (timezone.now() - last_sub.date_subscribed).total_seconds() < 60:
                messages.success(request, "Successfully subscribed to our newsletter.")
                return redirect(next_url)
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save(update_fields=['is_active'])
            if created:
                messages.success(request, "Successfully subscribed to our newsletter.")
            else:
                messages.info(request, "You are already subscribed to our newsletter.")
        else:
            messages.error(request, "Please enter a valid email address.")
    return redirect(next_url)
