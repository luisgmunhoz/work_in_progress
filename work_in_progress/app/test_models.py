import uuid

from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from work_in_progress.app.models import models

from .models import Company, Contato, Processo, SystemUser


class SystemUserModelTest(TestCase):
    def setUp(self) -> None:
        self.user = SystemUser.objects.create_user(
            username="testuser",
            password="testpass",
        )

    def test_secret_field(self) -> None:
        """
        Test that the secret field is generated with a UUID and is unique.
        """
        self.assertIsNotNone(self.user.secret)
        self.assertEqual(len(self.user.secret), 32)
        self.assertIsInstance(uuid.UUID(self.user.secret), uuid.UUID)
        self.assertRaises(
            IntegrityError,
            SystemUser.objects.create,
            secret=self.user.secret,
        )

    def test_system_users_groups_related_name(self) -> None:
        """
        Test that the related name of the groups field
        in the SystemUser model is set to 'system_users_groups'.
        """
        field = SystemUser._meta.get_field("groups")
        self.assertEqual(field.remote_field.related_name, "system_users_groups")

    def test_system_users_permissions_related_name(self) -> None:
        """
        Test that the related name of the user_permissions field in
        the SystemUser model is set to 'system_users_permissions'.
        """
        field = SystemUser._meta.get_field("user_permissions")
        self.assertEqual(field.remote_field.related_name, "system_users_permissions")


class ContatoModelTest(TestCase):
    def setUp(self) -> None:
        self.user = SystemUser.objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.contato = Contato.objects.create(
            nome="Test Contact",
            endereco="Test Address",
            numero="123",
            complemento="Test Complement",
            bairro="Test Neighborhood",
            cidade="Test City",
            estado="Test State",
            cep="12345678",
            telefone="1234567890",
            email_responsavel="test@test.com",
            email_cobranca="test@test.com",
            criado_por=self.user,
        )

    def test_contato_id_field(self) -> None:
        """
        Test that the contato_id field is generated with a UUID and is unique.
        """
        self.assertIsNotNone(self.contato.contato_id)
        self.assertEqual(len(self.contato.contato_id), 32)
        self.assertIsInstance(uuid.UUID(self.contato.contato_id), uuid.UUID)
        self.assertRaises(
            IntegrityError,
            Contato.objects.create,
            contato_id=self.contato.contato_id,
        )

    def test_contato_nome_field(self) -> None:
        """
        Test that the nome field is required and cannot be blank or null.
        """
        field = Contato._meta.get_field("nome")
        self.assertFalse(field.blank)
        self.assertFalse(field.null)

    def test_contato_criado_por_field(self) -> None:
        """
        Test that the criado_por field is a foreign key to the
        SystemUser model with a related name of 'contatos'.
        """
        field = Contato._meta.get_field("criado_por")
        self.assertIsInstance(field, models.ForeignKey)
        self.assertEqual(field.remote_field.model, SystemUser)
        self.assertEqual(field.remote_field.related_name, "contatos")


class CompanyModelTest(TestCase):
    def setUp(self) -> None:
        self.user = SystemUser.objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.contato = Contato.objects.create(
            nome="Test Contact",
            endereco="Test Address",
            numero="123",
            complemento="Test Complement",
            bairro="Test Neighborhood",
            cidade="Test City",
            estado="Test State",
            cep="12345678",
            telefone="1234567890",
            email_responsavel="test@test.com",
            email_cobranca="test@test.com",
            criado_por=self.user,
        )
        self.company = Company.objects.create(
            cnpj="12345678901234",
            razao_social="Test Company",
            nome_fantasia="Test Company",
            inscricao_estadual="123456789",
            inscricao_municipal="123456789",
            criado_por=self.user,
            contato=self.contato,
        )

    def test_company_id_field(self) -> None:
        """
        Test that the company_id field is generated with a UUID and is unique.
        """
        self.assertIsNotNone(self.company.company_id)
        self.assertEqual(len(self.company.company_id), 32)
        self.assertIsInstance(uuid.UUID(self.company.company_id), uuid.UUID)
        self.assertRaises(
            IntegrityError,
            Company.objects.create,
            company_id=self.company.company_id,
        )

    def test_company_criado_por_field(self) -> None:
        """
        Test that the criado_por field is a foreign key to
        the SystemUser model with a related name of 'companies'.
        """
        field = Company._meta.get_field("criado_por")
        self.assertIsInstance(field, models.ForeignKey)
        self.assertEqual(field.remote_field.model, SystemUser)
        self.assertEqual(field.remote_field.related_name, "companies")

    def test_company_contato_field(self) -> None:
        """
        Test that the contato field is a foreign key to the
        Contato model with a related name of 'companies'.
        """
        field = Company._meta.get_field("contato")
        self.assertIsInstance(field, models.ForeignKey)
        self.assertEqual(field.remote_field.model, Contato)
        self.assertEqual(field.remote_field.related_name, "companies")


class ProcessoModelTest(TestCase):
    def setUp(self) -> None:
        self.user = SystemUser.objects.create_user(
            username="testuser",
            password="testpass",
        )
        self.contato = Contato.objects.create(
            nome="Test Contact",
            endereco="Test Address",
            numero="123",
            complemento="Test Complement",
            bairro="Test Neighborhood",
            cidade="Test City",
            estado="Test State",
            cep="12345678",
            telefone="1234567890",
            email_responsavel="test@test.com",
            email_cobranca="test@test.com",
            criado_por=self.user,
        )
        self.processo = Processo.objects.create(
            advogado_responsavel="Test Lawyer",
            cliente="Test Client",
            numero_processo="123456789",
            vara="Test Court",
            comarca="Test District",
            estado="Test State",
            status="Test Status",
            fase="Test Phase",
            valor_causa=1000.0,
            valor_condenacao=500.0,
            valor_honorario=200.0,
            valor_preposto=100.0,
            valor_total=800.0,
            data_distribuicao=timezone.now(),
            criado_por=self.user,
        )

    def test_processo_id_field(self) -> None:
        """
        Test that the processo_id field is generated with a UUID and is unique.
        """
        self.assertIsNotNone(self.processo.processo_id)
        self.assertEqual(len(self.processo.processo_id), 32)
        self.assertIsInstance(uuid.UUID(self.processo.processo_id), uuid.UUID)
        self.assertRaises(
            IntegrityError,
            Processo.objects.create,
            processo_id=self.processo.processo_id,
        )

    def test_processo_criado_por_field(self) -> None:
        """
        Test that the criado_por field is a foreign key to the SystemUser
        model with a related name of 'processos'.
        """
        field = Processo._meta.get_field("criado_por")
        self.assertIsInstance(field, models.ForeignKey)
        self.assertEqual(field.remote_field.model, SystemUser)
        self.assertEqual(field.remote_field.related_name, "processos")

    def test_processo_valor_fields(self) -> None:
        """
        Test that the valor fields are required and cannot be null.
        """
        valor_fields = [
            "valor_causa",
            "valor_condenacao",
            "valor_honorario",
            "valor_preposto",
            "valor_total",
        ]
        for field_name in valor_fields:
            field = Processo._meta.get_field(field_name)
            self.assertFalse(field.blank)
            self.assertFalse(field.null)
