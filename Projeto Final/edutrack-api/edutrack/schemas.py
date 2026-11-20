"""Contratos HTTP explícitos; campos desconhecidos são recusados."""

from datetime import date, datetime, timedelta, timezone
from typing import Annotated, Literal
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    StringConstraints,
    field_serializer,
    field_validator,
    model_validator,
)

from edutrack.cpf import valid_cpf

Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=150)]
TaskStatus = Literal["pendente", "em_andamento", "concluida", "cancelada"]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    @field_serializer("*", when_used="json", check_fields=False)
    def serialize_utc_dates(self, value):
        # DATETIME2 retorna datetime sem fuso; a API declara UTC explicitamente no JSON.
        if isinstance(value, datetime) and value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value


class Page[T](Contract):
    items: list[T]
    total: int
    limit: int
    offset: int


class Registration(Contract):
    nome: Name
    email: EmailStr = Field(max_length=255)
    senha: SecretStr = Field(min_length=10, max_length=128)
    cpf: SecretStr = Field(min_length=11, max_length=14, description="Validado matematicamente e descartado; não armazenado nem consultado na Receita Federal.")

    @field_validator("cpf")
    @classmethod
    def validate_cpf(cls, value):
        if not valid_cpf(value.get_secret_value()):
            raise ValueError("CPF inválido. Confira os números digitados.")
        return value

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value):
        return value.lower()


class Login(Contract):
    email: EmailStr = Field(max_length=255)
    senha: SecretStr = Field(min_length=1, max_length=128)


class EmailConfirmation(Login):
    codigo: str = Field(pattern=r"^[0-9]{6}$", description="Código de seis dígitos recebido por e-mail.")


class ProfileInput(Contract):
    nome: Name


class UserOut(Contract):
    id: UUID
    nome: str
    email: str
    criado_em: datetime
    role: Literal["student", "admin"]


class AdminAccessOut(Contract):
    role: Literal["admin"]
    email_verificado: Literal[True]
    gestao_usuarios_disponivel: Literal[False] = False


class TokenOut(Contract):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int
    user: UserOut


class CourseInput(Contract):
    nome: Name
    instituicao: str | None = Field(default=None, max_length=200)
    data_inicio: date | None = None
    data_fim: date | None = None

    @model_validator(mode="after")
    def ordered_dates(self):
        if self.data_inicio and self.data_fim and self.data_fim < self.data_inicio:
            raise ValueError("A data final não pode ser anterior à inicial.")
        return self


class CourseOut(CourseInput):
    id: UUID
    criado_em: datetime
    atualizado_em: datetime


class DisciplineInput(Contract):
    curso_id: UUID
    nome: Name
    professor: str | None = Field(default=None, max_length=150)
    carga_horaria: int | None = Field(default=None, ge=0, le=10000)


class DisciplineOut(DisciplineInput):
    id: UUID
    criado_em: datetime
    atualizado_em: datetime


class TaskInput(Contract):
    disciplina_id: UUID
    titulo: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
    descricao: str | None = Field(default=None, max_length=30000)
    data_prevista: AwareDatetime | None = None
    status: TaskStatus = "pendente"
    minutos_estimados: int | None = Field(default=None, ge=0, le=100000)


class TaskOut(Contract):
    id: UUID
    disciplina_id: UUID
    titulo: str
    descricao: str | None
    data_prevista: datetime | None
    status: TaskStatus
    minutos_estimados: int | None
    concluido_em: datetime | None
    criado_em: datetime
    atualizado_em: datetime


class TimeEntryInput(Contract):
    tarefa_id: UUID
    iniciado_em: AwareDatetime
    finalizado_em: AwareDatetime

    @model_validator(mode="after")
    def valid_period(self):
        minutes = (self.finalizado_em - self.iniciado_em).total_seconds() / 60
        if minutes < 1 or minutes > 240:
            raise ValueError("Uma sessão precisa durar de 1 a 240 minutos.")
        if self.finalizado_em > datetime.now(timezone.utc):
            raise ValueError("Não é possível registrar uma sessão futura.")
        return self


class TimeEntryOut(Contract):
    id: UUID
    tarefa_id: UUID
    iniciado_em: datetime
    finalizado_em: datetime | None
    duracao_minutos: int | None


class ChatMessage(Contract):
    role: Literal["user", "assistant"]
    text: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class ChatInput(Contract):
    maior_de_idade: bool = False
    messages: list[ChatMessage] = Field(min_length=1, max_length=10)
    enviar_dados_ia: bool = False

    @model_validator(mode="after")
    def last_message_from_user(self):
        if self.messages[-1].role != "user":
            raise ValueError("A última mensagem precisa ser do aluno.")
        return self


class PlanInput(Contract):
    maior_de_idade: bool = False
    data_inicio: date
    dias: int = Field(default=7, ge=1, le=14)
    minutos_por_dia: int = Field(default=60, ge=15, le=240)
    objetivo: str = Field(default="Organizar as atividades pendentes", max_length=1000)
    usar_ia: bool = False
    enviar_dados_ia: bool = False

    @model_validator(mode="after")
    def valid_horizon(self):
        if self.data_inicio > date.max - timedelta(days=self.dias - 1):
            raise ValueError("O período ultrapassa o limite de datas permitido.")
        return self


class PlanBlock(Contract):
    data: date
    tarefa_id: UUID
    disciplina_id: UUID
    curso_id: UUID
    titulo: str
    minutos: int
    orientacao: str


class StudyPlan(Contract):
    origem: Literal["regras", "ia"] = "regras"
    resumo: str
    blocos: list[PlanBlock]
    alertas: list[str]
    tarefas_nao_planejadas: list[UUID]
    somente_proposta: bool = True


class ChatOutput(Contract):
    reply: str
    tools_used: list[str]
    plan: StudyPlan | None = None
