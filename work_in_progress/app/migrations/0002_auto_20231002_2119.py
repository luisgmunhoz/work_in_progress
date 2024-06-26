# Generated by Django 3.1.1 on 2023-10-02 21:19

import django.db.models.deletion
from django.db import migrations, models

import work_in_progress.app.models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Contato",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("endereco", models.CharField(max_length=100)),
                ("numero", models.CharField(max_length=100)),
                ("complemento", models.CharField(max_length=100)),
                ("bairro", models.CharField(max_length=100)),
                ("cidade", models.CharField(max_length=100)),
                ("estado", models.CharField(max_length=100)),
                ("cep", models.CharField(max_length=100)),
                ("telefone", models.CharField(max_length=100)),
                ("email_responsavel", models.CharField(max_length=100)),
                ("email_cobranca", models.CharField(max_length=100)),
            ],
        ),
        migrations.AlterField(
            model_name="systemuser",
            name="secret",
            field=models.CharField(
                default=work_in_progress.app.models.get_new_uuid_hex,
                editable=False,
                max_length=100,
                unique=True,
            ),
        ),
        migrations.CreateModel(
            name="Processo",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("advogado_responsavel", models.CharField(max_length=100)),
                ("cliente", models.CharField(max_length=100)),
                ("numero_processo", models.CharField(max_length=100)),
                ("vara", models.CharField(max_length=100)),
                ("comarca", models.CharField(max_length=100)),
                ("estado", models.CharField(max_length=100)),
                ("status", models.CharField(max_length=100)),
                ("fase", models.CharField(max_length=100)),
                ("valor_causa", models.FloatField()),
                ("valor_condenacao", models.FloatField()),
                ("valor_honorario", models.FloatField()),
                ("valor_preposto", models.FloatField()),
                ("valor_total", models.FloatField()),
                ("data_distribuicao", models.DateTimeField()),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("ativo", models.BooleanField(default=True)),
                (
                    "criado_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="processos",
                        to="app.systemuser",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Company",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cnpj", models.CharField(max_length=100)),
                ("razao_social", models.CharField(max_length=100)),
                ("nome_fantasia", models.CharField(max_length=100)),
                ("inscricao_estadual", models.CharField(max_length=100)),
                ("inscricao_municipal", models.CharField(max_length=100)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
                ("ativo", models.BooleanField(default=True)),
                (
                    "contato",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="companies",
                        to="app.contato",
                    ),
                ),
                (
                    "criado_por",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="companies",
                        to="app.systemuser",
                    ),
                ),
            ],
        ),
    ]
