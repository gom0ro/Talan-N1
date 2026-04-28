from django.contrib import admin
from .models import (
    NewsCategory, News, Teacher, GalleryAlbum, GalleryImage,
    DocumentCategory, Document, Page, Slider, ContactMessage,
    Club, ClubSchedule, ClubMember, ClubImage,
    Article, ArticleImage,
    PsychologyArticle, SocialArticle, MedicalArticle, GuardianArticle,
    InstagramReel, LibraryCategory, LibraryBook
)


# ── Жаңалықтар ──────────────────────────────────────────────

class NewsInline(admin.StackedInline):
    """Категория ішінде жаңалықтарды қосу/өңдеу"""
    model = News
    extra = 0
    fields = ('title', 'image', 'is_published', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True  # Толық өңдеу сілтемесі


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'news_count')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [NewsInline]

    @admin.display(description='Жаңалық саны')
    def news_count(self, obj):
        return obj.news.count()


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category', 'created_at')
    search_fields = ('title', 'text')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    date_hierarchy = 'created_at'
    list_per_page = 20

    fieldsets = (
        ('📝 Негізгі ақпарат', {
            'fields': ('title', 'slug', 'category', 'text', 'image'),
        }),
        ('⚙️ Баптаулар', {
            'fields': ('is_published',),
            'classes': ('collapse',),
        }),
    )


# ── Әкімшілік персонал ──────────────────────────────────────

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'experience', 'order')
    list_filter = ('subject',)
    search_fields = ('name', 'subject')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)


# ── Галерея ─────────────────────────────────────────────────

class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 3
    fields = ('image', 'caption')


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_count', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GalleryImageInline]

    @admin.display(description='Суреттер саны')
    def image_count(self, obj):
        return obj.images.count()


# ── Құжаттар ────────────────────────────────────────────────

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'doc_type_display', 'uploaded_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')

    fieldsets = (
        ('📄 Негізгі ақпарат', {
            'fields': ('title', 'description', 'category'),
        }),
        ('📎 Файл немесе сілтеме', {
            'fields': ('file', 'link'),
            'description': 'Файл жүктеңіз НЕМЕСЕ сыртқы сілтеме беріңіз. Екеуін де толтыруға болады.',
        }),
    )

    @admin.display(description='Түрі')
    def doc_type_display(self, obj):
        icons = {
            'word': '📝 Word',
            'pdf': '📕 PDF',
            'excel': '📊 Excel',
            'powerpoint': '📙 PowerPoint',
            'image': '🖼️ Сурет',
            'archive': '📦 Архив',
            'link': '🔗 Сілтеме',
            'file': '📄 Файл',
        }
        return icons.get(obj.file_type, '📄 Файл')


# ── Беттер ──────────────────────────────────────────────────

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')


# ── Слайдер ─────────────────────────────────────────────────

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)


# ── Хабарламалар ────────────────────────────────────────────

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    list_editable = ('is_read',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'created_at')

    def has_add_permission(self, request):
        return False


# ── Үйірмелер ───────────────────────────────────────────────

class ClubScheduleInline(admin.TabularInline):
    model = ClubSchedule
    verbose_name = "Сабақ кестесі"
    verbose_name_plural = "Информация: Сабақ кестесі"
    extra = 1


class ClubMemberInline(admin.TabularInline):
    model = ClubMember
    verbose_name = "Қатысушы"
    verbose_name_plural = "Информация: Қатысушылар тізімі"
    extra = 1


class ClubImageInline(admin.TabularInline):
    model = ClubImage
    verbose_name = "Фото"
    verbose_name_plural = "Галерея: Үйірме фотосуреттері"
    extra = 3


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'member_count', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)
    search_fields = ('name', 'content')
    
    # Секцияларға бөлу
    fieldsets = (
        ('👉 О кружке', {
            'fields': ('name', 'slug', 'content', 'image', 'order'),
            'description': 'Үйірменің негізгі мәліметтері'
        }),
    )
    
    inlines = [ClubImageInline, ClubScheduleInline, ClubMemberInline]

    @admin.display(description='Қатысушылар')
    def member_count(self, obj):
        return obj.members.count()


# ── Админ-сайт баптаулары ───────────────────────────────────
admin.site.site_header = '«Талант №1» мектебі'
admin.site.site_title = 'Талант №1 — Админ панель'
admin.site.index_title = 'Басқару панелі'


# ── Мақалалар (психология, әлеуметтік, мед. қызмет, қамқоршылық) ───

class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    verbose_name = 'Қосымша сурет'
    verbose_name_plural = 'Галерея: Қосымша суреттер (5-ке дейін)'
    extra = 1
    max_num = 5


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'section', 'author', 'is_published', 'created_at')
    list_filter = ('section', 'is_published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    date_hierarchy = 'created_at'
    list_per_page = 20

    fieldsets = (
        ('📝 Негізгі ақпарат', {
            'fields': ('title', 'slug', 'section', 'author', 'content', 'image'),
        }),
        ('⚙️ Баптаулар', {
            'fields': ('is_published',),
            'classes': ('collapse',),
        }),
    )

    inlines = [ArticleImageInline]


# ── Proxy модельдер (әр бөлім бөлек) ────────────────────────

class SectionArticleAdmin(admin.ModelAdmin):
    """Бір бөлімнің мақалаларын көрсететін базалық класс"""
    section_key = None  # override in subclass

    list_display = ('title', 'author', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    inlines = [ArticleImageInline]

    fieldsets = (
        ('📝 Негізгі ақпарат', {
            'fields': ('title', 'slug', 'author', 'content', 'image'),
        }),
        ('⚙️ Баптаулар', {
            'fields': ('is_published',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(section=self.section_key)

    def save_model(self, request, obj, form, change):
        obj.section = self.section_key
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(PsychologyArticle)
class PsychologyArticleAdmin(SectionArticleAdmin):
    section_key = 'psychology'


@admin.register(SocialArticle)
class SocialArticleAdmin(SectionArticleAdmin):
    section_key = 'social'


@admin.register(MedicalArticle)
class MedicalArticleAdmin(SectionArticleAdmin):
    section_key = 'medical'


@admin.register(GuardianArticle)
class GuardianArticleAdmin(SectionArticleAdmin):
    section_key = 'guardian'


@admin.register(LibraryCategory)
class LibraryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(LibraryBook)
class LibraryBookAdmin(admin.ModelAdmin):
    list_display = ('book_number', 'title', 'category', 'is_published', 'created_at')
    list_display_links = ('book_number', 'title')
    list_editable = ('is_published', 'category')
    list_filter = ('category', 'is_published')
    search_fields = ('book_number', 'title', 'description')
    
    fieldsets = (
        ('📝 Негізгі ақпарат', {
            'fields': ('book_number', 'title', 'description', 'category'),
        }),
        ('📎 Файл және Мұқаба', {
            'fields': ('cover', 'file', 'link'),
            'description': 'Электронды кітапты жүктеңіз немесе сілтеме беріңіз.',
        }),
        ('⚙️ Баптаулар', {
            'fields': ('is_published',),
        }),
    )


@admin.register(InstagramReel)
class InstagramReelAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order', 'created_at')
    list_editable = ('is_active', 'order')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'embed_code')

