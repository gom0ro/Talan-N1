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
    subject = models.CharField('Лауазымы / Пәні', max_length=150)
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
    image = models.ImageField('Сурет', upload_to='gallery/photos/')
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
    """Құжаттар"""
    title = models.CharField('Атауы', max_length=255)
    file = models.FileField('Файл', upload_to='documents/')
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
