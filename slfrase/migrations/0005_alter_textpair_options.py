# Generated by Django 4.2 on 2023-04-24 19:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("slfrase", "0004_alter_studystate_options_studystate_answer_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="textpair",
            options={"ordering": ("-created_ts",)},
        ),
    ]