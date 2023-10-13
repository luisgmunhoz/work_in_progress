from datetime import datetime
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
def get_new_uuid_hex():
    return f"{uuid.uuid4().hex}"


class SystemUser(AbstractUser):
    secret: str = models.CharField(
        max_length=255,
        default=get_new_uuid_hex,
        editable=False,
        unique=True,
    )

    class Meta:
        db_table = "system_user"


SystemUser._meta.get_field("groups").remote_field.related_name = "system_users_groups"
SystemUser._meta.get_field(
    "user_permissions"
).remote_field.related_name = "system_users_permissions"


class Contato(models.Model):
    contato_id: str = models.CharField(
        max_length=255,
        default=get_new_uuid_hex,
        editable=False,
        unique=True,
        primary_key=True,
    )
    nome: str = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        verbose_name="nome do contato",
        default="nome",
    )
    endereco: str = models.CharField(max_length=255)
    numero: str = models.CharField(max_length=255)
    complemento: str = models.CharField(max_length=255)
    bairro: str = models.CharField(max_length=255)
    cidade: str = models.CharField(max_length=255)
    estado: str = models.CharField(max_length=255)
    cep: str = models.CharField(max_length=255)
    telefone: str = models.CharField(max_length=255)
    email_responsavel: str = models.CharField(max_length=255)
    email_cobranca: str = models.CharField(max_length=255)
    criado_por: SystemUser = models.ForeignKey(
        SystemUser,
        on_delete=models.CASCADE,
        related_name="contatos",
    )


class Company(models.Model):
    company_id: str = models.CharField(
        max_length=255,
        default=get_new_uuid_hex,
        editable=False,
        unique=True,
        primary_key=True,
    )
    cnpj: str = models.CharField(max_length=255)
    razao_social: str = models.CharField(max_length=255)
    nome_fantasia: str = models.CharField(max_length=255)
    inscricao_estadual: str = models.CharField(max_length=255)
    inscricao_municipal: str = models.CharField(max_length=255)
    criado_por: SystemUser = models.ForeignKey(
        SystemUser, on_delete=models.CASCADE, related_name="companies"
    )
    criado_em: datetime = models.DateTimeField(auto_now_add=True)
    atualizado_em: datetime = models.DateTimeField(auto_now=True)
    ativo: bool = models.BooleanField(default=True)
    contato: Contato = models.ForeignKey(
        Contato, on_delete=models.CASCADE, related_name="companies"
    )


class Processo(models.Model):
    processo_id: str = models.CharField(
        max_length=255,
        default=get_new_uuid_hex,
        editable=False,
        unique=True,
        primary_key=True,
    )
    advogado_responsavel: str = models.CharField(max_length=255)
    cliente: str = models.CharField(max_length=255)
    numero_processo: str = models.CharField(max_length=255)
    vara: str = models.CharField(max_length=255)
    comarca: str = models.CharField(max_length=255)
    estado: str = models.CharField(max_length=255)
    status: str = models.CharField(max_length=255)
    fase: str = models.CharField(max_length=255)
    valor_causa: float = models.FloatField()
    valor_condenacao: float = models.FloatField()
    valor_honorario: float = models.FloatField()
    valor_preposto: float = models.FloatField()
    valor_total: float = models.FloatField()
    data_distribuicao: datetime = models.DateTimeField()
    criado_por: SystemUser = models.ForeignKey(
        SystemUser, on_delete=models.CASCADE, related_name="processos"
    )
    criado_em: datetime = models.DateTimeField(auto_now_add=True)
    atualizado_em: datetime = models.DateTimeField(auto_now=True)
    ativo: bool = models.BooleanField(default=True)
