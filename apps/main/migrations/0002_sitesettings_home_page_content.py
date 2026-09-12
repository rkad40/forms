from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='home_page_content',
            field=models.TextField(
                blank=True,
                help_text='Content displayed on the public home page.',
                verbose_name='Home Page Content',
            ),
        ),
    ]
