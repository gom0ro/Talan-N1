import os
import time
import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from unidecode import unidecode


class NewsCategory(models.Model):
    """Категории новостей"""
    name = models.CharField('Атауы', max_length=100)
    slug = models.SlugField('URL', max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = 'Жаңалық санаты'
        verbose_name_plural = 'Жаңалық санаттары'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class News(models.Model):
    """Жаңалықтар"""
    title = models.CharField('Тақырыбы', max_length=255)
    slug = models.SlugField('URL', max_length=270, unique=True, blank=True)
    text = models.TextField('Мәтіні')
    image = models.ImageField('Сурет', upload_to='news/', blank=True, null=True)
    category = models.ForeignKey(
        NewsCategory, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Санаты',
        related_name='news'
    )
    is_published = models.BooleanField('Жарияланған', default=True)
    created_at = models.DateTimeField('Құрылған уақыты', auto_now_add=True)
    updated_at = models.DateTimeField('Жаңартылған уақыты', auto_now=True)

    class Meta:
        verbose_name = 'Жаңалық'
        verbose_name_plural = 'Жаңалықтар'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Teacher(models.Model):
    """Әкімшілік персонал"""
    name = models.CharField('Аты-жөні', max_length=200)
    slug = models.SlugField('URL', max_length=220, unique=True, blank=True)
    photo = models.ImageField('Фото', upload_to='teachers/', blank=True, null=True)
    subject = models.CharField('Лауазымы / Пәні', max_length=150, blank=True)
    experience = models.PositiveIntegerField('Тәжірибесі (жыл)', default=0)
    description = models.TextField('Сипаттама', blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)

    class Meta:
        verbose_name = 'Әкімшілік персонал'
        verbose_name_plural = 'Әкімшілік персонал'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class GalleryAlbum(models.Model):
    """Фотоальбом"""
    title = models.CharField('Атауы', max_length=200)
    slug = models.SlugField('URL', max_length=220, unique=True, blank=True)
    cover = models.ImageField('Мұқаба', upload_to='gallery/covers/', blank=True, null=True)
    description = models.TextField('Сипаттама', blank=True)
    created_at = models.DateTimeField('Құрылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Фотоальбом'
        verbose_name_plural = 'Фотоальбомдар'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class GalleryImage(models.Model):
    """Фотоальбомдағы сурет"""
    album = models.ForeignKey(
        GalleryAlbum, on_delete=models.CASCADE,
        related_name='images', verbose_name='Альбом'
    )
    image = models.ImageField('Сурет', upload_to='gallery/photos/', blank=True, null=True)
    instagram_link = models.URLField('Instagram видео сілтемесі', blank=True, null=True, help_text='Егер суреттің орнына Инстаграм видео қойғыңыз келсе, осында сілтемені жазыңыз')
    caption = models.CharField('Тақырыбы', max_length=200, blank=True)
    uploaded_at = models.DateTimeField('Жүктелген уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Галерея суреті'
        verbose_name_plural = 'Галерея суреттері'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.caption or f"Сурет #{self.pk}"


class DocumentCategory(models.Model):
    """Құжат санаттары"""
    name = models.CharField('Атауы', max_length=100)
    slug = models.SlugField('URL', max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = 'Құжат санаты'
        verbose_name_plural = 'Құжат санаттары'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Document(models.Model):
    """Құжаттар — файл жүктеу немесе сілтеме беру"""
    title = models.CharField('Атауы', max_length=255)
    description = models.CharField('Сипаттамасы', max_length=500, blank=True)
    file = models.FileField(
        'Файл', upload_to='documents/', blank=True, null=True,
        validators=[],
        help_text='Тек PDF форматындағы файлды жүктеуге болады. Өлшемі 50 МБ-тан аспауы керек.'
    )
    link = models.URLField('Сілтеме (URL)', blank=True,
                           help_text='Сыртқы сілтеме — файл жүктемей, тікелей URL беру үшін')
    category = models.ForeignKey(
        DocumentCategory, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Санаты',
        related_name='documents'
    )
    uploaded_at = models.DateTimeField('Жүктелген уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Құжат'
        verbose_name_plural = 'Құжаттар'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    @property
    def download_url(self):
        """Файл немесе сілтемені қайтарады"""
        if self.file:
            return self.file.url
        return self.link or '#'

    @property
    def file_url(self):
        """file.url немесе link"""
        if self.file:
            return self.file.url
        return self.link or '#'

    @property
    def has_file(self):
        return bool(self.file)

    @property
    def file_type(self):
        """Файл түрін анықтау (иконка үшін)"""
        if self.file and self.file.name:
            name = self.file.name.lower()
            if name.endswith('.pdf'):
                return 'pdf'
            elif name.endswith(('.doc', '.docx')):
                return 'word'
            elif name.endswith(('.xls', '.xlsx')):
                return 'excel'
            elif name.endswith(('.ppt', '.pptx')):
                return 'powerpoint'
            elif name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                return 'image'
            elif name.endswith(('.zip', '.rar', '.7z')):
                return 'archive'
        if self.link:
            return 'link'
        return 'file'



class LibraryCategory(models.Model):
    """Кітапхана санаттары"""
    name = models.CharField('Атауы', max_length=100)
    slug = models.SlugField('URL', max_length=120, unique=True, blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)

    class Meta:
        verbose_name = 'Кітап санаты'
        verbose_name_plural = 'Кітап санаттары'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class LibraryBook(models.Model):
    """Кітапхана — кітаптар тізімі"""
    book_number = models.CharField('№ (Номер)', max_length=50, blank=True)
    title = models.CharField('Тақырыбы / Тема', max_length=255)
    description = models.TextField('Сипаттамасы', blank=True)
    cover = models.ImageField('Мұқаба суреті', upload_to='library/', blank=True, null=True)
    file = models.FileField('Файл (PDF, Word)', upload_to='library/files/', blank=True, null=True,
                            help_text='Электронды кітапты жүктеңіз')
    link = models.URLField('Сыртқы сілтеме', blank=True,
                           help_text='Google Drive, т.б. сілтеме')
    category = models.ForeignKey(
        LibraryCategory, on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Санаты',
        related_name='books'
    )
    is_published = models.BooleanField('Жарияланған', default=True)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Кітап'
        verbose_name_plural = 'Кітапхана'
        ordering = ['category__order', 'title']

    def __str__(self):
        return self.title

    @property
    def download_url(self):
        if self.file:
            return self.file.url
        return self.link or '#'


class Page(models.Model):
    """Статикалық беттер (Мектеп туралы, т.б.)"""
    title = models.CharField('Тақырыбы', max_length=200)
    slug = models.SlugField('URL', max_length=220, unique=True, blank=True)
    content = models.TextField('Мазмұны')
    image = models.ImageField('Сурет', upload_to='pages/', blank=True, null=True)
    updated_at = models.DateTimeField('Жаңартылған уақыты', auto_now=True)

    class Meta:
        verbose_name = 'Бет'
        verbose_name_plural = 'Беттер'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Slider(models.Model):
    """Басты бет слайдері"""
    title = models.CharField('Тақырыбы', max_length=150)
    subtitle = models.CharField('Қосымша мәтін', max_length=300, blank=True)
    image = models.ImageField('Сурет', upload_to='slider/')
    link = models.URLField('Сілтеме', blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)
    is_active = models.BooleanField('Белсенді', default=True)

    class Meta:
        verbose_name = 'Слайд'
        verbose_name_plural = 'Слайдер'
        ordering = ['order']

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """Кері байланыс хабарламалары"""
    name = models.CharField('Аты', max_length=100)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=20, blank=True)
    subject = models.CharField('Тақырыбы', max_length=200, blank=True)
    message = models.TextField('Хабарлама')
    created_at = models.DateTimeField('Жіберілген уақыты', auto_now_add=True)
    is_read = models.BooleanField('Оқылды', default=False)

    class Meta:
        verbose_name = 'Хабарлама'
        verbose_name_plural = 'Хабарламалар'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} — {self.subject}"


class Club(models.Model):
    """Үйірмелер мен клубтар (Қосымша білім беру)"""
    name = models.CharField('Атауы', max_length=200)
    slug = models.SlugField('URL', max_length=220, unique=True, blank=True)
    content = models.TextField('Мазмұны', blank=True)
    image = models.ImageField('Сурет', upload_to='clubs/', blank=True, null=True)
    order = models.PositiveIntegerField('Реттілік', default=0)

    class Meta:
        verbose_name = 'Үйірме'
        verbose_name_plural = 'Үйірмелер'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ClubSchedule(models.Model):
    """Үйірме кестесі"""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='schedules', verbose_name='Үйірме')
    day = models.CharField('Күн', max_length=50)
    time = models.CharField('Уақыт', max_length=100)

    class Meta:
        verbose_name = 'Кесте'
        verbose_name_plural = 'Кестелер'

    def __str__(self):
        return f"{self.day}: {self.time}"


class ClubMember(models.Model):
    """Үйірме қатысушылары"""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members', verbose_name='Үйірме')
    full_name = models.CharField('Аты-жөні', max_length=255)
    info = models.CharField('Қосымша ақпарат (сыныбы т.б.)', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Қатысушы'
        verbose_name_plural = 'Қатысушылар'

    def __str__(self):
        return self.full_name


class ClubImage(models.Model):
    """Үйірме галереясындағы сурет"""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='images', verbose_name='Үйірме')
    image = models.ImageField('Сурет', upload_to='clubs/gallery/')
    caption = models.CharField('Сипаттама', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Үйірме суреті'
        verbose_name_plural = 'Үйірме галереясы'

    def __str__(self):
        return self.caption or f"Сурет #{self.pk}"


class Article(models.Model):
    """Мақалалар — психология, әлеуметтік жұмыс, мед. қызмет, қамқоршылық"""
    SECTION_CHOICES = [
        ('psychology', 'Психология'),
        ('social', 'Әлеуметтік жұмыс'),
        ('medical', 'Медициналық қызмет'),
        ('guardian', 'Қамқоршылық кеңес'),
    ]

    title = models.CharField('Тақырыбы', max_length=255)
    slug = models.SlugField('URL', max_length=270, unique=True, blank=True)
    content = models.TextField('Мазмұны')
    image = models.ImageField('Негізгі сурет', upload_to='articles/', blank=True, null=True)
    section = models.CharField('Бөлім', max_length=20, choices=SECTION_CHOICES)
    author = models.ForeignKey(
        'auth.User', on_delete=models.SET_NULL,
        null=True, blank=True, verbose_name='Автор'
    )
    is_published = models.BooleanField('Жарияланған', default=True)
    created_at = models.DateTimeField('Құрылған уақыты', auto_now_add=True)
    updated_at = models.DateTimeField('Жаңартылған уақыты', auto_now=True)

    class Meta:
        verbose_name = 'Мақала'
        verbose_name_plural = 'Мақалалар'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_section_display_kz(self):
        return dict(self.SECTION_CHOICES).get(self.section, self.section)


class ArticleImage(models.Model):
    """Мақалаға қосымша суреттер (1-5)"""
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE,
        related_name='images', verbose_name='Мақала'
    )
    image = models.ImageField('Сурет', upload_to='articles/gallery/')
    caption = models.CharField('Сипаттама', max_length=200, blank=True)

    class Meta:
        verbose_name = 'Қосымша сурет'
        verbose_name_plural = 'Қосымша суреттер'

    def __str__(self):
        return self.caption or f"Сурет #{self.pk}"


# ── Proxy модельдер (әр бөлім админкада бөлек көрінеді) ──────

class PsychologyArticle(Article):
    class Meta:
        proxy = True
        verbose_name = 'Психология мақаласы'
        verbose_name_plural = 'Психология мақалалары'


class SocialArticle(Article):
    class Meta:
        proxy = True
        verbose_name = 'Әлеуметтік жұмыс мақаласы'
        verbose_name_plural = 'Әлеуметтік жұмыс'


class MedicalArticle(Article):
    class Meta:
        proxy = True
        verbose_name = 'Медициналық қызмет мақаласы'
        verbose_name_plural = 'Медициналық қызмет'


class GuardianArticle(Article):
    class Meta:
        proxy = True
        verbose_name = 'Қамқоршылық кеңес мақаласы'
        verbose_name_plural = 'Қамқоршылық кеңес'


class InstagramReel(models.Model):
    """Инстаграм рилстары (басты бетте көрсету үшін)"""
    title = models.CharField('Атауы немесе сипаттамасы', max_length=200, blank=True, help_text='Тек өзіңізге түсінікті болу үшін')
    embed_code = models.TextField('Instagram Embed коды', help_text='Инстаграмнан алынған HTML кодты осында қойыңыз')
    is_active = models.BooleanField('Көрсету', default=True)
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Инстаграм рилс'
        verbose_name_plural = 'Инстаграм рилстары'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title or f"Рилс #{self.pk}"


class MethodoCategory(models.Model):
    """Әдістемелік жұмыстар, Жетістіктер, Бірлестіктер санаттары"""
    name = models.CharField('Санат атауы (мысалы: Жетістіктер, Жетекшілер)', max_length=150)
    slug = models.SlugField('URL', max_length=170, unique=True, blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)

    class Meta:
        verbose_name = 'Әдістемелік санат'
        verbose_name_plural = '1. Әдістемелік санаттар'
        ordering = ['order', 'name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class MethodoItem(models.Model):
    """Әдістемелік материалдар мен Жетістіктер (Документ, PPTX, Сурет т.б.)"""
    category = models.ForeignKey(MethodoCategory, on_delete=models.CASCADE, related_name='items', verbose_name='Бірлестік санаты')
    title = models.CharField('Аты / Тақырыбы', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    image = models.ImageField('1-ші Сурет (фото)', upload_to='methodo/images/', blank=True, null=True)
    image2 = models.ImageField('2-ші Сурет (фото)', upload_to='methodo/images/', blank=True, null=True)
    file = models.FileField('Документ (PPTX, Word, RAR)', upload_to='methodo/files/', blank=True, null=True, help_text='Word, PPTX, RAR немесе кез-келген құжат')
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Материал немесе Жетістік'
        verbose_name_plural = '2. Материалдар мен Жетістіктер'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


# ── Proxy модельдер: әр санат өз бетінде admin-да ─────────────

class MagistrItem(MethodoItem):
    """Педагогика ғылымдарының магистрі — proxy"""
    class Meta:
        proxy = True
        verbose_name = 'Педагогика ғылымдарының магистрі'
        verbose_name_plural = 'Педагогика ғылымдарының магистрі'


class SanatItem(MethodoItem):
    """Біліктілік санат — proxy"""
    class Meta:
        proxy = True
        verbose_name = 'Біліктілік санат'
        verbose_name_plural = 'Біліктілік санат'


class ZhetekshilerItem(MethodoItem):
    """Өдістемелік бірлестік жетекшілері — proxy"""
    class Meta:
        proxy = True
        verbose_name = 'Өдістемелік бірлестік жетекшілері'
        verbose_name_plural = 'Өдістемелік бірлестік жетекшілері'



class ZhetistikItem(models.Model):
    """Жетістіктер — 2 фотосы бар жазба"""
    title = models.CharField('Тақырыбы / Аты', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    image1 = models.ImageField('1-ші Фото', upload_to='zhetistik/', blank=True, null=True)
    image2 = models.ImageField('2-ші Фото', upload_to='zhetistik/', blank=True, null=True)
    file = models.FileField('Документ (PDF, Word, PPTX)', upload_to='zhetistik/files/', blank=True, null=True,
                            help_text='PDF, Word, PPTX немесе кез-келген құжат')
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Жетістік'
        verbose_name_plural = 'Жетістіктер'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class TimetableItem(models.Model):
    """Sabaq kestesi 5-11 synyp"""
    title = models.CharField('Taqyryby', max_length=255)
    description = models.TextField('Sipattama', blank=True)
    image1 = models.ImageField('1-shi Foto/Keste', upload_to='timetable/', blank=True, null=True)
    image2 = models.ImageField('2-shi Foto/Keste', upload_to='timetable/', blank=True, null=True)
    file = models.FileField('Fayl (PDF, Word)', upload_to='timetable/files/', blank=True, null=True)
    order = models.PositiveIntegerField('Rettіlіk', default=0)
    created_at = models.DateTimeField('Qosylghan uaqyty', auto_now_add=True)

    class Meta:
        verbose_name = 'Sabaq kestesi'
        verbose_name_plural = '5-11 Synyp sabaq kestesi'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class TarbieItem(models.Model):
    """Tarbie orynbasary"""
    title = models.CharField('Taqyryby', max_length=255)
    description = models.TextField('Sipattama', blank=True)
    image1 = models.ImageField('1-shi Foto', upload_to='tarbie_oryn/', blank=True, null=True)
    image2 = models.ImageField('2-shi Foto', upload_to='tarbie_oryn/', blank=True, null=True)
    file = models.FileField('Fayl (PDF, Word, PPTX)', upload_to='tarbie_oryn/files/', blank=True, null=True)
    link = models.URLField('Google Drive / Silteme (URL)', blank=True,
                           help_text='Google Drive siltemesin osy jerge qoyyңyz. Mysal: https://drive.google.com/...')
    order = models.PositiveIntegerField('Rettіlіk', default=0)
    created_at = models.DateTimeField('Qosylghan uaqyty', auto_now_add=True)


    class Meta:
        verbose_name = 'Tarbie orynbasary'
        verbose_name_plural = 'Tarbie orynbasary'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class BastauyshItem(models.Model):
    """Bastauysh synyp"""
    title = models.CharField('Taqyryby', max_length=255)
    description = models.TextField('Sipattama', blank=True)
    image1 = models.ImageField('1-shi Foto', upload_to='bastauysh/', blank=True, null=True)
    image2 = models.ImageField('2-shi Foto', upload_to='bastauysh/', blank=True, null=True)
    file = models.FileField('Fayl (PDF, Word, PPTX)', upload_to='bastauysh/files/', blank=True, null=True)
    order = models.PositiveIntegerField('Rettіlіk', default=0)
    created_at = models.DateTimeField('Qosylghan uaqyty', auto_now_add=True)

    class Meta:
        verbose_name = 'Bastauysh synyp'
        verbose_name_plural = 'Bastauysh synyp'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class ParentsMeetingItem(models.Model):
    title = models.CharField('Taqyryby', max_length=255)
    description = models.TextField('Sipattama', blank=True)
    image1 = models.ImageField('1-shi Foto', upload_to='parents_meeting/', blank=True, null=True)
    image2 = models.ImageField('2-shi Foto', upload_to='parents_meeting/', blank=True, null=True)
    file = models.FileField('Fayl (PDF, Word, PPTX)', upload_to='parents_meeting/files/', blank=True, null=True)
    order = models.PositiveIntegerField('Rettіlіk', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ata-analar zhinalysy'
        verbose_name_plural = 'Ata-analar zhinalysy'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class ZhylJospar(models.Model):
    """Жылдық жоспар — тәрбие жұмыстары"""
    title = models.CharField('Тақырыбы / Аты', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    image1 = models.ImageField('1-ші Фото', upload_to='zhyl_jospar/', blank=True, null=True)
    image2 = models.ImageField('2-ші Фото', upload_to='zhyl_jospar/', blank=True, null=True)
    file = models.FileField('Файл (PDF, Word, PPTX)', upload_to='zhyl_jospar/files/', blank=True, null=True,
                            help_text='PDF, Word, PPTX немесе кез-келген құжат')
    link = models.URLField('Сілтеме (Google Drive т.б.)', blank=True,
                           help_text='Google Drive немесе басқа сілтеме URL')
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Жылдық жоспар'
        verbose_name_plural = 'Жылдық жоспар'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class IsShara(models.Model):
    """Іс-шаралар — тәрбие жұмыстары"""
    title = models.CharField('Тақырыбы / Іс-шара аты', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    image1 = models.ImageField('1-ші Фото', upload_to='is_shara/', blank=True, null=True)
    image2 = models.ImageField('2-ші Фото', upload_to='is_shara/', blank=True, null=True)
    file = models.FileField('Файл (PDF, Word, PPTX)', upload_to='is_shara/files/', blank=True, null=True,
                            help_text='PDF, Word, PPTX немесе кез-келген құжат')
    link = models.URLField('Сілтеме (Google Drive т.б.)', blank=True,
                           help_text='Google Drive немесе басқа сілтеме URL')
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Іс-шара'
        verbose_name_plural = 'Іс-шаралар'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class AskhanaItem(models.Model):
    """Асхана — тамақтану, мәзір, фото"""
    title = models.CharField('Тақырыбы / Аты', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    image1 = models.ImageField('1-ші Фото', upload_to='askhana/', blank=True, null=True)
    image2 = models.ImageField('2-ші Фото', upload_to='askhana/', blank=True, null=True)
    file = models.FileField('Файл (PDF, Word, PPTX)', upload_to='askhana/files/', blank=True, null=True,
                            help_text='PDF, Word, PPTX немесе кез-келген құжат')
    link = models.URLField('Сілтеме (Google Drive т.б.)', blank=True,
                           help_text='Google Drive немесе басқа сілтеме URL')
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Асхана'
        verbose_name_plural = 'Асхана'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


# ── АТА-АНАЛАР бөлімі ─────────────────────────────────────────

class PedQoldau(models.Model):
    """Педагогикалық қолдау орталығы"""
    title = models.CharField('Тақырыбы / Аты', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    image1 = models.ImageField('1-ші Фото', upload_to='ped_qoldau/', blank=True, null=True)
    image2 = models.ImageField('2-ші Фото', upload_to='ped_qoldau/', blank=True, null=True)
    file = models.FileField('Файл (PDF, Word, PPTX)', upload_to='ped_qoldau/files/', blank=True, null=True)
    link = models.URLField('Сілтеме (Google Drive т.б.)', blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Педагогикалық қолдау орталығы'
        verbose_name_plural = 'Педагогикалық қолдау орталығы'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class IshkiTartip(models.Model):
    """Мектептің ішкі тәртіп ережелері"""
    title = models.CharField('Тақырыбы / Аты', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    image1 = models.ImageField('1-ші Фото', upload_to='ishki_tartip/', blank=True, null=True)
    image2 = models.ImageField('2-ші Фото', upload_to='ishki_tartip/', blank=True, null=True)
    file = models.FileField('Файл (PDF, Word, PPTX)', upload_to='ishki_tartip/files/', blank=True, null=True)
    link = models.URLField('Сілтеме (Google Drive т.б.)', blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Мектептің ішкі тәртіп ережелері'
        verbose_name_plural = 'Мектептің ішкі тәртіп ережелері'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class Profilaktika(models.Model):
    """Құқықбұзушылықтың алдын алу"""
    title = models.CharField('Тақырыбы / Аты', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    image1 = models.ImageField('1-ші Фото', upload_to='profilaktika/', blank=True, null=True)
    image2 = models.ImageField('2-ші Фото', upload_to='profilaktika/', blank=True, null=True)
    file = models.FileField('Файл (PDF, Word, PPTX)', upload_to='profilaktika/files/', blank=True, null=True)
    link = models.URLField('Сілтеме (Google Drive т.б.)', blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Құқықбұзушылықтың алдын алу'
        verbose_name_plural = 'Құқықбұзушылықтың алдын алу'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class Parlament(models.Model):
    """Мектеп парламенті"""
    title = models.CharField('Тақырыбы / Аты', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    image1 = models.ImageField('1-ші Фото', upload_to='parlament/', blank=True, null=True)
    image2 = models.ImageField('2-ші Фото', upload_to='parlament/', blank=True, null=True)
    file = models.FileField('Файл (PDF, Word, PPTX)', upload_to='parlament/files/', blank=True, null=True)
    link = models.URLField('Сілтеме (Google Drive т.б.)', blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Мектеп парламенті'
        verbose_name_plural = 'Мектеп парламенті'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class AdalUrpaq(models.Model):
    """Адал ұрпақ"""
    title = models.CharField('Тақырыбы / Аты', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    image1 = models.ImageField('1-ші Фото', upload_to='adal_urpaq/', blank=True, null=True)
    image2 = models.ImageField('2-ші Фото', upload_to='adal_urpaq/', blank=True, null=True)
    file = models.FileField('Файл (PDF, Word, PPTX)', upload_to='adal_urpaq/files/', blank=True, null=True)
    link = models.URLField('Сілтеме (Google Drive т.б.)', blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Адал ұрпақ'
        verbose_name_plural = 'Адал ұрпақ'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


class ZhasUlan(models.Model):
    """Жас ұлан"""
    title = models.CharField('Тақырыбы / Аты', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    image1 = models.ImageField('1-ші Фото', upload_to='zhas_ulan/', blank=True, null=True)
    image2 = models.ImageField('2-ші Фото', upload_to='zhas_ulan/', blank=True, null=True)
    file = models.FileField('Файл (PDF, Word, PPTX)', upload_to='zhas_ulan/files/', blank=True, null=True)
    link = models.URLField('Сілтеме (Google Drive т.б.)', blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Жас ұлан'
        verbose_name_plural = 'Жас ұлан'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title


# ── АТТЕСТАЦИЯ бөлімі ────────────────────────────────────────

class AttestationYear(models.Model):
    """Аттестация — оқу жылы"""
    title = models.CharField('Оқу жылы', max_length=50, help_text='Мысалы: 2024-2025')
    slug = models.SlugField('URL', max_length=60, unique=True, blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)
    is_active = models.BooleanField('Көрсету', default=True)

    class Meta:
        verbose_name = 'Аттестация оқу жылы'
        verbose_name_plural = 'Аттестация оқу жылдары'
        ordering = ['order', 'title']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.title))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class AttestationCategory(models.Model):
    """Аттестация — санат (аккордеон блогы), мысалы «ЖАЛПЫ СИПАТТАМА»"""
    DEFAULT_NAME = 'ЖАЛПЫ СИПАТТАМА'

    TYPE_STANDARD = 1
    TYPE_YEARS = 2
    TYPE_CELL = 3
    TYPE_DEEP = 4
    TYPE_COLLAPSIBLE = 5
    TYPE_CHOICES = [
        (TYPE_STANDARD, 'Стандартная таблица'),
        (TYPE_YEARS, 'Таблица по годам'),
        (TYPE_CELL, 'Таблица с вложенными годами в ячейке'),
        (TYPE_DEEP, 'Многоуровневая таблица'),
        (TYPE_COLLAPSIBLE, 'Стандартная таблица (раскрывающаяся)'),
    ]

    year = models.ForeignKey(
        AttestationYear, on_delete=models.CASCADE,
        related_name='categories', verbose_name='Оқу жылы'
    )
    name = models.CharField('Атауы', max_length=200, help_text='Мысалы: ЖАЛПЫ СИПАТТАМА')
    type = models.PositiveSmallIntegerField(
        'Блок түрі', choices=TYPE_CHOICES, default=TYPE_STANDARD,
        help_text='Сайттағы кесте түрін анықтайды'
    )
    order = models.PositiveIntegerField('Реттілік', default=0)
    is_open = models.BooleanField(
        'Ашық күйінде', default=False,
        help_text='Бет ашылғанда блок түбелдегі күйде болады'
    )
    is_active = models.BooleanField('Көрсету', default=True)

    class Meta:
        verbose_name = 'Аттестация санаты'
        verbose_name_plural = 'Аттестация санаттары'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    def get_type_display(self):
        return dict(self.TYPE_CHOICES).get(self.type, self.type)

    def to_dict(self):
        """
        JS рендерерге берілетін толық блок JSON-ы.

        type бойынша рендерер әр түрлі макет салады:
          1 — стандартты кесте          nodes тікелей құжаттар
          2 — жылдар бойынша кесте     nodes → жыл тобы → құжаттар
          3 — жаңаша ашылатын кесте   nodes → жол → топ → құжаттар
          4 — терең сатылар кестесі    nodes → жол → бөлім → жыл → құжат
          5 — стандартты кесте         nodes тікелей құжаттар (2–4 сияқты ашылып-жабылады)
        """
        return {
            'id': self.pk,
            'type': self.type,
            'categoryTitle': self.name,
            'isOpen': self.is_open,
            'yearTitle': self.year.title,
            'nodes': [node.to_dict() for node in self.active_root_nodes],
        }

    @property
    def active_root_nodes(self):
        attached = getattr(self, 'prefetched_nodes', None)
        if attached is not None:
            return attached
        return self.nodes.filter(parent__isnull=True, is_active=True)


# ── Аттестация: PDF жүктеу көмекшілері ────────────────────────

PDF_MAX_SIZE = 50 * 1024 * 1024  # 50 МБ


def validate_pdf_file(value):
    """
    Тек PDF қабылдайды: кеңейтімі, өлшемі (50 МБ) және
    файл қолтаңбасы («%PDF») тексеріледі.
    """
    if not value:
        return
    name = (getattr(value, 'name', '') or '').lower()
    if not name.endswith('.pdf'):
        raise ValidationError('Тек PDF форматындағы файлды жүктеуге болады.')
    if value.size > PDF_MAX_SIZE:
        raise ValidationError('Файл өлшемі 50 МБ-тан аспауы керек.')
    try:
        value.seek(0)
        header = value.read(5)
        value.seek(0)
    except (AttributeError, ValueError):
        return
    if header and header[:4] != b'%PDF':
        raise ValidationError('Файл PDF құрылымына сәйкес келмейді.')


def documents_upload_to(instance, filename):
    """Қайталанбайтын атау: documents/doc_<stamp>_<uuid>.pdf"""
    ext = os.path.splitext(filename)[1].lower() or '.pdf'
    stamp = int(time.time())
    unique = uuid.uuid4().hex[:8]
    return f'documents/doc_{stamp}_{unique}{ext}'


def attestation_upload_to(instance, filename):
    """Қайталанбайтын атау: attestation/doc_<уақыт>_<uuid>.pdf"""
    ext = os.path.splitext(filename)[1].lower() or '.pdf'
    stamp = int(time.time())
    unique = uuid.uuid4().hex[:8]
    return f'attestation/doc_{stamp}_{unique}{ext}'


class AttestationNodeQuerySet(models.QuerySet):
    """Бір сұраудан ағаш жинауға көмектесетін queryset"""

    def attach_tree(self):
        """
        Барлық элементті бір сұрақпен оқып, түбелдік түйіндерді
        {category_id: [node, ...]} түрінде қайтарады.

        Әр түйінге `prefetched_children` және `prefetched_nodes`
        тіркеледі, сондықтан to_dict() қайта сұрақ жібермейді.
        """
        nodes = list(self)
        by_id = {}
        for node in nodes:
            node.prefetched_children = []
            by_id[node.pk] = node

        roots = []
        for node in nodes:
            parent = by_id.get(node.parent_id)
            if parent is None:
                roots.append(node)
            else:
                parent.prefetched_children.append(node)

        by_category = {}
        for node in roots:
            by_category.setdefault(node.category_id, []).append(node)
        return by_category


class AttestationNode(models.Model):
    """
    Аттестация блогының мазмұны — рекурсивтік ағаш.

    Бір ғана модель барлық 4 блок түріне қызмет етеді:
      item     — жол немесе бөлім тақырыбы (жоғарғы деңгей)
      group    — жыл / топ / бөлім (ішкі аккордеон)
      document — файлға сүйленетін құжат
    """
    KIND_ITEM = 'item'
    KIND_GROUP = 'group'
    KIND_DOCUMENT = 'document'
    KIND_CHOICES = [
        (KIND_ITEM, 'Тақырып (жол / бөлім)'),
        (KIND_GROUP, 'Топ (жыл / бөлім)'),
        (KIND_DOCUMENT, 'Құжат (файл)'),
    ]

    category = models.ForeignKey(
        AttestationCategory, on_delete=models.CASCADE,
        related_name='nodes', verbose_name='Санат'
    )
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, related_name='children',
        null=True, blank=True, verbose_name='Ата-атасы'
    )
    kind = models.CharField(
        'Түрі', max_length=20, choices=KIND_CHOICES, default=KIND_DOCUMENT
    )
    title = models.CharField('Атауы', max_length=255)
    subtitle = models.CharField(
        'Қосымша мәтін', max_length=150, blank=True,
        help_text='Мысалы жылдар аралығы: 2024–2027'
    )
    file = models.FileField(
        'Файл (PDF)', upload_to=attestation_upload_to,
        validators=[validate_pdf_file], blank=True, null=True,
        help_text='Тек PDF форматы, өлшемі 50 МБ-тан аспайды.'
    )
    link = models.URLField('Сілтеме', blank=True)
    order = models.PositiveIntegerField('Реттілік', default=0)
    is_open = models.BooleanField('Ашық күйінде', default=False)
    is_active = models.BooleanField('Көрсету', default=True)

    objects = AttestationNodeQuerySet.as_manager()

    class Meta:
        verbose_name = 'Аттестация элементі'
        verbose_name_plural = 'Аттестация элементтері'
        ordering = ['order', 'id']

    def __str__(self):
        prefix = '— ' if self.parent_id else ''
        return f'{prefix}{self.title}'

    @property
    def download_url(self):
        if self.file:
            return self.file.url
        return self.link or ''

    @property
    def file_url(self):
        """Клиентке арналған файл сілтемесі (/media/... немесе сыртқы URL)"""
        return self.download_url

    @property
    def has_file(self):
        return bool(self.file or self.link)

    @property
    def file_type(self):
        """Файл түрін анықтау (көрсетуге арналған)"""
        if self.file and self.file.name:
            name = self.file.name.lower()
            if name.endswith(('.doc', '.docx')):
                return 'word'
            elif name.endswith('.pdf'):
                return 'pdf'
            elif name.endswith(('.xls', '.xlsx')):
                return 'excel'
            elif name.endswith(('.ppt', '.pptx')):
                return 'powerpoint'
            elif name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                return 'image'
            elif name.endswith(('.zip', '.rar', '.7z')):
                return 'archive'
        if self.link:
            return 'link'
        return 'file'

    def to_dict(self):
        """JS рендерерге берілетін JSON құрылымы"""
        return {
            'id': self.pk,
            'title': self.title,
            'subtitle': self.subtitle,
            'kind': self.kind,
            'isOpen': self.is_open,
            'fileUrl': self.download_url,
            'file_url': self.file_url,
            'fileType': self.file_type,
            'hasFile': self.has_file,
            'children': [child.to_dict() for child in self.active_children],
        }

    @property
    def active_children(self):
        """Алдын ала жүктелген ағаш болмаса — дерекқордан оқиды"""
        attached = getattr(self, 'prefetched_children', None)
        if attached is not None:
            return attached
        return self.children.filter(is_active=True)


class AttestationDocument(models.Model):
    """Аттестация құжаттары (бір санатқа тиесілі)"""
    category = models.ForeignKey(
        AttestationCategory, on_delete=models.CASCADE,
        related_name='documents', verbose_name='Санат'
    )
    title = models.CharField('Атауы', max_length=255)
    description = models.TextField('Сипаттамасы', blank=True)
    file = models.FileField('Файл', upload_to='attestation/', blank=True, null=True,
                            help_text='PDF, Word, Excel, PPTX немесе басқа файлды жүктеңіз')
    link = models.URLField('Сілтеме (Google Drive т.б.)', blank=True,
                           help_text='Файл жүктемей, сыртқы сілтеме беру үшін')
    order = models.PositiveIntegerField(
        'Реттік нөмір', default=0,
        help_text='0 болса — реті автоматты (1, 2, 3...)'
    )
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Аттестация құжаты'
        verbose_name_plural = 'Аттестация құжаттары'
        ordering = ['order', '-created_at']


def zhetekshiler_upload_to(instance, filename):
    """Уникальды атау: zhetekshiler/doc_<stamp>_<uuid>.pdf"""
    ext = os.path.splitext(filename)[1].lower() or '.pdf'
    stamp = int(time.time())
    unique = uuid.uuid4().hex[:8]
    return f'zhetekshiler/doc_{stamp}_{unique}{ext}'


class ZhetekshilerDocument(models.Model):
    """Әдістемелік бірлестік жетекшілерінің PDF құжаттары"""

    title = models.CharField('Атауы', max_length=255)
    description = models.TextField('Сипаттама', blank=True)
    file = models.FileField(
        'PDF файлы', upload_to=zhetekshiler_upload_to,
        validators=[validate_pdf_file], blank=True, null=True,
        help_text='Тек PDF форматы, өлшемі 50 МБ-тан аспайды.'
    )
    order = models.PositiveIntegerField('Реттілік', default=0)
    created_at = models.DateTimeField('Қосылған уақыты', auto_now_add=True)

    class Meta:
        verbose_name = 'Жетекшілер құжаты (PDF)'
        verbose_name_plural = 'Жетекшілер құжаттары (PDF)'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def file_url(self):
        """Клиентке арналған файл сілтемесі"""
        if not self.file:
            return ''
        try:
            return self.file.url
        except ValueError:
            return ''

    @property
    def has_file(self):
        return bool(self.file)

    def to_dict(self):
        return {
            'id': self.pk,
            'title': self.title,
            'description': self.description,
            'file_url': self.file_url,
            'has_file': self.has_file,
        }

    def __str__(self):
        return self.title

    @property
    def download_url(self):
        """Файл немесе сілтемені қайтарады"""
        if self.file:
            return self.file.url
        return self.link or '#'

    @property
    def file_type(self):
        """Файл түрін анықтау (иконка үшін)"""
        if self.file and self.file.name:
            name = self.file.name.lower()
            if name.endswith(('.doc', '.docx')):
                return 'word'
            elif name.endswith('.pdf'):
                return 'pdf'
            elif name.endswith(('.xls', '.xlsx')):
                return 'excel'
            elif name.endswith(('.ppt', '.pptx')):
                return 'powerpoint'
            elif name.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                return 'image'
            elif name.endswith(('.zip', '.rar', '.7z')):
                return 'archive'
        if self.link:
            return 'link'
        return 'file'
