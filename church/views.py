from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import calendar
from .models import (
    Verse,
    NewsItem,
    NewsLine,
    CalendarEvent,
    Testimonial,
    GalleryImage,
    HeroSettings,
    AboutPage,
    InfoCard,
    CTACard,
    MensMinistry,
    Book,
    Partner,
    NewsletterSubscriber,
    FAQ,
    SidebarPromo,
    WordOfTruth,
    ManTalk,
    ChildrensBread,
    SchoolMinistryEnrollment,
    PageView,
)
from .query_utils import (
    get_cached_hero_settings,
    get_cached_cta_card,
    get_cached_about_page,
    get_cached_faqs,
    get_cached_sidebar_promos,
    get_cached_verse_of_the_day,
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
    get_optimized_man_talk_list,
    get_optimized_childrens_bread_preview,
    get_optimized_news_line_preview,
    get_optimized_word_of_truth_preview,
)
from django.template.loader import get_template
from io import BytesIO
from easy_thumbnails.files import get_thumbnailer
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .cache_decorators import cache_page_for_anonymous
from .middleware import get_client_ip


@cache_page_for_anonymous(60 * 60) # Cache the shell for an hour
def home_view(request):
    """Serve the lightweight App Shell with the logo instantly."""
    return render(request, 'church/home_shell.html')


@cache_page_for_anonymous(60 * 15)  # Cache content for 15 minutes
def home_content_view(request):
    """Heavy content view lazy-loaded via HTMX."""
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

    # Article previews for info card carousels (latest 5 per section)
    childrens_bread_articles = get_optimized_childrens_bread_preview(limit=5)
    news_line_articles = get_optimized_news_line_preview(limit=5)
    word_of_truth_articles = get_optimized_word_of_truth_preview(limit=5)

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
        'childrens_bread_articles': childrens_bread_articles,
        'news_line_articles': news_line_articles,
        'word_of_truth_articles': word_of_truth_articles,
        'cta_card': cta_card,
        'faqs': faqs,
        'sidebar_promos': sidebar_promos,
    }
    return render(request, 'church/home_content.html', context)


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
    faqs = get_cached_faqs()
    sidebar_promos = get_cached_sidebar_promos(limit=3)
    cta_card = get_cached_cta_card()
    verse_of_the_day = get_cached_verse_of_the_day()
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
    try:
        PageView.objects.create(
            path=request.path[:500],
            ip_address=get_client_ip(request),
            content_type='news',
            object_id=news_item.pk,
        )
    except Exception:
        pass
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


@cache_page_for_anonymous(60 * 15)  # Cache for 15 minutes
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
    """Donations page with contact and partner inquiry forms."""
    from .forms import ContactForm, PartnerInquiryForm

    # Initialize forms with None (or data)
    contact_form = ContactForm(prefix='contact')
    partner_form = PartnerInquiryForm(prefix='partner')

    if request.method == 'POST':
        # Determine which form was submitted based on the button name or prefix presence
        if 'contact-submit' in request.POST:
            contact_form = ContactForm(request.POST, prefix='contact')
            if contact_form.is_valid():
                # Server-side deduplication check
                name = contact_form.cleaned_data.get('name')
                email = contact_form.cleaned_data.get('email')
                message = contact_form.cleaned_data.get('message')
                
                last_msg = ContactMessage.objects.filter(email=email, message=message).order_by('-created_at').first()
                if last_msg and (timezone.now() - last_msg.created_at).total_seconds() < 60:
                    messages.success(request, 'Message Sent Successfully. We will get back to you shortly')
                    return redirect('donate')

                contact_form.save()
                messages.success(request, 'Message Sent Successfully. We will get back to you shortly')
                return redirect('donate')
            else:
                messages.error(request, 'Please correct the errors in the Contact form.')

        elif 'partner-submit' in request.POST:
            partner_form = PartnerInquiryForm(request.POST, prefix='partner')
            if partner_form.is_valid():
                # Server-side deduplication
                email = partner_form.cleaned_data.get('email')
                message = partner_form.cleaned_data.get('message')
                
                last_msg = PartnerInquiry.objects.filter(email=email, message=message).order_by('-created_at').first()
                if last_msg and (timezone.now() - last_msg.created_at).total_seconds() < 60:
                    messages.success(request, 'Message Sent Successfully. We will get back to you shortly')
                    return redirect('donate')

                partner_form.save()
                messages.success(request, 'Message Sent Successfully. We will get back to you shortly')
                return redirect('donate')
            else:
                messages.error(request, 'Please correct the errors in the Partner form.')

    context = {
        'contact_form': contact_form,
        'partner_form': partner_form,
    }
    return render(request, 'church/donate.html', context)


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
    """Contact Us page with form submission."""
    from .forms import ContactForm
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Server-side deduplication
            email = form.cleaned_data.get('email')
            message = form.cleaned_data.get('message')
            
            last_msg = ContactMessage.objects.filter(email=email, message=message).order_by('-created_at').first()
            if last_msg and (timezone.now() - last_msg.created_at).total_seconds() < 60:
                 messages.success(request, 'Message Sent Successfully. We will get back to you shortly')
                 return redirect('contact_us')

            form.save()
            messages.success(request, 'Message Sent Successfully. We will get back to you shortly')
            return redirect('contact_us')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    
    return render(request, 'church/contact_us.html', {'form': form})


@cache_page_for_anonymous(60 * 10)  # Cache for 10 minutes (anonymous users only)
def word_of_truth_list_view(request):
    """Word of Truth listing page - shows 9 articles initially with load more."""
    # Get first 9 articles
    initial_limit = 9
    articles_list = WordOfTruth.objects.filter(is_published=True).order_by('-created_at')
    total_count = articles_list.count()
    
    initial_articles = articles_list[:initial_limit]
    has_more = total_count > initial_limit
    
    context = {
        'articles': initial_articles,
        'has_more': has_more,
        'next_offset': initial_limit,
        'total_count': total_count,
    }
    
    # If HTMX request for loading more, return partial
    if request.headers.get('HX-Request'):
        return render(request, 'church/partials/word_of_truth_items.html', context)
    
    return render(request, 'church/word_of_truth_list.html', context)


def load_more_word_of_truth_view(request):
    """HTMX endpoint to load more Word of Truth articles"""
    offset = int(request.GET.get('offset', 0))
    limit = 9
    
    articles = WordOfTruth.objects.filter(is_published=True).order_by('-created_at')[offset:offset + limit]
    total_count = WordOfTruth.objects.filter(is_published=True).count()
    next_offset = offset + len(articles)
    has_more = next_offset < total_count
    
    context = {
        'articles': articles,
        'has_more': has_more,
        'next_offset': next_offset,
    }
    return render(request, 'church/partials/word_of_truth_items.html', context)


@cache_page_for_anonymous(60 * 15)  # Cache for 15 minutes (anonymous users only)
def word_of_truth_detail_view(request, slug):
    """Detail view for a Word of Truth article (optimized sidebar)."""
    cache_key = f'word_of_truth_{slug}'
    word_of_truth = cache.get(cache_key)
    if not word_of_truth:
        word_of_truth = get_object_or_404(WordOfTruth, slug=slug, is_published=True)
        cache.set(cache_key, word_of_truth, 600)
    try:
        PageView.objects.create(
            path=request.path[:500],
            ip_address=get_client_ip(request),
            content_type='wordoftruth',
            object_id=word_of_truth.pk,
        )
    except Exception:
        pass
    faqs = get_cached_faqs()
    sidebar_promos = get_cached_sidebar_promos(limit=3)
    cta_card = get_cached_cta_card()
    verse_of_the_day = get_cached_verse_of_the_day()
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
    """Search functionality with pagination and caching. Searches across multiple content types."""
    from django.db import connection
    from django.core.cache import cache
    import hashlib
    from itertools import chain
    from operator import attrgetter

    query = request.GET.get('q', '').strip()
    results = []
    page = request.GET.get('page', 1)

    if query:
        # Cache search results for popular queries (1 hour)
        cache_key = f'search_multi_{hashlib.md5(f"{query}_{page}".encode()).hexdigest()}'
        cached_results = cache.get(cache_key)
        
        if cached_results is not None:
            results = cached_results
        else:
            # Helper to search a specific model
            def search_model(ModelClass, search_query):
                # Basic icontains search for compatibility (simplifies multi-model logic)
                # In a full Postgres setup, we would use separate SearchVectors for each model
                return list(ModelClass.objects.filter(
                    Q(title__icontains=search_query) | 
                    Q(summary__icontains=search_query) |
                    Q(body__icontains=search_query),
                    is_published=True
                ))

            # Fetch results from all major content models
            news_results = search_model(NewsItem, query)
            wot_results = search_model(WordOfTruth, query)
            cb_results = search_model(ChildrensBread, query)
            mt_results = search_model(ManTalk, query)

            # Combine and sort by creation date (newest first)
            # Annotate with 'model_name' for display logic if needed, 
            # or rely on duck typing (all have title, summary, created_at, get_absolute_url)
            
            combined_results = sorted(
                chain(news_results, wot_results, cb_results, mt_results),
                key=attrgetter('created_at'),
                reverse=True
            )

            # Paginate combined results - 12 per page
            paginator = Paginator(combined_results, 12)

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
        email = request.POST.get('email', '').strip().lower()
        if email:
            # Basic deduplication for newsletter within 60 seconds
            from django.utils import timezone
            last_sub = NewsletterSubscriber.objects.filter(email=email).order_by('-updated_at').first()
            if last_sub and (timezone.now() - last_sub.updated_at).total_seconds() < 60:
                messages.success(request, "Successfully subscribed to our newsletter.")
                return redirect(request.META.get('HTTP_REFERER') or '/')

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

    next_url = request.META.get('HTTP_REFERER') or '/'
    return redirect(next_url)


@cache_page_for_anonymous(60 * 15)  # Cache for 15 minutes (anonymous users only)
def childrens_bread_list_view(request):
    """Children's Bread listing page - shows 9 articles initially with load more."""
    initial_limit = 9
    articles_list = ChildrensBread.objects.filter(is_published=True).order_by('-created_at')
    total_count = articles_list.count()
    
    initial_articles = articles_list[:initial_limit]
    has_more = total_count > initial_limit
    
    context = {
        'articles': initial_articles,
        'has_more': has_more,
        'next_offset': initial_limit,
        'total_count': total_count,
    }
    
    # If HTMX request for loading more, return partial
    if request.headers.get('HX-Request'):
        return render(request, 'church/partials/childrens_bread_items.html', context)
    
    return render(request, 'church/childrens_bread_list.html', context)


def load_more_childrens_bread_view(request):
    """HTMX endpoint to load more Children's Bread articles"""
    offset = int(request.GET.get('offset', 0))
    limit = 9
    
    articles = ChildrensBread.objects.filter(is_published=True).order_by('-created_at')[offset:offset + limit]
    total_count = ChildrensBread.objects.filter(is_published=True).count()
    next_offset = offset + len(articles)
    has_more = next_offset < total_count
    
    context = {
        'articles': articles,
        'has_more': has_more,
        'next_offset': next_offset,
    }
    return render(request, 'church/partials/childrens_bread_items.html', context)


@cache_page_for_anonymous(60 * 15)  # Cache for 15 minutes (anonymous users only)
def childrens_bread_detail_view(request, slug):
    """Detail view for a Children's Bread article (optimized sidebar)."""
    cache_key = f'childrens_bread_{slug}'
    article = cache.get(cache_key)
    if not article:
        article = get_object_or_404(ChildrensBread, slug=slug, is_published=True)
        cache.set(cache_key, article, 600)
    try:
        PageView.objects.create(
            path=request.path[:500],
            ip_address=get_client_ip(request),
            content_type='childrensbread',
            object_id=article.pk,
        )
    except Exception:
        pass
    faqs = get_cached_faqs()
    sidebar_promos = get_cached_sidebar_promos(limit=3)
    cta_card = get_cached_cta_card()
    verse_of_the_day = get_cached_verse_of_the_day()
    context = {
        'article': article,
        'faqs': faqs,
        'sidebar_promos': sidebar_promos,
        'cta_card': cta_card,
        'verse_of_the_day': verse_of_the_day,
    }
    return render(request, 'church/childrens_bread_detail.html', context)


@cache_page_for_anonymous(60 * 15)  # Cache for 15 minutes (anonymous users only)
def news_line_list_view(request):
    """News Line listing page - shows 9 articles initially with load more."""
    initial_limit = 9
    articles_list = NewsLine.objects.filter(is_published=True).order_by('-created_at')
    total_count = articles_list.count()
    
    initial_articles = articles_list[:initial_limit]
    has_more = total_count > initial_limit
    
    context = {
        'articles': initial_articles,
        'has_more': has_more,
        'next_offset': initial_limit,
        'total_count': total_count,
    }
    
    # If HTMX request for loading more, return partial
    if request.headers.get('HX-Request'):
        return render(request, 'church/partials/news_line_items.html', context)
    
    return render(request, 'church/news_line_list.html', context)


@cache_page_for_anonymous(60 * 15)  # Cache for 15 minutes (anonymous users only)
def news_line_detail_view(request, slug):
    """Detail view for a News Line article (optimized sidebar)."""
    cache_key = f'news_line_{slug}'
    article = cache.get(cache_key)
    if not article:
        article = get_object_or_404(NewsLine, slug=slug, is_published=True)
        cache.set(cache_key, article, 600)
    try:
        PageView.objects.create(
            path=request.path[:500],
            ip_address=get_client_ip(request),
            content_type='newsline',
            object_id=article.pk,
        )
    except Exception:
        pass
    faqs = get_cached_faqs()
    sidebar_promos = get_cached_sidebar_promos(limit=3)
    cta_card = get_cached_cta_card()
    verse_of_the_day = get_cached_verse_of_the_day()
    
    context = {
        'article': article,
        'faqs': faqs,
        'sidebar_promos': sidebar_promos,
        'cta_card': cta_card,
        'verse_of_the_day': verse_of_the_day,
    }
    return render(request, 'church/news_line_detail.html', context)


def load_more_news_line_view(request):
    """HTMX endpoint to load more News Line articles"""
    offset = int(request.GET.get('offset', 0))
    limit = 9
    
    articles = NewsLine.objects.filter(is_published=True).order_by('-created_at')[offset:offset + limit]
    total_count = NewsLine.objects.filter(is_published=True).count()
    next_offset = offset + len(articles)
    has_more = next_offset < total_count
    
    context = {
        'articles': articles,
        'has_more': has_more,
        'next_offset': next_offset,
    }
    return render(request, 'church/partials/news_line_items.html', context)


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
    """Platform analytics dashboard (staff only)."""
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

    # Visits per month (last 12 months) for graph: page views + unique visitors per month
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

    # Most read articles (content_type + object_id with count)
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

    # Recent activity: last 5 updated/created items across key models
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
    return render(request, 'church/analytics.html', context)


@staff_member_required
def analytics_reset_view(request):
    """Resets all analytics data (PageViews)."""
    if request.method == 'POST':
        PageView.objects.all().delete()
        from django.contrib import messages
        messages.success(request, 'Analytics data has been successfully reset.')
    return redirect('analytics')


def man_talk_list_view(request):
    """List all ManTalk articles."""
    from django.db import connection
    import hashlib

    search_query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)

    # Use cache for listing pages (5 mins)
    cache_key = f'man_talk_list_{hashlib.md5(f"{search_query}_{page}".encode()).hexdigest()}' if search_query else f'man_talk_list_page_{page}'
    cached_context = cache.get(cache_key)
    
    # Skipping complex object caching for now to avoid serialization issues
    
    articles = ManTalk.objects.filter(is_published=True).order_by('-created_at')

    if search_query:
        if connection.vendor == 'postgresql':
            try:
                from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
                vector = SearchVector('title', weight='A') + \
                         SearchVector('summary', weight='B') + \
                         SearchVector('body', weight='C')
                query = SearchQuery(search_query)
                articles = articles.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.1).order_by('-rank')
            except Exception:
                 articles = articles.filter(
                    Q(title__icontains=search_query) |
                    Q(summary__icontains=search_query) | 
                    Q(body__icontains=search_query)
                )
        else:
            articles = articles.filter(
                Q(title__icontains=search_query) |
                Q(summary__icontains=search_query) | 
                Q(body__icontains=search_query)
            )

    paginator = Paginator(articles, 9)
    try:
        articles_page = paginator.page(page)
    except PageNotAnInteger:
        articles_page = paginator.page(1)
    except EmptyPage:
        articles_page = paginator.page(paginator.num_pages)

    context = {
        'articles': articles_page,
        'search_query': search_query,
        'page_obj': articles_page,  # For pagination template
    }
    return render(request, 'church/mantalk_list.html', context)


def man_talk_detail_view(request, slug):
    """Detail view for a Man Talk article."""
    # Try to get from cache first
    cache_key = f'man_talk_detail_{slug}'
    article = cache.get(cache_key)

    if not article:
        article = get_object_or_404(ManTalk, slug=slug, is_published=True)
        cache.set(cache_key, article, 600)  # Cache for 10 mins

    # Get recent/related articles (excluding current)
    # Cache recent articles list too
    recent_cache_key = 'man_talk_recent'
    recent_articles = cache.get(recent_cache_key)
    if not recent_articles:
        recent_articles = ManTalk.objects.filter(is_published=True).exclude(id=article.id).order_by('-created_at')[:3]
        cache.set(recent_cache_key, recent_articles, 300) # 5 mins

    context = {
        'article': article,
        'recent_articles': recent_articles,
    }
    return render(request, 'church/mantalk_detail.html', context)


def book_list_view(request):
    """List view for Books with pagination."""
    # Cache the base query set for 5 minutes if no search
    search_query = request.GET.get('q', '')
    
    if search_query:
        books_list = Book.objects.filter(is_published=True).filter(
             Q(title__icontains=search_query) |
             Q(description__icontains=search_query) |
             Q(author__icontains=search_query)
        ).order_by('-created_at')
    else:
        # Check cache
        cache_key = 'book_list_all'
        books_list = cache.get(cache_key)
        if not books_list:
            books_list = Book.objects.filter(is_published=True).order_by('-created_at')
            cache.set(cache_key, books_list, 300)

    # Padding/Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(books_list, 9)  # 9 cards per page

    try:
        books_page = paginator.page(page)
    except PageNotAnInteger:
        books_page = paginator.page(1)
    except EmptyPage:
        books_page = paginator.page(paginator.num_pages)

    context = {
        'books': books_page,
        'search_query': search_query,
        'page_obj': books_page,
    }
    return render(request, 'church/book_list.html', context)


@cache_page_for_anonymous(60 * 15)  # Cache full page for 15 minutes (anonymous users)
def book_detail_view(request, slug):
    """Detail view for a Book."""
    cache_key = f'book_detail_{slug}'
    book = cache.get(cache_key)

    if not book:
        book = get_object_or_404(Book, slug=slug, is_published=True)
        cache.set(cache_key, book, 600)

    # Recent books for sidebar or bottom (per-book cache so exclude works correctly)
    recent_cache_key = f'books_recent_exclude_{book.id}'
    recent_books = cache.get(recent_cache_key)
    if not recent_books:
        recent_books = list(
            Book.objects.filter(is_published=True).exclude(id=book.id).order_by('-created_at')[:3]
        )
        cache.set(recent_cache_key, recent_books, 300)

    context = {
        'book': book,
        'recent_books': recent_books,
    }
    return render(request, 'church/book_detail.html', context)
