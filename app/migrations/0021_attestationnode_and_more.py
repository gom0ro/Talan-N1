import django.db.models.deletion
from django.db import migrations, models


def documents_to_nodes(apps, schema_editor):
    """Ескі AttestationDocument жазбаларын AttestationNode ағашына ауыстырады."""
    AttestationCategory = apps.get_model('app', 'AttestationCategory')
    AttestationNode = apps.get_model('app', 'AttestationNode')
    AttestationDocument = apps.get_model('app', 'AttestationDocument')

    for doc in AttestationDocument.objects.all().select_related('category'):
        AttestationNode.objects.create(
            category_id=doc.category_id,
            parent=None,
            kind='document',
            title=doc.title,
            subtitle=doc.description or '',
            file=doc.file.name or '',
            link=doc.link or '',
            order=doc.order or 0,
            is_active=True,
        )


def nodes_to_documents(apps, schema_editor):
    """Кері қайтару: тек түбелдегі құжат түйіндері AttestationDocument болуы тиіс."""
    AttestationDocument = apps.get_model('app', 'AttestationDocument')
    AttestationNode = apps.get_model('app', 'AttestationNode')

    AttestationDocument.objects.all().delete()
    for node in AttestationNode.objects.filter(parent__isnull=True, kind='document'):
        AttestationDocument.objects.create(
            category_id=node.category_id,
            title=node.title,
            description=node.subtitle or '',
            file=node.file.name or '',
            link=node.link or '',
            order=node.order or 0,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0020_attestationcategory_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='AttestationNode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kind', models.CharField(choices=[('item', 'Тақырып (жол / бөлім)'), ('group', 'Топ (жыл / бөлім)'), ('document', 'Құжат (файл)')], default='document', max_length=20, verbose_name='Түрі')),
                ('title', models.CharField(max_length=255, verbose_name='Атауы')),
                ('subtitle', models.CharField(blank=True, help_text='Мысалы жылдар аралығы: 2024–2027', max_length=150, verbose_name='Қосымша мәтін')),
                ('file', models.FileField(blank=True, null=True, upload_to='attestation/', verbose_name='Файл')),
                ('link', models.URLField(blank=True, verbose_name='Сілтеме')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Реттілік')),
                ('is_open', models.BooleanField(default=False, verbose_name='Ашық күйінде')),
                ('is_active', models.BooleanField(default=True, verbose_name='Көрсету')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='nodes', to='app.attestationcategory', verbose_name='Санат')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='app.attestationnode', verbose_name='Ата-атасы')),
            ],
            options={
                'verbose_name': 'Аттестация элементі',
                'verbose_name_plural': 'Аттестация элементтері',
                'ordering': ['order', 'id'],
            },
        ),
        migrations.AddField(
            model_name='attestationcategory',
            name='type',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Стандартная таблица'), (2, 'Таблица по годам'), (3, 'Таблица с вложенными годами в ячейке'), (4, 'Многоуровневая таблица')], default=1, help_text='Сайттағы кесте түрін анықтайды', verbose_name='Блок түрі'),
        ),
        migrations.RunPython(documents_to_nodes, nodes_to_documents),
    ]