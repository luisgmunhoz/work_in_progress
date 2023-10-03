# Generated by Django 3.1.1 on 2023-10-02 22:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0005_auto_20231002_2238"),
    ]

    operations = [
        migrations.AlterField(
            model_name="contato",
            name="criado_por",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="contatos",
                to="app.systemuser",
            ),
        ),
    ]