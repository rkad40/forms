from django.db import migrations, models
import django.db.models.deletion
import django.core.validators


def add_existing_home_page_link(apps, schema_editor):
    SiteSettings = apps.get_model("main", "SiteSettings")
    HomePageLink = apps.get_model("main", "HomePageLink")
    for site in SiteSettings.objects.all():
        HomePageLink.objects.get_or_create(
            site_settings=site,
            title="OCIA Participant Form",
            defaults={
                "description": "Open the OCIA participant form.",
                "url": "/ocia/participant/",
                "rank": 0,
                "verbosity": 0,
                "active": True,
            },
        )


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0002_sitesettings_home_page_content"),
    ]

    operations = [
        migrations.CreateModel(
            name="HomePageLink",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.CharField(blank=True, max_length=500)),
                ("url", models.CharField(help_text="Use a root-relative path such as /ocia/participant/ or a full URL.", max_length=500)),
                ("rank", models.PositiveIntegerField(db_index=True, default=0, validators=[django.core.validators.MinValueValidator(0)])),
                ("verbosity", models.PositiveSmallIntegerField(choices=[(0, "Everyone"), (1, "Staff"), (2, "Admin")], default=0, help_text="Minimum access level required to show this link.")),
                ("active", models.BooleanField(default=True)),
                ("site_settings", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="home_page_links", to="main.sitesettings")),
            ],
            options={"ordering": ("rank", "title", "pk")},
        ),
        migrations.AddConstraint(
            model_name="homepagelink",
            constraint=models.CheckConstraint(
                condition=models.Q(("verbosity__gte", 0), ("verbosity__lte", 2)),
                name="main_homepagelink_valid_verbosity",
            ),
        ),
        migrations.RunPython(add_existing_home_page_link, migrations.RunPython.noop),
    ]
