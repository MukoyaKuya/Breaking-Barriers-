from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.db import connection

from ..models import (
    Verse,
    Testimonial,
    GalleryImage,
    AboutPage,
    Partner,
    NewsletterSubscriber,
    FAQ,
    SidebarPromo,
    WordOfTruth,
    ManTalk,
    ChildrensBread,
    SchoolMinistryEnrollment,
    PageView,
    ContactMessage,
    PartnerInquiry,
    BoardMember,
)
from ..query_utils import (
    get_cached_hero_settings,
    get_cached_cta_card,
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
    get_optimized_childrens_bread_preview,
    get_optimized_news_line_preview,
    get_optimized_word_of_truth_preview,
    get_optimized_board_members,
    get_cached_maintenance_settings,
)
from ..cache_decorators import cache_page_for_anonymous
from ..middleware import get_client_ip


@cache_page_for_anonymous(60 * 60) # Cache the shell for an hour
def home_view(request):
    """Serve the lightweight App Shell with the logo instantly."""
    mn_settings = get_cached_maintenance_settings()
    if getattr(mn_settings, 'is_active', False):
        return render(request, 'church/maintenance.html')
    return render(request, 'church/home_shell.html')


@cache_page_for_anonymous(60 * 15)  # Cache content for 15 minutes
def home_content_view(request):
    """Heavy content view lazy-loaded via HTMX."""
    limit = 6
    news_items = get_optimized_news_items(limit=limit)
    from ..models import NewsItem
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


def leadership_view(request):
    """Leadership / Board Members page."""
    members = get_optimized_board_members()
    return render(request, 'church/leadership.html', {'members': members})


@cache_page_for_anonymous(60 * 15)  # Cache for 15 minutes
def gallery_view(request):
    """Gallery view with optional category filter and pagination."""
    category = request.GET.get('category', '')
    
    if category:
        gallery_images_list = GalleryImage.objects.filter(category=category).order_by('-uploaded_at')
    else:
        gallery_images_list = GalleryImage.objects.all().order_at('-uploaded_at')
    
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
    from ..forms import ContactForm, PartnerInquiryForm

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
    from ..forms import SchoolEnrollmentForm
    
    if request.method == 'POST':
        form = SchoolEnrollmentForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            name = form.cleaned_data.get('name')
            phone_number = form.cleaned_data.get('phone_number')

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
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        form = SchoolEnrollmentForm()

    return render(request, 'church/school_of_ministry.html', {'form': form})


def media_view(request):
    """Media page"""
    return render(request, 'church/media.html')


def contact_us_view(request):
    """Contact Us page with form submission."""
    from ..forms import ContactForm
    
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


def search_view(request):
    """Search functionality with pagination and caching. Searches across multiple content types."""
    import hashlib
    from itertools import chain
    from operator import attrgetter
    from ..models import NewsItem, WordOfTruth, ChildrensBread, ManTalk

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
    from django.urls import reverse
    from ..models import NewsItem, WordOfTruth

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
