from datetime import datetime
from typing import Dict, List, Type
from ninja import ModelSchema, Schema

from work_in_progress.app.models import Company, Contato, Processo


class LoginSchema(Schema):
    username: str = "username"
    password: str = "password"


class LoginSuccess(Schema):
    message: str = "Logged in succesfully"
    x_api_key: str = "010302039e09djsja-anasdjasiaosqos"


class Default200(Schema):
    message: str = "Ok"


class Default204(Schema):
    message: str = "No content"


class Default400(Schema):
    message: str = "Bad Request"


class Default401(Schema):
    message: str = "Unauthorized"


class Default403(Schema):
    message: str = "Forbidden"


class Default404(Schema):
    message: str = "Not Found"


class Default500(Schema):
    message: str = "Internal Server Error"


login_responses_dict: Dict[int, Type[Schema]] = {
    200: LoginSuccess,
    401: Default401,
    500: Default500,
}

responses_dict: Dict[int, Type[Schema]] = {
    200: Default200,
    401: Default401,
    204: Default204,
    400: Default400,
    403: Default403,
    404: Default404,
    500: Default500,
}


class ContatoSchema(ModelSchema):
    class Config:
        model = Contato
        model_exclude = ["criado_por", "contato_id"]


class ContatosSchema(Schema):
    contatos: List[ContatoSchema] = [
        ContatoSchema(
            nome="Nome teste",
            contato_id="1",
            endereco="Rua teste",
            numero="123",
            complemento="",
            bairro="Bairro teste",
            cidade="Cidade teste",
            estado="Estado teste",
            cep="12345678",
            telefone="12345678",
            email_responsavel="responsavel@teste.com",
            email_cobranca="financeiro@teste.com",
        )
    ]


class CompanySchema(ModelSchema):
    class Config:
        model = Company
        model_exclude = ["criado_por", "company_id"]


class CompaniesSchema(Schema):
    companies: List[CompanySchema] = [
        CompanySchema(
            company_id="1",
            cnpj="123456789",
            razao_social="Razão social teste",
            nome_fantasia="Nome fantasia teste",
            inscricao_estadual="123456789",
            inscricao_municipal="123456789",
            criado_em=datetime.now(),
            atualizado_em=datetime.now(),
            ativo=True,
            contato_id="1",
        )
    ]


class ProcessoSchema(ModelSchema):
    class Config:
        model = Processo
        model_exclude = ["criado_por", "processo_id"]


class ProcessosSchema(Schema):
    processos: List[ProcessoSchema] = [
        ProcessoSchema(
            processo_id="1",
            advogado_responsavel="Advogado responsável teste",
            cliente="Cliente teste",
            numero_processo="123456789",
            vara="Vara teste",
            comarca="Comarca teste",
            estado="Estado teste",
            status="Status teste",
            fase="Fase teste",
            valor_causa=220.0,
            valor_condenacao=230.0,
            valor_honorario=240.0,
            valor_preposto=250.0,
            valor_total=260.0,
            data_distribuicao=datetime.now(),
            criado_em=datetime.now(),
            atualizado_em=datetime.now(),
        )
    ]


response_get_processos = responses_dict.copy()
response_get_processos.update({200: ProcessosSchema})
response_get_companies = responses_dict.copy()
response_get_companies.update({200: CompaniesSchema})
response_get_contatos = responses_dict.copy()
response_get_contatos.update({200: ContatosSchema})
