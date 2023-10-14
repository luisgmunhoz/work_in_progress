from typing import Optional

from ninja import NinjaAPI
from ninja.security import APIKeyHeader

from work_in_progress.app.models import Company, Contato, Processo, SystemUser
from work_in_progress.app.schemas import (
    CompanySchema,
    ContatoSchema,
    LoginSchema,
    ProcessoSchema,
    login_responses_dict,
    response_get_companies,
    response_get_contatos,
    response_get_processos,
    responses_dict,
)


class ApiKey(APIKeyHeader):
    param_name = "X-API-Key"

    def authenticate(self, request, key: Optional[str]) -> Optional[SystemUser]:
        if key in SystemUser.objects.values_list("secret", flat=True):
            system_user = SystemUser.objects.get(secret=key)
            return system_user
        raise HTTPException(401, "Unauthorized")


header_key = ApiKey()

api = NinjaAPI(
    title="Work in progress API",
    version="0.0.1",
    description="Work in progress",
    csrf=True,
    urls_namespace="api",
    auth=header_key,
)


class HTTPException(Exception):
    status_code: int
    message: str

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


@api.exception_handler(Exception)
def base_exception(request, exc):
    try:
        exception_message = exc.message if exc.message else "Internal server error"
    except Exception:
        exception_message = "Internal server error"
    try:
        status = exc.status_code if exc.status_code else 500
    except Exception:
        status = 500
    return api.create_response(request, {"message": exception_message}, status=status)


def authenticate(request, username: str, password: str) -> Optional[str]:
    try:
        user = SystemUser.objects.get(username=username)
        if user.password == password:
            return user.secret
        else:
            raise HTTPException(401, "Invalid Credentials")

    except SystemUser.DoesNotExist:
        raise HTTPException(401, "Invalid Credentials")


@api.post("/login", auth=None, response=login_responses_dict, tags=["login"])
def login(request, data: LoginSchema):
    """
    Logar no sistema

    - **username**: username
    - **password**: password

    """
    x_api_key = authenticate(request, username=data.username, password=data.password)
    if x_api_key is not None:
        return 200, {"message": "Logged in succesfully", "x_api_key": x_api_key}
    else:
        raise HTTPException(401, "Invalid Credentials")


@api.get("/contatos", response=response_get_contatos, tags=["contatos"])
def get_contatos(request):
    if request.auth.is_superuser:
        contatos = Contato.objects.all()
    else:
        contatos = Contato.objects.filter(criado_por=request.auth)
    if contatos:
        return 200, {
            "contatos": [ContatoSchema.from_orm(contato).dict() for contato in contatos]
        }
    else:
        return 204, {"message": "No content"}


@api.post("/contatos", response=responses_dict, tags=["contatos"])
def create_contato(request, data: ContatoSchema):
    try:
        contato = Contato.objects.get(email_responsavel=data.email_responsavel)
        raise HTTPException(400, "Contato já existe")
    except Contato.DoesNotExist:
        contato = Contato.objects.create(**data.dict(), criado_por=request.auth)
        return {
            "message": f"Contato de nome {contato.nome} "
            f"e id {contato.contato_id} criado"
        }


@api.put(
    "/contatos/{contato_id}",
    response=responses_dict,
    tags=["contatos"],
)
def update_contato(request, contato_id: str, data: ContatoSchema):
    try:
        contato = Contato.objects.get(contato_id=contato_id)
    except Exception:
        raise HTTPException(404, "Contato não existe")
    try:
        contato_responsavel = Contato.objects.get(
            email_responsavel=data.email_responsavel
        )
    except Contato.DoesNotExist:
        contato_responsavel = None
    if contato_responsavel and contato_responsavel.contato_id != contato.contato_id:
        raise HTTPException(400, "Contato já existe")

    contato.nome = data.nome
    contato.endereco = data.endereco
    contato.numero = data.numero
    contato.complemento = data.complemento
    contato.bairro = data.bairro
    contato.cidade = data.cidade
    contato.estado = data.estado
    contato.cep = data.cep
    contato.telefone = data.telefone
    contato.email_responsavel = data.email_responsavel
    contato.email_cobranca = data.email_cobranca
    contato.save()
    return {"message": f"Contato de nome {contato.nome} e id {contato_id} atualizado"}


@api.delete(
    "/contatos/{contato_id}",
    response=responses_dict,
    tags=["contatos"],
)
def delete_contato(request, contato_id: str):
    try:
        contato = Contato.objects.get(contato_id=contato_id)
    except Contato.DoesNotExist:
        raise HTTPException(404, "Contato não existe, certeza que este contato existe?")
    contato.delete()
    return {"message": f"Contato de nome {contato.nome} e id {contato_id} deletado"}


@api.get(
    "/companies",
    response=response_get_companies,
    tags=["companies"],
)
def get_companies(request):
    if request.auth.is_superuser:
        companies = Company.objects.all()
    else:
        companies = Company.objects.filter(criado_por=request.auth)
    if companies:
        return 200, {
            "companies": [
                CompanySchema.from_orm(company).dict() for company in companies
            ]
        }
    else:
        return 204, {"message": "No content"}


@api.post(
    "/companies",
    response=responses_dict,
    tags=["companies"],
)
def create_company(request, data: CompanySchema):
    try:
        company = Company.objects.get(cnpj=data.cnpj)
        if company:
            raise HTTPException(400, "Company já existe")
    except Company.DoesNotExist:
        try:
            contato = Contato.objects.get(contato_id=data.contato_id)
        except Contato.DoesNotExist:
            raise HTTPException(404, "Contato não existe")

        try:
            company = Company.objects.create(
                cnpj=data.cnpj,
                razao_social=data.razao_social,
                nome_fantasia=data.nome_fantasia,
                inscricao_estadual=data.inscricao_estadual,
                inscricao_municipal=data.inscricao_municipal,
                contato=contato,
                criado_por=request.auth,
            )
            return {
                "message": "Company de nome "
                f"{company.nome_fantasia} e id {company.company_id} criada"
            }
        except Exception as e:
            raise HTTPException(400, str(e))


@api.put(
    "/companies/{company_id}",
    response=responses_dict,
    tags=["companies"],
)
def update_companies(request, company_id: str, data: CompanySchema):
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        raise HTTPException(404, "Company não existe")
    try:
        contato = Contato.objects.get(contato_id=data.contato_id)
    except Contato.DoesNotExist:
        raise HTTPException(404, "Contato não existe")

    company.contato = contato if contato else company.contato
    company.cnpj = data.cnpj
    company.razao_social = data.razao_social
    company.nome_fantasia = data.nome_fantasia
    company.inscricao_estadual = data.inscricao_estadual
    company.inscricao_municipal = data.inscricao_municipal
    company.save()
    return {
        "message": f"Company de nome {company.nome_fantasia} "
        f"e id {company.company_id} atualizada"
    }


@api.delete(
    "/companies/{company_id}",
    response=responses_dict,
    tags=["companies"],
)
def delete_companies(request, company_id: str):
    try:
        company = Company.objects.get(company_id=company_id)
    except Company.DoesNotExist:
        raise HTTPException(404, "Company não existe, certeza que esta company existe?")
    company.delete()
    return {
        "message": f"Company de nome {company.nome_fantasia} e id {company_id} deletada"
    }


@api.get(
    "/processos",
    response=response_get_processos,
    tags=["processos"],
)
def get_processos(request):
    if request.auth.is_superuser:
        processos = Processo.objects.all()
    else:
        processos = Processo.objects.filter(criado_por=request.auth)
    if processos:
        return 200, {
            "processos": [
                ProcessoSchema.from_orm(processo).dict() for processo in processos
            ]
        }
    else:
        return 204, {"message": "No content"}


@api.post(
    "/processos",
    response=responses_dict,
    tags=["processos"],
)
def create_processo(request, data: ProcessoSchema):
    processo = Processo.objects.create(**data.dict(), criado_por=request.auth)
    return {
        "message": f"Processo de numero {processo.numero_processo} "
        f"e id {processo.processo_id} e criado"
    }


@api.put(
    "/processos/{processo_id}",
    response=responses_dict,
    tags=["processos"],
)
def update_processo(request, processo_id: str, data: ProcessoSchema):
    processo = Processo.objects.get(processo_id=processo_id)
    processo.advogado_responsavel = data.advogado_responsavel
    processo.cliente = data.cliente
    processo.numero_processo = data.numero_processo
    processo.vara = data.vara
    processo.comarca = data.comarca
    processo.estado = data.estado
    processo.status = data.status
    processo.fase = data.fase
    processo.valor_causa = data.valor_causa
    processo.valor_condenacao = data.valor_condenacao
    processo.valor_honorario = data.valor_honorario
    processo.valor_preposto = data.valor_preposto
    processo.valor_total = data.valor_total
    processo.data_distribuicao = data.data_distribuicao
    processo.save()
    return {
        "message": f"Processo de numero {processo.numero_processo} "
        f"e id {processo.processo_id} atualizado"
    }


@api.delete(
    "/processos/{processo_id}",
    response=responses_dict,
    tags=["processos"],
)
def delete_processo(request, processo_id: str):
    try:
        processo = Processo.objects.get(processo_id=processo_id)
    except Processo.DoesNotExist:
        raise HTTPException(
            404, "Processo não existe, certeza que este processo existe?"
        )
    processo.delete()
    return {
        "message": f"Processo de numero {processo.numero_processo} "
        f"e id {processo_id}  deletado"
    }
