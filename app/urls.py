from django.urls import path
from django.views.generic import TemplateView
from . import views

app_name = 'app'

urlpatterns = [
    # Басты бет
    path('', views.index, name='index'),

    # Мектеп туралы
    path('about/', views.about, name='about'),

    # Жаңалықтар
    path('news/', views.news_list, name='news_list'),
    path('news/<slug:slug>/', views.news_detail, name='news_detail'),

    # Мұғалімдер
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('teachers/<slug:slug>/', views.teacher_detail, name='teacher_detail'),

    # Галерея
    path('gallery/', views.gallery, name='gallery'),
    path('gallery/<slug:slug>/', views.gallery_album, name='gallery_album'),

    # Құжаттар
    path('documents/', views.documents, name='documents'),

    # Байланыс
    path('contact/', views.contact, name='contact'),
    
    # Тәрбие жұмыстары (отдельные HTML страницы)
    path('tarbie/birtutas/', TemplateView.as_view(template_name='tarbie/birtutas.html'), name='tarbie_birtutas'),
    path('tarbie/zhospary/', TemplateView.as_view(template_name='tarbie/zhospary.html'), name='tarbie_zhospary'),
    path('tarbie/sharalar/', TemplateView.as_view(template_name='tarbie/sharalar.html'), name='tarbie_sharalar'),
    path('tarbie/ata-analar/', TemplateView.as_view(template_name='tarbie/ata_analar.html'), name='ata_analar'),
    path('tarbie/quqyq/', TemplateView.as_view(template_name='tarbie/quqyq.html'), name='quqyq'),
    path('tarbie/profilaktika/', TemplateView.as_view(template_name='tarbie/profilaktika.html'), name='profilaktika'),
    path('tarbie/synyp/', TemplateView.as_view(template_name='tarbie/synyp.html'), name='synyp'),
    path('tarbie/parlament/', TemplateView.as_view(template_name='tarbie/parlament.html'), name='parlament'),
    path('tarbie/adal-urpaq/', TemplateView.as_view(template_name='tarbie/adal_urpaq.html'), name='adal_urpaq'),
    path('tarbie/zhas-ulan/', TemplateView.as_view(template_name='tarbie/zhas_ulan.html'), name='zhas_ulan'),

    # Мектеп туралы (жеке HTML беттер)
    path('about/history/', TemplateView.as_view(template_name='about/history.html'), name='history'),
    path('about/administration/', TemplateView.as_view(template_name='about/administration.html'), name='administration'),
    path('about/kitapkhana/', TemplateView.as_view(template_name='about/kitapkhana.html'), name='kitapkhana'),
    path('about/askhana/', TemplateView.as_view(template_name='about/askhana.html'), name='askhana'),
    
    # Әдістемелік жұмыстар (жеке HTML беттер)
    path('method/magistr/', TemplateView.as_view(template_name='about/magistr.html'), name='magistr'),
    path('method/sanat/', TemplateView.as_view(template_name='about/sanat.html'), name='sanat'),
    path('method/zhetekshiler/', TemplateView.as_view(template_name='about/zhetekshiler.html'), name='zhetekshiler'),
    path('method/zhetistik/', TemplateView.as_view(template_name='about/zhetistik.html'), name='zhetistik'),

    # Үйірмелер
    path('club/<slug:slug>/', views.club_detail, name='club_detail'),

    # Қалған мануалдық HTML беттер
    path('parents-meeting/', TemplateView.as_view(template_name='pages/parents_meeting.html'), name='parents_meeting'),
    path('school-rules/', TemplateView.as_view(template_name='pages/school_rules.html'), name='school_rules'),
    path('med-kyzmet/', TemplateView.as_view(template_name='pages/med_kyzmet.html'), name='med_kyzmet'),
    path('psikholog/', TemplateView.as_view(template_name='pages/psikholog.html'), name='psikholog'),
    path('kamqorshy/', TemplateView.as_view(template_name='pages/kamqorshy.html'), name='kamqorshy'),
    path('logoped/', TemplateView.as_view(template_name='pages/logoped.html'), name='logoped'),
    path('logoped-okushy/', TemplateView.as_view(template_name='pages/logoped_okushy.html'), name='logoped_okushy'),
    path('defektolog/', TemplateView.as_view(template_name='pages/defektolog.html'), name='defektolog'),
    path('defektolog-okushy/', TemplateView.as_view(template_name='pages/defektolog_okushy.html'), name='defektolog_okushy'),
    path('timetable/', TemplateView.as_view(template_name='pages/timetable.html'), name='timetable'),
    path('rules/', TemplateView.as_view(template_name='pages/rules.html'), name='rules'),
    path('achievements/', TemplateView.as_view(template_name='pages/achievements.html'), name='achievements'),
    path('career/', TemplateView.as_view(template_name='pages/career.html'), name='career'),
    path('zhaz-2024/', TemplateView.as_view(template_name='pages/zhaz_2024.html'), name='zhaz_2024'),
    path('social-work/', TemplateView.as_view(template_name='pages/social_work.html'), name='social_work'),
    path('self-assessment/', TemplateView.as_view(template_name='pages/self_assessment.html'), name='self_assessment'),
    
    # МАД топтары
    path('mad-a/', TemplateView.as_view(template_name='pages/mad_a.html'), name='mad_a'),
    path('mad-ae/', TemplateView.as_view(template_name='pages/mad_ae.html'), name='mad_ae'),
    path('mad-b/', TemplateView.as_view(template_name='pages/mad_b.html'), name='mad_b'),
    path('mad-v/', TemplateView.as_view(template_name='pages/mad_v.html'), name='mad_v'),
    path('mad-g/', TemplateView.as_view(template_name='pages/mad_g.html'), name='mad_g'),
    path('mad-f/', TemplateView.as_view(template_name='pages/mad_f.html'), name='mad_f'),
    path('mad-d/', TemplateView.as_view(template_name='pages/mad_d.html'), name='mad_d'),
    path('mad-e/', TemplateView.as_view(template_name='pages/mad_e.html'), name='mad_e'),

    # Мақалалар (психология, әлеуметтік, мед., қамқоршылық)
    path('articles/<str:section>/', views.article_list, name='article_list'),
    path('articles/<str:section>/<slug:slug>/', views.article_detail, name='article_detail'),

    path('page/<slug:slug>/', views.static_page, name='static_page'),
]