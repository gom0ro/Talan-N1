from django import forms
from django.contrib import admin
from .models import (
    NewsCategory, News, Teacher, GalleryAlbum, GalleryImage,
    DocumentCategory, Document, Page, Slider, ContactMessage,
    Club, ClubSchedule, ClubMember, ClubImage,
    Article, ArticleImage,
    PsychologyArticle, SocialArticle, MedicalArticle, GuardianArticle,
    InstagramReel, LibraryCategory, LibraryBook,
    MethodoCategory, MethodoItem, ZhetistikItem,
    MagistrItem, SanatItem, ZhetekshilerItem,
    TimetableItem, TarbieItem, BastauyshItem,
    ParentsMeetingItem,
    ZhylJospar, IsShara, AskhanaItem,
    PedQoldau, IshkiTartip, Profilaktika, Parlament, AdalUrpaq, ZhasUlan,
    AttestationYear, AttestationCategory, AttestationNode,
)

admin.site.site_header = 'Talant No1 Mektep'
admin.site.site_title = 'Talant No1 Admin'
admin.site.index_title = 'Basqaru paneli'


# ── News ──────────────────────────────────────────────────────

class NewsInline(admin.StackedInline):
    model = News
    extra = 0
    fields = ('title', 'image', 'is_published', 'created_at')
    readonly_fields = ('created_at',)
    show_change_link = True


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'news_count')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [NewsInline]

    @admin.display(description='Zhanaly saны')
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
        ('Negizgi aqparat', {
            'fields': ('title', 'slug', 'category', 'text', 'image'),
        }),
        ('Baptaular', {
            'fields': ('is_published',),
            'classes': ('collapse',),
        }),
    )


# ── Teachers ──────────────────────────────────────────────────

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'experience', 'order')
    list_filter = ('subject',)
    search_fields = ('name', 'subject')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)


# ── Gallery ───────────────────────────────────────────────────

class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 3
    fields = ('image', 'instagram_link', 'caption')


@admin.register(GalleryAlbum)
class GalleryAlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'image_count', 'created_at')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GalleryImageInline]

    @admin.display(description='Sureтter sany')
    def image_count(self, obj):
        return obj.images.count()


# ── Documents ─────────────────────────────────────────────────

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_at')
    list_filter = ('category',)
    search_fields = ('title', 'description')
    fieldsets = (
        ('Negizgi aqparat', {
            'fields': ('title', 'description', 'category'),
        }),
        ('Fayl nemese silteme', {
            'fields': ('file', 'link'),
        }),
    )


# ── Pages ─────────────────────────────────────────────────────

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')


# ── Slider ────────────────────────────────────────────────────

@admin.register(Slider)
class SliderAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)


# ── Contact ───────────────────────────────────────────────────

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    list_editable = ('is_read',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'phone', 'subject', 'message', 'created_at')

    def has_add_permission(self, request):
        return False


# ── Clubs ─────────────────────────────────────────────────────

class ClubScheduleInline(admin.TabularInline):
    model = ClubSchedule
    verbose_name = "Sabaq kestesi"
    verbose_name_plural = "Sabaq kestesi"
    extra = 1


class ClubMemberInline(admin.TabularInline):
    model = ClubMember
    verbose_name = "Qatysusy"
    verbose_name_plural = "Qatysuсhylar"
    extra = 1


class ClubImageInline(admin.TabularInline):
    model = ClubImage
    verbose_name = "Foto"
    verbose_name_plural = "Galereya"
    extra = 3


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'member_count', 'order')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order',)
    search_fields = ('name', 'content')
    fieldsets = (
        ('Ujiyrme turaly', {
            'fields': ('name', 'slug', 'content', 'image', 'order'),
        }),
    )
    inlines = [ClubImageInline, ClubScheduleInline, ClubMemberInline]

    @admin.display(description='Qatysuсhylar')
    def member_count(self, obj):
        return obj.members.count()


# ── Articles ──────────────────────────────────────────────────

class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
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
        ('Negizgi aqparat', {
            'fields': ('title', 'slug', 'section', 'author', 'content', 'image'),
        }),
        ('Baptaular', {
            'fields': ('is_published',),
            'classes': ('collapse',),
        }),
    )
    inlines = [ArticleImageInline]


class SectionArticleAdmin(admin.ModelAdmin):
    section_key = None
    list_display = ('title', 'author', 'is_published', 'created_at')
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    list_editable = ('is_published',)
    date_hierarchy = 'created_at'
    list_per_page = 20
    inlines = [ArticleImageInline]
    fieldsets = (
        ('Negizgi aqparat', {
            'fields': ('title', 'slug', 'author', 'content', 'image'),
        }),
        ('Baptaular', {
            'fields': ('is_published',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(section=self.section_key)

    def save_model(self, request, obj, form, change):
        obj.section = self.section_key
        if not obj.author_id:
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


# ── Library ───────────────────────────────────────────────────

@admin.register(LibraryCategory)
class LibraryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(LibraryBook)
class LibraryBookAdmin(admin.ModelAdmin):
    list_display = ('book_number', 'title', 'category', 'is_published')
    list_display_links = ('book_number', 'title')
    list_editable = ('is_published', 'category')
    list_filter = ('category', 'is_published')
    search_fields = ('book_number', 'title', 'description')
    fieldsets = (
        ('Negizgi aqparat', {
            'fields': ('book_number', 'title', 'description', 'category'),
        }),
        ('Fayl zhane Muqaba', {
            'fields': ('cover', 'file', 'link'),
        }),
        ('Baptaular', {
            'fields': ('is_published',),
        }),
    )


# ── Instagram ─────────────────────────────────────────────────

@admin.register(InstagramReel)
class InstagramReelAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_editable = ('is_active', 'order')


# ── Methodo (proxy models) ────────────────────────────────────

class BaseMethodoItemAdmin(admin.ModelAdmin):
    category_slug = None
    category_name = ''
    list_display = ('title', 'order', 'created_at')
    list_editable = ('order',)
    search_fields = ('title', 'description')
    fieldsets = (
        ('Negizgi aqparat', {
            'fields': ('title', 'description', 'order'),
        }),
        ('Suretterdi zhukteyin (2 foto)', {
            'fields': ('image', 'image2'),
            'description': '1-shi zhane 2-shi fotony zhyktey alasyz.',
        }),
        ('Dokument', {
            'fields': ('file',),
            'description': 'PDF, Word, PPTX nemese kez-kelgen quzhatt.',
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if self.category_slug:
            return qs.filter(category__slug=self.category_slug)
        return qs

    def save_model(self, request, obj, form, change):
        if self.category_slug:
            cat, _ = MethodoCategory.objects.get_or_create(
                slug=self.category_slug,
                defaults={'name': self.category_name or self.category_slug}
            )
            obj.category = cat
        super().save_model(request, obj, form, change)


@admin.register(MagistrItem)
class MagistrItemAdmin(BaseMethodoItemAdmin):
    category_slug = 'magistr'
    category_name = 'Pedagogika magistri'


@admin.register(SanatItem)
class SanatItemAdmin(BaseMethodoItemAdmin):
    category_slug = 'sanat'
    category_name = 'Biliktіlik sanat'


@admin.register(ZhetekshilerItem)
class ZhetekshilerItemAdmin(BaseMethodoItemAdmin):
    category_slug = 'zhetekshiler'
    category_name = 'Odistemeilik birlestik zhetekshileri'


# ── Zhetistikter ──────────────────────────────────────────────

@admin.register(ZhetistikItem)
class ZhetistikItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at')
    list_editable = ('order',)
    search_fields = ('title', 'description')
    fieldsets = (
        ('Negizgi aqparat', {
            'fields': ('title', 'description', 'order'),
        }),
        ('Suretterdi zhukteyin (2 foto)', {
            'fields': ('image1', 'image2'),
            'description': '1-shi zhane 2-shi fotony zhyktey alasyz.',
        }),
        ('Dokument', {
            'fields': ('file',),
            'description': 'PDF, Word, PPTX nemese kez-kelgen quzhatt.',
        }),
    )


# ── Simple pages admin ────────────────────────────────────────

class SimpleItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at')
    list_editable = ('order',)
    search_fields = ('title', 'description')
    fieldsets = (
        ('Negizgi aqparat', {
            'fields': ('title', 'description', 'order'),
        }),
        ('2 Foto', {
            'fields': ('image1', 'image2'),
            'description': '1-shi zhane 2-shi fotony zhyktey alasyz.',
        }),
        ('Fayl / Dokument', {
            'fields': ('file',),
            'description': 'PDF, Word, PPTX nemese kez-kelgen quzhatt.',
        }),
    )


@admin.register(TimetableItem)
class TimetableItemAdmin(SimpleItemAdmin):
    pass


@admin.register(TarbieItem)
class TarbieItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'order', 'created_at')
    list_editable = ('order',)
    search_fields = ('title', 'description')
    fieldsets = (
        ('Negizgi aqparat', {
            'fields': ('title', 'description', 'order'),
        }),
        ('2 Foto', {
            'fields': ('image1', 'image2'),
        }),
        ('Fayl zhykteu', {
            'fields': ('file',),
            'description': 'PDF, Word, PPTX fayl zhyktey alasyz.',
        }),
        ('Google Drive silteme', {
            'fields': ('link',),
            'description': 'Google Drive nemese basqa silteme URL-in osy jerge qoyynyz.',
        }),
    )


@admin.register(BastauyshItem)
class BastauyshItemAdmin(SimpleItemAdmin):
    pass


@admin.register(ParentsMeetingItem)
class ParentsMeetingItemAdmin(SimpleItemAdmin):
    pass


# ── Жылдық жоспар және Іс-шаралар ────────────────────────────

class TarbieFullItemAdmin(admin.ModelAdmin):
    """Базалық класс: тақырып, сипаттама, 2 фото, файл, сілтеме, реттілік"""
    list_display = ('title', 'order', 'created_at')
    list_editable = ('order',)
    search_fields = ('title', 'description')
    fieldsets = (
        ('📝 Негізгі ақпарат', {
            'fields': ('title', 'description', 'order'),
        }),
        ('🖼️ Фотосуреттер', {
            'fields': ('image1', 'image2'),
            'description': '1-ші және 2-ші фотоны жүктей аласыз.',
        }),
        ('📎 Файл немесе Сілтеме', {
            'fields': ('file', 'link'),
            'description': 'Файл жүктеңіз НЕМЕСЕ Google Drive сілтемесін беріңіз.',
        }),
    )


@admin.register(ZhylJospar)
class ZhylJosparAdmin(TarbieFullItemAdmin):
    pass


@admin.register(IsShara)
class IsShareAdmin(TarbieFullItemAdmin):
    pass


# ── Асхана ────────────────────────────────────────────────────

@admin.register(AskhanaItem)
class AskhanaItemAdmin(TarbieFullItemAdmin):
    pass


# ── АТА-АНАЛАР бөлімі ────────────────────────────────────────

@admin.register(PedQoldau)
class PedQoldauAdmin(TarbieFullItemAdmin):
    pass


@admin.register(IshkiTartip)
class IshkiTartipAdmin(TarbieFullItemAdmin):
    pass


@admin.register(Profilaktika)
class ProfilaktikaAdmin(TarbieFullItemAdmin):
    pass


@admin.register(Parlament)
class ParlamentAdmin(TarbieFullItemAdmin):
    pass


@admin.register(AdalUrpaq)
class AdalUrpaqAdmin(TarbieFullItemAdmin):
    pass


@admin.register(ZhasUlan)
class ZhasUlanAdmin(TarbieFullItemAdmin):
    pass


# ── Аттестация ────────────────────────────────────────────────

TYPE_HELP = """
Төрт түр бар — таңдаған түрі сайттағы кесте құрылымын анықтайды:

1. Стандартты кесте — тізімделген құжаттар бір кестеде.
2. Жылдар бойынша кесте — әр жылға жеке сұр аккордеон, ішінде кесте.
3. Жаңаша ашылатын аккордеон — кесте жолдарының үшінші бағасында
   жыл/топ аккордеондары, ашылғанда файлдар тізімі.
4. Терең сатылар кесте — төрт баған, үшіншісінде бөлім → жыл → файл.

1-түрде элементтер тікелей «Құжат» болады.
2-түрде: жыл (Топ) → құжат.
3-түрде: тақырып (жол) → жыл (Топ) → құжат.
4-түрде: тақырып (жол) → бөлім (Топ) → жыл (Топ) → құжат.
"""


class AttestationNodeForm(forms.ModelForm):
    """Құжат файлын жүктеу өрісі — браузер тек PDF таңдайды."""

    class Meta:
        model = AttestationNode
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        widget = self.fields['file'].widget
        widget.attrs['accept'] = 'application/pdf,.pdf'
        existing = getattr(widget, 'attrs', {}).get('class', '')
        widget.attrs['class'] = (existing + ' att-pdf-input').strip()


class AttestationNodeInline(admin.TabularInline):
    """Санаттың жоғарғы деңгейіндегі элементтер (1-түрде — құжаттар)"""
    model = AttestationNode
    form = AttestationNodeForm
    extra = 1
    fk_name = 'category'
    fields = ('order', 'kind', 'title', 'subtitle', 'file', 'link', 'is_open', 'is_active')
    ordering = ('order', 'id')
    verbose_name = 'Element'
    verbose_name_plural = 'Elementter'


@admin.register(AttestationYear)
class AttestationYearAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_count', 'node_count', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    prepopulated_fields = {'slug': ('title',)}
    fieldsets = (
        ('Negizgi aqparat', {
            'fields': ('title', 'slug', 'order', 'is_active'),
        }),
    )

    @admin.display(description='Sanattar sany')
    def category_count(self, obj):
        return obj.categories.count()

    @admin.display(description='Elementter sany')
    def node_count(self, obj):
        return AttestationNode.objects.filter(category__year=obj).count()


@admin.register(AttestationCategory)
class AttestationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'node_count', 'order', 'is_open', 'is_active')
    list_display_links = ('name',)
    list_editable = ('type', 'order', 'is_open', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('name',)
    exclude = ('year',)
    fieldsets = (
        ('Blok turi', {
            'fields': ('type',),
            'description': TYPE_HELP,
        }),
        ('Negizgi aqparat', {
            'fields': ('name', 'order'),
        }),
        ('Baptaular', {
            'fields': ('is_open', 'is_active'),
            'classes': ('collapse',),
            'description': '«Ashыq kuyinde» — kelganda ushul blok tuldegi kuyde bolady.',
        }),
    )
    inlines = [AttestationNodeInline]

    def save_model(self, request, obj, form, change):
        """«Оқу жылы» өрісі формада көрсетілмейді — әдепкі жылмен толтырылады."""
        if not obj.year_id:
            obj.year = (
                AttestationYear.objects.filter(is_active=True).first()
                or AttestationYear.objects.first()
            )
        super().save_model(request, obj, form, change)

    @admin.display(description='Elementter sany')
    def node_count(self, obj):
        return obj.nodes.count()


@admin.register(AttestationNode)
class AttestationNodeAdmin(admin.ModelAdmin):
    """Терең деңгейдегі элементтер осында басқарылады"""
    form = AttestationNodeForm
    list_display = ('order', 'title', 'kind', 'category', 'parent', 'level', 'has_file')
    list_display_links = ('title',)
    list_editable = ('order', 'kind')
    list_filter = ('category', 'kind', 'is_active')
    search_fields = ('title', 'subtitle')
    autocomplete_fields = ('category',)
    fieldsets = (
        ('Negizgi aqparat', {
            'fields': ('order', 'category', 'parent', 'kind', 'title', 'subtitle'),
        }),
        ('Fayl nemese silteme', {
            'fields': ('file', 'link'),
            'description': 'Fayl yukteiniz НЕМЕСЕ сыртқы silteme beriniz.',
        }),
        ('Baptaular', {
            'fields': ('is_open', 'is_active'),
            'classes': ('collapse',),
        }),
    )

    @admin.display(description='Deнгей')
    def level(self, obj):
        depth = 0
        parent = obj.parent
        while parent is not None:
            depth += 1
            parent = parent.parent
        return depth

    @admin.display(boolean=True, description='Fayl bar')
    def has_file(self, obj):
        return obj.has_file
