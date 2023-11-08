from typing import Any, Dict, List, Optional, Tuple, Union

import jwt
from django.db.models import QuerySet
from ninja import NinjaAPI
from ninja.security import HttpBearer
from requests import Request

from work_in_progress.app.models import Company, Contato, Processo, Produto, SystemUser
from work_in_progress.app.schemas import (
    CompanySchema,
    ContatoSchema,
    LoginSchema,
    ProcessoSchema,
    ProdutoSchema,
    login_responses_dict,
    response_get_companies,
    response_get_contatos,
    response_get_processos,
    response_get_produtos,
    responses_dict,
)
from work_in_progress.settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


class JWTAuth(HttpBearer):
    """
    JWTAuth class that extends HttpBearer.
    It overrides the authenticate method to provide JWT token based authentication.
    """

    def authenticate(self, request: Request, token: str) -> Optional[SystemUser]:
        """
        Authenticate the request using the provided JWT token.

        Args:
            request: The request instance.
            token: A string representing the Bearer token.

        Returns:
            The SystemUser instance associated with the provided token.

        Raises:
            HTTPException: If the token is not properly formatted,
            does not contain a 'sub' claim, or is not a valid JWT token.
        """
        try:
            if token.startswith("Bearer "):
                token = token[7:]
            else:
                raise HTTPException(
                    message="Token mal formatado, deve haver o prefixo Bearer",
                    status_code=401,
                )
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
                verify=True,
                options={"verify_exp": True},
                expire=ACCESS_TOKEN_EXPIRE_MINUTES,
            )
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(401, "Unauthorized")
            user = SystemUser.objects.get(id=user_id)
            return user
        except jwt.InvalidTokenError:
            raise HTTPException(401, "Unauthorized")


api_description = """
    Work in progress API
    ## Authorization
    This API uses JWT Bearer tokens for authorization. To authorize,
    click the 'Authorize' button and enter your token
    in the format 'Bearer {your_token}'.
    """

api = NinjaAPI(
    title="Work in progress API",
    version="0.0.1",
    description=api_description,
    auth=JWTAuth(),
)


class HTTPException(Exception):
    status_code: int
    message: str

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message


@api.exception_handler(Exception)
def base_exception(request: Request, exc: HTTPException) -> None:
    try:
        exception_message = exc.message if exc.message else "Internal server error"
    except Exception:
        exception_message = "Internal server error"
    try:
        status = exc.status_code if exc.status_code else 500
    except Exception:
        status = 500
    return api.create_response(request, {"message": exception_message}, status=status)


def authenticate(request: Request, username: str, password: str) -> Optional[str]:
    try:
        user = SystemUser.objects.get(username=username)
        if user.password == password:
            token = jwt.encode({"sub": user.id}, SECRET_KEY, algorithm=ALGORITHM)
            return token
        else:
            raise HTTPException(401, "Invalid Credentials")

    except SystemUser.DoesNotExist:
        raise HTTPException(401, "Invalid Credentials")


@api.post("/login", auth=None, response=login_responses_dict, tags=["login"])
def login(request: Request, data: LoginSchema) -> Tuple[int, Dict[str, str]]:
    """
    Logar no sistema

    - **username**: username
    - **password**: password

    """
    token = authenticate(request, username=data.username, password=data.password)
    if token is not None:
        return 200, {"message": "Logged in succesfully", "token": token}
    else:
        raise HTTPException(401, "Invalid Credentials")


@api.get("/contatos", response=response_get_contatos, tags=["contatos"])
def get_contatos(request: Request) -> Tuple[int, Dict[str, Any]]:
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
def create_contato(request: Request, data: ContatoSchema) -> Dict[str, str]:
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
def update_contato(
    request: Request, contato_id: str, data: ContatoSchema
) -> Dict[str, str]:
    try:
        contato: Contato = Contato.objects.filter(criado_por=request.auth).get(
            contato_id=contato_id
        )
    except Exception:
        raise HTTPException(404, "Contato não existe")
    try:
        contato_responsavel: Optional[Contato] = Contato.objects.filter(
            criado_por=request.auth
        ).get(email_responsavel=data.email_responsavel)
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
def delete_contato(request: Request, contato_id: str) -> Dict[str, str]:
    try:
        contato: Contato = Contato.objects.filter(criado_por=request.auth).get(
            contato_id=contato_id
        )
    except Contato.DoesNotExist:
        raise HTTPException(404, "Contato não existe, certeza que este contato existe?")
    contato.delete()
    return {"message": f"Contato de nome {contato.nome} e id {contato_id} deletado"}


@api.get(
    "/companies",
    response=response_get_companies,
    tags=["companies"],
)
def get_companies(
    request: Request,
) -> Tuple[int, Dict[str, Union[str, List[Dict[str, Union[str, int, float, bool]]]]]]:
    if request.auth.is_superuser:
        companies: QuerySet[Company]
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
def create_company(request: Request, data: CompanySchema) -> Optional[Dict[str, str]]:
    try:
        company = Company.objects.get(cnpj=data.cnpj)
        if company:
            raise HTTPException(400, "Company já existe")
    except Company.DoesNotExist:
        try:
            contato = Contato.objects.filter(criado_por=request.auth).get(
                contato_id=data.contato_id
            )
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
    return None


@api.put(
    "/companies/{company_id}",
    response=responses_dict,
    tags=["companies"],
)
def update_companies(
    request: Request, company_id: str, data: CompanySchema
) -> Dict[str, str]:
    try:
        company = Company.objects.filter(criado_por=request.auth).get(
            company_id=company_id
        )
    except Company.DoesNotExist:
        raise HTTPException(404, "Company não existe")
    try:
        contato = Contato.objects.filter(criado_por=request.auth).get(
            contato_id=data.contato_id
        )
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
def delete_companies(request: Request, company_id: str) -> Dict[str, str]:
    try:
        company = Company.objects.filter(criado_por=request.auth).get(
            company_id=company_id
        )
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
def get_processos(
    request: Request,
) -> Tuple[int, Dict[str, Union[str, List[Dict[str, Union[str, int, float, bool]]]]]]:
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
def create_processo(request: Request, data: ProcessoSchema) -> Dict[str, str]:
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
def update_processo(
    request: Request, processo_id: str, data: ProcessoSchema
) -> Dict[str, str]:
    processo = Processo.objects.filter(criado_por=request.auth).get(
        processo_id=processo_id
    )
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
def delete_processo(request: Request, processo_id: str) -> Dict[str, str]:
    try:
        processo = Processo.objects.filter(criado_por=request.auth).get(
            processo_id=processo_id
        )
    except Processo.DoesNotExist:
        raise HTTPException(
            404, "Processo não existe, certeza que este processo existe?"
        )
    processo.delete()
    return {
        "message": f"Processo de numero {processo.numero_processo} "
        f"e id {processo_id}  deletado"
    }


# PRODUTO


@api.post("/produtos", response=responses_dict, tags=["produtos"])
def create_produto(request: Request, data: ProdutoSchema) -> Dict[str, str]:
    produto = Produto.objects.create(**data.dict(), criado_por=request.auth)
    return {
        "message": f"Produto de nome {produto.nome} "
        f"e id {produto.id_produto} criado"
    }


@api.get("/produtos", response=response_get_produtos, tags=["produtos"])
def get_produtos(
    request: Request,
) -> Tuple[int, Dict[str, Union[str, List[Dict[str, Union[str, int, float, bool]]]]]]:
    produtos: QuerySet[Produto]
    if request.auth.is_superuser:
        produtos = Produto.objects.all()
    else:
        produtos = Produto.objects.filter(criado_por=request.auth)
    if produtos:
        return 200, {
            "produtos": [ProdutoSchema.from_orm(produto).dict() for produto in produtos]
        }
    else:
        return 204, {"message": "No content"}


@api.get("/produtos/{produto_id}", response=ProdutoSchema, tags=["produtos"])
def get_produto(request: Request, produto_id: str) -> Optional[ProdutoSchema]:
    try:
        produto: Produto = Produto.objects.filter(criado_por=request.auth).get(
            id_produto=produto_id
        )
        if produto:
            return ProdutoSchema.from_orm(produto)
        return None
    except Produto.DoesNotExist:
        raise HTTPException(status_code=404, message="Produto não encontrado")


@api.put("/produtos/{produto_id}", response=responses_dict, tags=["produtos"])
def update_produto(
    request: Request, produto_id: str, data: ProdutoSchema
) -> Tuple[int, Dict[str, str]]:
    try:
        produto: Produto = Produto.objects.filter(criado_por=request.auth).get(
            id_produto=produto_id
        )
    except Produto.DoesNotExist:
        raise HTTPException(status_code=404, message="Produto não encontrado")
    produto.nome = data.nome
    produto.descricao = data.descricao
    produto.preco = data.preco
    produto.quantidade = data.quantidade
    produto.save()
    return 200, {
        "message": f"Produto de nome {produto.nome} e id {produto_id} "
        "atualizado com sucesso"
    }


@api.delete("/produtos/{produto_id}", tags=["produtos"])
def delete_produto(request: Request, produto_id: str) -> Tuple[int, Dict[str, str]]:
    try:
        produto: Produto = Produto.objects.filter(criado_por=request.auth).get(
            id_produto=produto_id
        )
    except Produto.DoesNotExist:
        raise HTTPException(status_code=404, message="Produto não encontrado")
    nome = produto.nome
    produto.delete()
    return 200, {
        "message": f"Produto de nome {nome} e id {produto_id} deletado com sucesso"
    }
