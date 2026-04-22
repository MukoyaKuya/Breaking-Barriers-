from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import calendar

from ..models import (
    NewsItem,
    NewsLine,
    CalendarEvent,
    InfoCard,
    WordOfTruth,
    ManTalk,
    ChildrensBread,
    Book,
    PageView,
)
from ..query_utils import (
    get_cached_cta_card,
    get_cached_faqs,
    get_cached_sidebar_promos,
    get_cached_verse_of_the_day,
    get_optimized_word_of_truth_list,
    get_optimized_man_talk_list,
)
from ..cache_decorators import cache_page_for_anonymous
from ..middleware import get_client_ip


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
        'user_is_staff': request.user.is_staff,
    }
    return render(request, 'church/news_list.html', context)


@cache_page_for_anonymous(60 * 15)
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
    related_articles = NewsItem.objects.filter(is_published=True).exclude(pk=news_item.pk).order_by('?')[:2]
    context = {
        'news_item': news_item,
        'related_articles': related_articles,
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


@cache_page_for_anonymous(60 * 10)
def word_of_truth_list_view(request):
    """Word of Truth listing page"""
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
    if request.headers.get('HX-Request'):
        return render(request, 'church/partials/word_of_truth_items.html', context)
    return render(request, 'church/word_of_truth_list.html', context)


def load_more_word_of_truth_view(request):
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


def word_of_truth_detail_view(request, slug):
    """Detail view for a Word of Truth article."""
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
    related_articles = WordOfTruth.objects.filter(is_published=True).exclude(pk=word_of_truth.pk).order_by('?')[:2]
    context = {
        'word_of_truth': word_of_truth,
        'faqs': faqs,
        'sidebar_promos': sidebar_promos,
        'cta_card': cta_card,
        'verse_of_the_day': verse_of_the_day,
        'related_articles': related_articles,
    }
    return render(request, 'church/word_of_truth_detail.html', context)


def word_of_truth_pdf_view(request, slug):
    """Generate and download PDF for a Word of Truth article"""
    try:
        from xhtml2pdf import pisa
    except ModuleNotFoundError:
        return HttpResponse("PDF generation dependency missing.", status=501)

    word_of_truth = get_object_or_404(WordOfTruth, slug=slug, is_published=True)
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
    from django.template.loader import get_template
    template = get_template('church/word_of_truth_pdf.html')
    context = {'article': word_of_truth, 'current_year': timezone.now().year, 'logo_data_uri': logo_data_uri}
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{word_of_truth.slug}.pdf"'
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
       return HttpResponse('Error generating PDF')
    return response


@cache_page_for_anonymous(60 * 15)
def childrens_bread_list_view(request):
    initial_limit = 9
    articles_list = ChildrensBread.objects.filter(is_published=True).order_by('-created_at')
    total_count = articles_list.count()
    initial_articles = articles_list[:initial_limit]
    has_more = total_count > initial_limit
    context = {
        'articles': initial_articles,
        'has_more': has_more,
        'next_offset': initial_limit,
    }
    if request.headers.get('HX-Request'):
        return render(request, 'church/partials/childrens_bread_items.html', context)
    return render(request, 'church/childrens_bread_list.html', context)


def load_more_childrens_bread_view(request):
    offset = int(request.GET.get('offset', 0))
    limit = 9
    articles = ChildrensBread.objects.filter(is_published=True).order_by('-created_at')[offset:offset + limit]
    total_count = ChildrensBread.objects.filter(is_published=True).count()
    next_offset = offset + len(articles)
    has_more = next_offset < total_count
    context = {'articles': articles, 'has_more': has_more, 'next_offset': next_offset}
    return render(request, 'church/partials/childrens_bread_items.html', context)


def childrens_bread_detail_view(request, slug):
    cache_key = f'childrens_bread_{slug}'
    article = cache.get(cache_key)
    if not article:
        article = get_object_or_404(ChildrensBread, slug=slug, is_published=True)
        cache.set(cache_key, article, 600)
    try:
        PageView.objects.create(path=request.path[:500], ip_address=get_client_ip(request), content_type='childrensbread', object_id=article.pk)
    except Exception:
        pass
    context = {
        'article': article,
        'faqs': get_cached_faqs(),
        'sidebar_promos': get_cached_sidebar_promos(limit=3),
        'cta_card': get_cached_cta_card(),
        'verse_of_the_day': get_cached_verse_of_the_day(),
        'related_articles': ChildrensBread.objects.filter(is_published=True).exclude(pk=article.pk).order_by('?')[:2],
    }
    return render(request, 'church/childrens_bread_detail.html', context)


@cache_page_for_anonymous(60 * 15)
def news_line_list_view(request):
    initial_limit = 9
    articles_list = NewsLine.objects.filter(is_published=True).order_by('-created_at')
    total_count = articles_list.count()
    initial_articles = articles_list[:initial_limit]
    has_more = total_count > initial_limit
    context = {'articles': initial_articles, 'has_more': has_more, 'next_offset': initial_limit}
    if request.headers.get('HX-Request'):
        return render(request, 'church/partials/news_line_items.html', context)
    return render(request, 'church/news_line_list.html', context)


def news_line_detail_view(request, slug):
    cache_key = f'news_line_{slug}'
    article = cache.get(cache_key)
    if not article:
        article = get_object_or_404(NewsLine, slug=slug, is_published=True)
        cache.set(cache_key, article, 600)
    try:
        PageView.objects.create(path=request.path[:500], ip_address=get_client_ip(request), content_type='newsline', object_id=article.pk)
    except Exception:
        pass
    context = {
        'article': article,
        'faqs': get_cached_faqs(),
        'sidebar_promos': get_cached_sidebar_promos(limit=3),
        'cta_card': get_cached_cta_card(),
        'verse_of_the_day': get_cached_verse_of_the_day(),
    }
    return render(request, 'church/news_line_detail.html', context)


def load_more_news_line_view(request):
    offset = int(request.GET.get('offset', 0))
    limit = 9
    articles = NewsLine.objects.filter(is_published=True).order_by('-created_at')[offset:offset + limit]
    total_count = NewsLine.objects.filter(is_published=True).count()
    next_offset = offset + len(articles)
    has_more = next_offset < total_count
    context = {'articles': articles, 'has_more': has_more, 'next_offset': next_offset}
    return render(request, 'church/partials/news_line_items.html', context)


@cache_page_for_anonymous(60 * 10)
def man_talk_list_view(request):
    from django.db import connection
    search_query = request.GET.get('q', '').strip()
    page = request.GET.get('page', 1)
    articles = ManTalk.objects.filter(is_published=True).order_by('-created_at')
    if search_query:
        articles = articles.filter(Q(title__icontains=search_query) | Q(summary__icontains=search_query) | Q(body__icontains=search_query))
    paginator = Paginator(articles, 9)
    try:
        articles_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        articles_page = paginator.page(1)
    return render(request, 'church/mantalk_list.html', {'articles': articles_page, 'search_query': search_query, 'page_obj': articles_page})


def man_talk_detail_view(request, slug):
    article = get_object_or_404(ManTalk, slug=slug, is_published=True)
    recent_articles = ManTalk.objects.filter(is_published=True).exclude(id=article.id).order_by('-created_at')[:3]
    context = {
        'article': article,
        'recent_articles': recent_articles,
        'faqs': get_cached_faqs(),
        'sidebar_promos': get_cached_sidebar_promos(limit=3),
        'cta_card': get_cached_cta_card(),
        'verse_of_the_day': get_cached_verse_of_the_day(),
    }
    return render(request, 'church/mantalk_detail.html', context)


def book_list_view(request):
    search_query = request.GET.get('q', '')
    books_list = Book.objects.filter(is_published=True).order_by('-created_at')
    if search_query:
        books_list = books_list.filter(Q(title__icontains=search_query) | Q(description__icontains=search_query) | Q(author__icontains=search_query))
    paginator = Paginator(books_list, 9)
    page = request.GET.get('page', 1)
    try:
        books_page = paginator.page(page)
    except (PageNotAnInteger, EmptyPage):
        books_page = paginator.page(1)
    return render(request, 'church/book_list.html', {'books': books_page, 'search_query': search_query, 'page_obj': books_page})


@cache_page_for_anonymous(60 * 15)
def book_detail_view(request, slug):
    book = get_object_or_404(Book, slug=slug, is_published=True)
    recent_books = Book.objects.filter(is_published=True).exclude(id=book.id).order_by('-created_at')[:3]
    return render(request, 'church/book_detail.html', {'book': book, 'recent_books': recent_books})


def add_article_comment(request, content_type_id, object_id):
    from django.contrib.contenttypes.models import ContentType
    from ..forms import ArticleCommentForm
    from django.contrib import messages
    from django.shortcuts import redirect
    import time
    
    if request.method == 'POST':
        # Rate limiting: 1 comment per 60 seconds per session
        last_comment_time = request.session.get('last_comment_time')
        current_time = time.time()
        
        if last_comment_time and (current_time - last_comment_time < 60):
            wait_time = int(60 - (current_time - last_comment_time))
            messages.error(request, f"You are posting too frequently. Please wait {wait_time} seconds.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        form = ArticleCommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.content_type_id = content_type_id
            comment.object_id = object_id
            comment.save()
            
            # Update last comment timestamp
            request.session['last_comment_time'] = current_time
            messages.success(request, "Your comment has been submitted successfully.")
        else:
            # Capture specific form errors to show to the user
            error_msg = "There was an error submitting your comment."
            for field, errors in form.errors.items():
                if field != 'honeypot':
                    error_msg = f"{errors[0]}"
                    break
            messages.error(request, error_msg)
            
    # Redirect back to the page the user came from
    return redirect(request.META.get('HTTP_REFERER', '/'))
