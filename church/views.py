from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import calendar
from .models import (
    Verse,
    NewsItem,
    CalendarEvent,
    Testimonial,
    GalleryImage,
    HeroSettings,
    AboutPage,
    InfoCard,
    CTACard,
    MensMinistry,
    Partner,
    NewsletterSubscriber,
    FAQ,
    SidebarPromo,
    WordOfTruth,
    SchoolMinistryEnrollment,
)
from .query_utils import (
    get_cached_hero_settings,
    get_cached_cta_card,
    get_cached_about_page,
    get_optimized_news_items,
    get_optimized_testimonials,
    get_optimized_gallery_items,
    get_optimized_mens_ministry,
    get_optimized_partners,
    get_optimized_verse_of_the_day,
    get_optimized_info_cards,
    get_optimized_faqs,
    get_optimized_sidebar_promos,
    get_optimized_word_of_truth_list,
)
from django.template.loader import get_template
from io import BytesIO
from easy_thumbnails.files import get_thumbnailer
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .cache_decorators import cache_page_for_anonymous


@cache_page_for_anonymous(60 * 15)  # Cache for 15 minutes (anonymous users only)
def home_view(request):
    """Home page view with featured content (optimized queries + cached singletons)."""
    limit = 6
    news_items = get_optimized_news_items(limit=limit)
    total_count = NewsItem.objects.filter(is_published=True).count()
    has_more_news = total_count > limit

    testimonials = get_optimized_testimonials(limit=6)
    gallery_items = get_optimized_gallery_items(limit=6)
    mens_ministry = get_optimized_mens_ministry()
    partners = get_optimized_partners()
    hero_settings = get_cached_hero_settings()
    verse_of_the_day = get_optimized_verse_of_the_day()

    cards = get_optimized_info_cards()
    childrens_bread_card = cards['childrens_bread']
    news_card = cards['news']
    word_of_truth_card = cards['word_of_truth']
    cta_card = get_cached_cta_card()

    faqs = get_optimized_faqs()
    sidebar_promos = get_optimized_sidebar_promos(limit=3)

    context = {
        'news_items': news_items,
        'has_more_news': has_more_news,
        'testimonials': testimonials,
        'gallery_items': gallery_items,
        'mens_ministry': mens_ministry,
        'partners': partners,
        'hero_settings': hero_settings,
        'verse_of_the_day': verse_of_the_day,
        'childrens_bread_card': childrens_bread_card,
        'news_card': news_card,
        'word_of_truth_card': word_of_truth_card,
        'cta_card': cta_card,
        'faqs': faqs,
        'sidebar_promos': sidebar_promos,
    }
    return render(request, 'church/home.html', context)


@cache_page_for_anonymous(60 * 30)  # Cache for 30 minutes (anonymous users only)
def about_view(request):
    """About page view (driven from AboutPage singleton, cached)."""
    about = AboutPage.load()
    return render(request, 'church/about.html', {'about': about})


def news_list_view(request):
    """Interactive calendar-style view of events"""
    today = timezone.localdate()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    # Get all published calendar events in this month
    monthly_events = CalendarEvent.objects.filter(
        is_published=True,
        event_date__year=year,
        event_date__month=month,
    ).order_by('event_date', 'title')

    # Map events to their calendar day
    events_by_day = {}
    for item in monthly_events:
        events_by_day.setdefault(item.event_date, []).append(item)

    # Build calendar grid (weeks x days)
    cal = calendar.Calendar(firstweekday=6)  # Sunday start
    month_days = list(cal.itermonthdates(year, month))
    weeks = []
    for week_start in range(0, len(month_days), 7):
        week = []
        for day in month_days[week_start:week_start + 7]:
            week.append({
                'date': day,
                'in_current_month': (day.month == month),
                'events': events_by_day.get(day, []),
                'is_today': (day == today),
            })
        weeks.append(week)

    # Previous / next month helpers
    prev_month_year = year
    prev_month = month - 1
    if prev_month == 0:
        prev_month = 12
        prev_month_year -= 1

    next_month_year = year
    next_month = month + 1
    if next_month == 13:
        next_month = 1
        next_month_year += 1

    context = {
        'weeks': weeks,
        'current_year': year,
        'current_month': month,
        'current_month_name': calendar.month_name[month],
        'prev_month': prev_month,
        'prev_month_year': prev_month_year,
        'next_month': next_month,
        'next_month_year': next_month_year,
        'monthly_events': monthly_events,
        'user_is_staff': request.user.is_staff,  # For admin editing features
    }
    return render(request, 'church/news_list.html', context)


@cache_page_for_anonymous(60 * 15)  # Cache for 15 minutes (anonymous users only)
def info_card_detail_view(request, slug):
    """Detail view for Hero Info Cards (Children's Bread, News, Word of Truth)."""
    card = get_object_or_404(InfoCard, slug=slug, is_active=True)
    faqs = get_optimized_faqs()
    sidebar_promos = get_optimized_sidebar_promos(limit=3)
    cta_card = get_cached_cta_card()
    verse_of_the_day = get_optimized_verse_of_the_day()
    context = {
        'card': card,
        'faqs': faqs,
        'sidebar_promos': sidebar_promos,
        'cta_card': cta_card,
        'verse_of_the_day': verse_of_the_day,
    }
    return render(request, 'church/info_card_detail.html', context)


@cache_page_for_anonymous(60 * 15)  # Cache for 15 minutes (anonymous users only)
def news_detail_view(request, slug):
    """Detail view for a single news item"""
    news_item = get_object_or_404(NewsItem, slug=slug, is_published=True)
    context = {
        'news_item': news_item,
    }
    return render(request, 'church/news_detail.html', context)


def load_more_news_view(request):
    """HTMX endpoint to load more news items"""
    offset = int(request.GET.get('offset', 0))
    limit = 6
    
    news_items = NewsItem.objects.filter(is_published=True)[offset:offset + limit]
    total_count = NewsItem.objects.filter(is_published=True).count()
    next_offset = offset + len(news_items)
    has_more = next_offset < total_count
    
    context = {
        'news_items': news_items,
        'has_more_news': has_more,
        'next_offset': next_offset,
    }
    return render(request, 'church/partials/news_items.html', context)


def gallery_view(request):
    """Gallery view with optional category filter and pagination."""
    category = request.GET.get('category', '')
    
    if category:
        gallery_images_list = GalleryImage.objects.filter(category=category).order_by('-uploaded_at')
    else:
        gallery_images_list = GalleryImage.objects.all().order_by('-uploaded_at')
    
    # Paginate results - 9 per page
    paginator = Paginator(gallery_images_list, 9)
    page = request.GET.get('page', 1)
    
    try:
        gallery_images = paginator.page(page)
    except PageNotAnInteger:
        gallery_images = paginator.page(1)
    except EmptyPage:
        gallery_images = paginator.page(paginator.num_pages)
    
    # Get all unique categories for the filters
    categories = GalleryImage.objects.values_list('category', flat=True).distinct()
    
    context = {
        'gallery_images': gallery_images,
        'page_obj': gallery_images,
        'categories': categories,
        'selected_category': category,
    }
    
    # If HTMX request, return only the gallery items partial
    if request.headers.get('HX-Request'):
        return render(request, 'church/partials/gallery_items.html', context)
    
    return render(request, 'church/gallery.html', context)


def privacy_view(request):
    """Privacy policy page"""
    return render(request, 'church/privacy.html')


def donate_view(request):
    """Donations page"""
    return render(request, 'church/donate.html')


def childrens_bread_school_view(request):
    """Children's Bread School page"""
    return render(request, 'church/childrens_bread_school.html')


def school_of_ministry_view(request):
    """School of Ministry enrolment form (stores enrollments in DB)."""
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        phone_number = (request.POST.get('phone_number') or '').strip()

        if not name or not email:
            messages.error(request, "Please enter your name and a valid email address.")
            return redirect('school_of_ministry')

        enrollment, created = SchoolMinistryEnrollment.objects.get_or_create(
            email=email,
            defaults={
                'name': name,
                'phone_number': phone_number,
                'programme': 'School of Ministry',
            },
        )

        if not created:
            # Keep record fresh if they submit again
            changed = False
            if enrollment.name != name:
                enrollment.name = name
                changed = True
            if phone_number and enrollment.phone_number != phone_number:
                enrollment.phone_number = phone_number
                changed = True
            if changed:
                enrollment.save(update_fields=['name', 'phone_number'])

            messages.info(request, "You are already enrolled. Thank you!")
        else:
            messages.success(request, "Thank you! You’re enrolled for the School of Ministry. We’ll contact you soon.")

        return redirect('school_of_ministry')

    return render(request, 'church/school_of_ministry.html')


def media_view(request):
    """Media page"""
    return render(request, 'church/media.html')


def contact_us_view(request):
    """Contact Us page"""
    return render(request, 'church/contact_us.html')


@cache_page_for_anonymous(60 * 10)  # Cache for 10 minutes (anonymous users only)
def word_of_truth_view(request):
    """Word of Truth page (optimized with pagination)."""
    verses = Verse.objects.filter(is_active=True, is_featured=True).order_by('-date_posted')
    
    # Paginate articles - 20 per page
    articles_list = get_optimized_word_of_truth_list()
    paginator = Paginator(articles_list, 20)
    page = request.GET.get('page', 1)
    
    try:
        articles = paginator.page(page)
    except PageNotAnInteger:
        articles = paginator.page(1)
    except EmptyPage:
        articles = paginator.page(paginator.num_pages)
    
    context = {
        'verses': verses,
        'articles': articles,
        'page_obj': articles,
    }
    return render(request, 'church/word_of_truth.html', context)


@cache_page_for_anonymous(60 * 15)  # Cache for 15 minutes (anonymous users only)
def word_of_truth_detail_view(request, slug):
    """Detail view for a Word of Truth article (optimized sidebar)."""
    word_of_truth = get_object_or_404(WordOfTruth, slug=slug, is_published=True)
    faqs = get_optimized_faqs()
    sidebar_promos = get_optimized_sidebar_promos(limit=3)
    cta_card = get_cached_cta_card()
    verse_of_the_day = get_optimized_verse_of_the_day()
    context = {
        'word_of_truth': word_of_truth,
        'faqs': faqs,
        'sidebar_promos': sidebar_promos,
        'cta_card': cta_card,
        'verse_of_the_day': verse_of_the_day,
    }
    return render(request, 'church/word_of_truth_detail.html', context)


def word_of_truth_pdf_view(request, slug):
    """Generate and download PDF for a Word of Truth article"""
    # Optional dependency: only needed for PDF generation
    try:
        from xhtml2pdf import pisa
    except ModuleNotFoundError:
        return HttpResponse(
            "PDF generation dependency missing: install 'xhtml2pdf' to enable this feature.",
            status=501,
            content_type="text/plain",
        )

    word_of_truth = get_object_or_404(WordOfTruth, slug=slug, is_published=True)
    
    # Logo for PDF: embed as base64 so xhtml2pdf renders it reliably (file:// often fails on Windows)
    from pathlib import Path
    from django.conf import settings
    import base64
    logo_data_uri = None
    logo_file = Path(settings.BASE_DIR) / 'static' / 'images' / 'logo.png'
    if logo_file.exists():
        try:
            logo_bytes = logo_file.read_bytes()
            logo_b64 = base64.b64encode(logo_bytes).decode('ascii')
            logo_data_uri = f'data:image/png;base64,{logo_b64}'
        except Exception:
            pass
    
    template_path = 'church/word_of_truth_pdf.html'
    context = {
        'article': word_of_truth,
        'current_year': timezone.now().year,
        'logo_data_uri': logo_data_uri,
    }
    
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{word_of_truth.slug}.pdf"'
    
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    
    # create a pdf
    pisa_status = pisa.CreatePDF(
       html, dest=response)
    
    # if error then return response as error
    if pisa_status.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def search_view(request):
    """Search functionality with pagination and caching. Uses PostgreSQL full-text when available."""
    from django.db import connection
    from django.core.cache import cache
    import hashlib

    query = request.GET.get('q', '').strip()
    results = []
    page = request.GET.get('page', 1)

    if query:
        # Cache search results for popular queries (1 hour)
        # Use hash of query + page to create cache key (prefix added automatically)
        cache_key = f'search_{hashlib.md5(f"{query}_{page}".encode()).hexdigest()}'
        cached_results = cache.get(cache_key)
        
        if cached_results is not None:
            results = cached_results
        else:
            # Use PostgreSQL full-text search when available (faster, better ranking)
            if connection.vendor == 'postgresql':
                try:
                    from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank

                    search_vector = (
                        SearchVector('title', weight='A', config='english')
                        + SearchVector('summary', weight='B', config='english')
                        + SearchVector('body', weight='C', config='english')
                    )
                    search_query = SearchQuery(query, config='english')
                    news_results = (
                        NewsItem.objects.filter(is_published=True)
                        .annotate(
                            search=search_vector,
                            rank=SearchRank(search_vector, search_query),
                        )
                        .filter(search=search_query)
                        .order_by('-rank', '-created_at')
                    )
                except Exception:
                    # Fallback to icontains if full-text fails (e.g. extension missing)
                    news_results = NewsItem.objects.filter(
                        Q(title__icontains=query)
                        | Q(summary__icontains=query)
                        | Q(body__icontains=query),
                        is_published=True,
                    ).order_by('-created_at')
            else:
                # SQLite / other: use icontains
                news_results = NewsItem.objects.filter(
                    Q(title__icontains=query)
                    | Q(summary__icontains=query)
                    | Q(body__icontains=query),
                    is_published=True,
                ).order_by('-created_at')

            # Paginate results - 12 per page
            paginator = Paginator(news_results, 12)

            try:
                results = paginator.page(page)
            except PageNotAnInteger:
                results = paginator.page(1)
            except EmptyPage:
                results = paginator.page(paginator.num_pages)
            
            # Cache paginated results for 1 hour
            cache.set(cache_key, results, 3600)

    context = {
        'query': query,
        'results': results,
        'page_obj': results if query else None,
    }
    return render(request, 'church/search_results.html', context)


def search_autocomplete_view(request):
    """JSON API for search autocomplete. Returns up to 8 suggestions (news + word of truth)."""
    from django.db import connection
    from django.http import JsonResponse
    from django.urls import reverse

    q = (request.GET.get('q') or '').strip()
    if len(q) < 2:
        return JsonResponse({'suggestions': []})

    suggestions = []
    try:
        if connection.vendor == 'postgresql':
            try:
                from django.contrib.postgres.search import SearchVector, SearchQuery

                sv = (
                    SearchVector('title', weight='A', config='english')
                    + SearchVector('summary', weight='B', config='english')
                    + SearchVector('body', weight='C', config='english')
                )
                sq = SearchQuery(q, config='english')
                news = (
                    NewsItem.objects.filter(is_published=True)
                    .annotate(search=sv)
                    .filter(search=sq)
                    .values('title', 'slug')[:5]
                )
                for n in news:
                    suggestions.append({
                        'title': n['title'],
                        'url': reverse('news_detail', args=[n['slug']]),
                        'type': 'Event',
                    })
            except Exception:
                news = (
                    NewsItem.objects.filter(
                        Q(title__icontains=q) | Q(summary__icontains=q),
                        is_published=True,
                    )
                    .values('title', 'slug')[:5]
                )
                for n in news:
                    suggestions.append({
                        'title': n['title'],
                        'url': reverse('news_detail', args=[n['slug']]),
                        'type': 'Event',
                    })
        else:
            news = (
                NewsItem.objects.filter(
                    Q(title__icontains=q) | Q(summary__icontains=q),
                    is_published=True,
                )
                .values('title', 'slug')[:5]
            )
            for n in news:
                suggestions.append({
                    'title': n['title'],
                    'url': reverse('news_detail', args=[n['slug']]),
                    'type': 'Event',
                })

        # Word of Truth suggestions (fill up to 8 total)
        if connection.vendor == 'postgresql':
            try:
                from django.contrib.postgres.search import SearchVector, SearchQuery

                sv = SearchVector('title', weight='A', config='english') + SearchVector('summary', weight='B', config='english')
                sq = SearchQuery(q, config='english')
                wot = (
                    WordOfTruth.objects.filter(is_published=True)
                    .annotate(search=sv)
                    .filter(search=sq)
                    .values('title', 'slug')[:8 - len(suggestions)]
                )
            except Exception:
                wot = (
                    WordOfTruth.objects.filter(
                        Q(title__icontains=q) | Q(summary__icontains=q),
                        is_published=True,
                    )
                    .values('title', 'slug')[:8 - len(suggestions)]
                )
        else:
            wot = (
                WordOfTruth.objects.filter(
                    Q(title__icontains=q) | Q(summary__icontains=q),
                    is_published=True,
                )
                .values('title', 'slug')[:8 - len(suggestions)]
            )
        for w in wot:
            suggestions.append({
                'title': w['title'],
                'url': reverse('word_of_truth_detail', args=[w['slug']]),
                'type': 'Word of Truth',
            })
    except Exception:
        pass

    return JsonResponse({'suggestions': suggestions[:8]})


def calendar_event_create_view(request):
    """AJAX endpoint to create a calendar event"""
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
            return JsonResponse({
                'success': True,
                'event': {
                    'id': event.id,
                    'title': event.title,
                    'event_date': str(event.event_date),
                    'color': event.color,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid method'}, status=405)


def calendar_event_detail_view(request, event_id):
    """AJAX endpoint to get calendar event details (for viewing)"""
    event = get_object_or_404(CalendarEvent, id=event_id, is_published=True)
    
    if request.method == 'GET':
        if event.image:
            if event.image_cropping:
                image_url = get_thumbnailer(event.image).get_thumbnail({
                    'size': (800, 600),
                    'box': event.image_cropping,
                    'crop': True,
                    'detail': True,
                }).url
            else:
                image_url = event.image.url
        else:
            image_url = None
            
        return JsonResponse({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'event_date': str(event.event_date),
            'event_type': event.event_type,
            'location': event.location,
            'color': event.color,
            'image_url': image_url,
        })
    
    return JsonResponse({'error': 'Invalid method'}, status=405)


def calendar_event_edit_view(request, event_id):
    """AJAX endpoint to edit a calendar event (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    event = get_object_or_404(CalendarEvent, id=event_id)
    
    if request.method == 'POST':
        try:
            event.title = request.POST.get('title', event.title)
            event.description = request.POST.get('description', event.description)
            event.event_date = request.POST.get('event_date', event.event_date)
            event.event_type = request.POST.get('event_type', event.event_type)
            event.location = request.POST.get('location', event.location)
            event.color = request.POST.get('color', event.color)
            event.is_published = request.POST.get('is_published', 'true').lower() == 'true'
            event.save()
            
            return JsonResponse({
                'success': True,
                'event': {
                    'id': event.id,
                    'title': event.title,
                    'event_date': str(event.event_date),
                    'color': event.color,
                }
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    elif request.method == 'GET':
        return JsonResponse({
            'id': event.id,
            'title': event.title,
            'description': event.description,
            'event_date': str(event.event_date),
            'event_type': event.event_type,
            'location': event.location,
            'color': event.color,
            'is_published': event.is_published,
        })
    
    return JsonResponse({'error': 'Invalid method'}, status=405)


def calendar_event_delete_view(request, event_id):
    """AJAX endpoint to delete a calendar event"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    event = get_object_or_404(CalendarEvent, id=event_id)
    
    if request.method == 'POST':
        event.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def newsletter_subscribe_view(request):
    """Handle newsletter email subscriptions from the footer form."""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
            if not subscriber.is_active:
                subscriber.is_active = True
                subscriber.save(update_fields=['is_active'])
            if created:
                messages.success(request, "Thank you for subscribing to our newsletter.")
            else:
                messages.info(request, "You are already subscribed to our newsletter.")
        else:
            messages.error(request, "Please enter a valid email address.")

    # Redirect back to the page the user came from (usually the homepage)
    next_url = request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)
