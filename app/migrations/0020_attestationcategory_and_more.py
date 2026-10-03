import django.db.models.deletion
from django.db import migrations, models


DEFAULT_CATEGORY_NAME = 'ЖАЛПЫ СИПАТТАМА'


def create_default_categories(apps, schema_editor):
    """Әр оқу жылына «ЖАЛПЫ СИПАТТАМА» санатын жасайды және ескі
    жылға тігелген құжаттарды соған ауыстырады."""
    AttestationYear = apps.get_model('app', 'AttestationYear')
    AttestationCategory = apps.get_model('app', 'AttestationCategory')
    AttestationDocument = apps.get_model('app', 'AttestationDocument')

    for index, year in enumerate(AttestationYear.objects.all(), start=1):
        category, _ = AttestationCategory.objects.get_or_create(
            year=year,
            name=DEFAULT_CATEGORY_NAME,
            defaults={'order': index, 'is_active': True},
        )
        AttestationDocument.objects.filter(category__isnull=True, year=year).update(
            category=category
        )


def link_documents_to_categories(apps, schema_editor):
    """category=None қалған құжаттарды жылының санатына жасайды (қосымша сақтық)."""
    AttestationYear = apps.get_model('app', 'AttestationYear')
    AttestationCategory = apps.get_model('app', 'AttestationCategory')
    AttestationDocument = apps.get_model('app', 'AttestationDocument')

    for year in AttestationYear.objects.all():
        category = AttestationCategory.objects.filter(year=year).first()
        if category is None:
            category = AttestationCategory.objects.create(
                year=year, name=DEFAULT_CATEGORY_NAME, is_active=True
            )
        AttestationDocument.objects.filter(category__isnull=True).update(category=category)


def unlink_documents_from_years(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0019_attestationyear_attestationdocument'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttestationCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Мысалы: ЖАЛПЫ СИПАТТАМА', max_length=200, verbose_name='Атауы')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Реттілік')),
                ('is_open', models.BooleanField(default=False, help_text='Бет ашылғанда блок түбелдегі күйде болады', verbose_name='Ашық күйінде')),
                ('is_active', models.BooleanField(default=True, verbose_name='Көрсету')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='categories', to='app.attestationyear', verbose_name='Оқу жылы')),
            ],
            options={
                'verbose_name': 'Аттестация санаты',
                'verbose_name_plural': 'Аттестация санаттары',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.AddField(
            model_name='attestationdocument',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='app.attestationcategory', verbose_name='Санат'),
        ),
        migrations.RunPython(create_default_categories, unlink_documents_from_years),
        migrations.RemoveField(
            model_name='attestationdocument',
            name='year',
        ),
        migrations.RunPython(link_documents_to_categories, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='attestationdocument',
            name='category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='documents', to='app.attestationcategory', verbose_name='Санат'),
        ),
        migrations.AlterField(
            model_name='attestationdocument',
            name='order',
            field=models.PositiveIntegerField(default=0, help_text='0 болса — реті автоматты (1, 2, 3...)', verbose_name='Реттік нөмір'),
        ),
    ]