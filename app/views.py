from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages

from .models import (
    News, NewsCategory, Teacher, GalleryAlbum,
    DocumentCategory, Document, Page, Slider, Club,
    Article, InstagramReel, LibraryCategory, LibraryBook
)
from .forms import ContactForm


# ── Басты бет ───────────────────────────────────────────────

def index(request):
    """Басты бет"""
    sliders = Slider.objects.filter(is_active=True)
    latest_news = News.objects.filter(is_published=True)[:6]
    instagram_reels = InstagramReel.objects.filter(is_active=True)
    context = {
        'sliders': sliders,
        'latest_news': latest_news,
        'instagram_reels': instagram_reels,
    }
    return render(request, 'index.html', context)


# ── Мектеп туралы ───────────────────────────────────────────

def about(request):
    """Мектеп туралы бет"""
    page = Page.objects.filter(slug='about').first()
    teachers_preview = Teacher.objects.all()[:4]
    context = {
        'page': page,
        'teachers_preview': teachers_preview,
    }
    return render(request, 'about.html', context)


def kitapkhana(request):
    """Кітапхана беті (санаттар тізімі)"""
    categories = LibraryCategory.objects.all()
    context = {
        'categories': categories,
    }
    return render(request, 'about/kitapkhana.html', context)


def kitapkhana_category(request, slug):
    """Белгілі бір санаттағы кітаптар тізімі"""
    category = get_object_or_404(LibraryCategory, slug=slug)
    books = category.books.filter(is_published=True)
    context = {
        'category': category,
        'books': books,
    }
    return render(request, 'about/kitapkhana_category.html', context)


# ── Жаңалықтар ──────────────────────────────────────────────

def news_list(request):
    """Жаңалықтар тізімі (пагинация + іздеу + санат)"""
    queryset = News.objects.filter(is_published=True)
    categories = NewsCategory.objects.all()

    # Іздеу
    search_query = request.GET.get('q', '')
    if search_query:
        queryset = queryset.filter(
            Q(title__icontains=search_query) |
            Q(text__icontains=search_query)
        )

    # Санат бойынша сүзу
    category_slug = request.GET.get('category', '')
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)

    paginator = Paginator(queryset, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'current_category': category_slug,
    }
    return render(request, 'news_list.html', context)


def news_detail(request, slug):
    """Жаңалық толық беті"""
    news_item = get_object_or_404(News, slug=slug, is_published=True)
    related_news = News.objects.filter(
        is_published=True, category=news_item.category
    ).exclude(pk=news_item.pk)[:3]
    context = {
        'news': news_item,
        'related_news': related_news,
    }
    return render(request, 'news_detail.html', context)


# ── Мұғалімдер ──────────────────────────────────────────────

def teacher_list(request):
    """Мұғалімдер тізімі"""
    teachers = Teacher.objects.all()
    return render(request, 'teacher_list.html', {'teachers': teachers})


def teacher_detail(request, slug):
    """Мұғалім туралы толық ақпарат"""
    teacher = get_object_or_404(Teacher, slug=slug)
    return render(request, 'teacher_detail.html', {'teacher': teacher})


# ── Галерея ─────────────────────────────────────────────────

def gallery(request):
    """Галерея — альбомдар тізімі"""
    albums = GalleryAlbum.objects.all()
    return render(request, 'gallery.html', {'albums': albums})


def gallery_album(request, slug):
    """Альбом ішіндегі суреттер"""
    album = get_object_or_404(GalleryAlbum, slug=slug)
    return render(request, 'gallery_album.html', {'album': album})


# ── Құжаттар ────────────────────────────────────────────────

def documents(request):
    """Құжаттар тізімі"""
    categories = DocumentCategory.objects.prefetch_related('documents').all()
    return render(request, 'documents.html', {'categories': categories})


# ── Байланыс ────────────────────────────────────────────────

def contact(request):
    """Байланыс беті + форма"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Хабарламаңыз сәтті жіберілді! Рақмет.')
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


# ── Статикалық бет ──────────────────────────────────────────

def static_page(request, slug):
    """Кез-келген статикалық бет"""
    try:
        page = Page.objects.get(slug=slug)
    except Page.DoesNotExist:
        page = Page.objects.create(title=slug.replace('-', ' ').title(), slug=slug, content='Бұл бет әзірге бос. <br> Админкадан толтырыңыз.')
    return render(request, [f'pages/{slug}.html', 'static_page.html'], {'page': page})


def club_detail(request, slug):
    """Үйірмелер мен клубтардың толық беті"""
    club = get_object_or_404(Club, slug=slug)
    return render(request, 'club_detail.html', {'club': club})


# ── Мақалалар (психология, әлеуметтік, мед., қамқоршылық) ──────

SECTION_TITLES = {
    'psychology': 'Психология',
    'social': 'Әлеуметтік жұмыс',
    'medical': 'Медициналық қызмет',
    'guardian': 'Қамқоршылық кеңес',
}


def article_list(request, section):
    """Бөлім бойынша мақалалар тізімі"""
    articles = Article.objects.filter(section=section, is_published=True)
    section_title = SECTION_TITLES.get(section, section)

    paginator = Paginator(articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'section': section,
        'section_title': section_title,
    }
    return render(request, 'article_list.html', context)


def article_detail(request, section, slug):
    """Мақаланың толық беті"""
    article = get_object_or_404(Article, slug=slug, section=section, is_published=True)
    related = Article.objects.filter(
        section=section, is_published=True
    ).exclude(pk=article.pk)[:3]
    section_title = SECTION_TITLES.get(section, section)

    context = {
        'article': article,
        'related': related,
        'section': section,
        'section_title': section_title,
    }
    return render(request, 'article_detail.html', context)
