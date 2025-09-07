from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SiteFeature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('icon_class', models.CharField(max_length=100)),
                ('sort_order', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='SocialLink',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('facebook', 'Facebook'), ('instagram', 'Instagram'), ('twitter', 'Twitter'), ('linkedin', 'LinkedIn'), ('youtube', 'YouTube'), ('whatsapp', 'WhatsApp')], max_length=50)),
                ('url', models.URLField(max_length=500)),
                ('icon_class', models.TextField(blank=True, max_length=100, null=True)),
            ],
        ),
    ]
