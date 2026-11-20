"""OAuth autenticado e importação explícita. Nunca escreve na conta Google."""

import json
import secrets
from datetime import datetime, timedelta
from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import Field, model_validator
from sqlalchemy import delete, func, select, update
from sqlalchemy.exc import IntegrityError

from edutrack.database import require_writes
from edutrack.google_classroom import ID_PATTERN, authorization_url, fingerprint, seal, unseal
from edutrack.integration_models import (
    ClassroomContent,
    ClassroomDisciplineLink,
    ClassroomTaskLink,
    GoogleConnection,
    GoogleOAuthAttempt,
)
from edutrack.models import Course, Discipline, Task, utc_now
from edutrack.routes import Db, Student
from edutrack.schemas import Contract, CourseInput

router = APIRouter(prefix="/api/integrations/google", tags=["Google Classroom"])
write = [Depends(require_writes)]


class CallbackInput(Contract):
    state: str = Field(min_length=32, max_length=200)
    code: str = Field(min_length=1, max_length=4096)


class ClassSelection(Contract):
    turma_id: str = Field(pattern=ID_PATTERN)
    atividades: list[str] = Field(default_factory=list, max_length=500)
    modo: Literal["selecionadas", "todas_atividades", "completo"] = "selecionadas"

    @model_validator(mode="after")
    def explicit_selection(self):
        if self.modo != "selecionadas" and self.atividades:
            raise ValueError("A importação automática não recebe uma seleção parcial de atividades.")
        return self


class ImportInput(Contract):
    curso_id: UUID | None = None
    novo_curso: CourseInput | None = None
    conexao_versao: UUID
    turmas: list[ClassSelection] = Field(min_length=1, max_length=10)

    @model_validator(mode="after")
    def single_destination(self):
        if (self.curso_id is None) == (self.novo_curso is None):
            raise ValueError("Escolha um curso existente ou informe o novo curso, nunca ambos.")
        if any(t.modo == "completo" for t in self.turmas) and len(self.turmas) != 1:
            raise ValueError("Importe uma turma completa de cada vez.")
        return self


class PreviewInput(Contract):
    turma_id: str = Field(pattern=ID_PATTERN)
    completo: bool = False


def enabled(request):
    settings = request.app.state.settings
    if not settings.classroom_enabled:
        raise HTTPException(503, "Classroom ainda não ativado. O administrador precisa configurar o projeto Google e aplicar a migração.")
    return settings


def connection(db, user_id):
    row = db.get(GoogleConnection, user_id)
    if not row:
        raise HTTPException(409, "Conecte sua conta Google primeiro.")
    return row


@router.get("/status")
def status(request: Request, db: Db, student: Student):
    active = request.app.state.settings.classroom_enabled
    row = db.get(GoogleConnection, student.id) if active else None
    return {"configured": active, "connected": bool(row), "email": row.email if row else None,
            "conexao_versao": str(row.versao) if row else None, "somente_leitura": True,
            "completo_configurado": active and request.app.state.settings.classroom_full_import_enabled,
            "completo_autorizado": bool(row and row.conteudo_autorizado)}


@router.post("/start", dependencies=write)
def start(request: Request, db: Db, student: Student):
    settings = enabled(request)
    request.app.state.limiter.check("google-start:" + str(student.id), 5, 300)
    state, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(64)
    # Um novo início invalida tentativas anteriores, inclusive abas antigas.
    db.execute(delete(GoogleOAuthAttempt).where(GoogleOAuthAttempt.usuario_id == student.id))
    db.add(GoogleOAuthAttempt(state_hash=fingerprint(state), usuario_id=student.id,
                             verifier_cifrado=seal(settings, student.id, verifier), expira_em=utc_now() + timedelta(minutes=10)))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Outra tentativa de conexão foi iniciada. Aguarde e tente novamente nesta aba.") from None
    return {"authorization_url": authorization_url(settings, state, verifier)}


@router.post("/callback", dependencies=write)
def callback(body: CallbackInput, request: Request, db: Db, student: Student):
    settings = enabled(request)
    request.app.state.limiter.check("google-callback:" + str(student.id), 10, 300)
    state_hash = fingerprint(body.state)
    row = db.get(GoogleOAuthAttempt, state_hash)
    if not row or row.usuario_id != student.id:
        raise HTTPException(400, "Autorização inválida. Inicie a conexão novamente.")
    result = db.execute(update(GoogleOAuthAttempt).where(GoogleOAuthAttempt.state_hash == state_hash,
        GoogleOAuthAttempt.usuario_id == student.id, GoogleOAuthAttempt.usado_em.is_(None), GoogleOAuthAttempt.expira_em > utc_now()).values(usado_em=utc_now()))
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(400, "Autorização expirada ou já utilizada. Inicie novamente.")
    verifier = unseal(settings, student.id, row.verifier_cifrado)
    db.commit()  # Consumo atômico antes da troca externa; um código nunca é repetido.
    google = request.app.state.google_client_factory(settings)
    try:
        sub, email, refresh = google.exchange(body.code, verifier)
        # Uma desconexão ou nova tentativa durante a chamada externa invalida o retorno antigo.
        current = db.execute(update(GoogleOAuthAttempt).where(GoogleOAuthAttempt.state_hash == state_hash,
            GoogleOAuthAttempt.usuario_id == student.id, GoogleOAuthAttempt.usado_em.is_not(None)).values(verifier_cifrado="consumido"))
        if current.rowcount != 1:
            db.rollback()
            google.revoke(refresh)
            raise HTTPException(409, "A conexão foi cancelada ou reiniciada em outra aba. Inicie novamente.")
    finally:
        google.close()
    previous = db.get(GoogleConnection, student.id)
    if previous and previous.google_sub != sub:
        db.rollback()
        google = request.app.state.google_client_factory(settings)
        try:
            google.revoke(refresh)
        finally:
            google.close()
        raise HTTPException(409, "Para trocar a conta Google, desconecte a conta atual primeiro. Importações de contas diferentes ficam independentes.")
    if previous:
        previous.google_sub, previous.email = sub, email
        previous.refresh_cifrado, previous.versao = seal(settings, student.id, refresh), uuid4()
        previous.conteudo_autorizado = google.full_content_authorized
    else:
        db.add(GoogleConnection(usuario_id=student.id, google_sub=sub, email=email, refresh_cifrado=seal(settings, student.id, refresh), versao=uuid4(), conteudo_autorizado=google.full_content_authorized))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        google = request.app.state.google_client_factory(settings)
        try:
            google.revoke(refresh)
        finally:
            google.close()
        raise HTTPException(409, "A conexão foi alterada em outra aba. Consulte o estado e conecte novamente se necessário.") from None
    return {"connected": True}


def google_access(request, db, student, *, completo=False):
    settings = enabled(request)
    request.app.state.limiter.check("google-read:" + str(student.id), 20, 60)
    row = connection(db, student.id)
    if completo:
        if not settings.classroom_full_import_enabled:
            raise HTTPException(503, "A importação completa aguarda ativação pelo administrador.")
        if not row.conteudo_autorizado:
            raise HTTPException(409, "Atualize a autorização Google para incluir materiais, avisos e tópicos.")
    google = request.app.state.google_client_factory(settings)
    try:
        access = google.access(unseal(settings, student.id, row.refresh_cifrado))
    except Exception:
        google.close()
        raise
    return google, access, row


@router.get("/courses")
def courses(request: Request, db: Db, student: Student):
    google, access, row = google_access(request, db, student)
    try:
        return {"turmas": google.courses(access), "conexao_versao": str(row.versao)}
    finally:
        google.close()


@router.post("/preview")
def preview(body: PreviewInput, request: Request, db: Db, student: Student):
    google, access, row = google_access(request, db, student, completo=body.completo)
    try:
        if body.turma_id not in {c["id"] for c in google.courses(access)}:
            raise HTTPException(404, "Turma não disponível para esta conta.")
        tasks, contents = google.full_course(access, body.turma_id) if body.completo else (google.coursework(access, body.turma_id), [])
        imported = set(db.scalars(select(ClassroomTaskLink.atividade_id).where(ClassroomTaskLink.usuario_id == student.id,
            ClassroomTaskLink.google_sub == row.google_sub, ClassroomTaskLink.turma_id == body.turma_id)))
        link = db.scalar(select(ClassroomDisciplineLink).where(ClassroomDisciplineLink.usuario_id == student.id,
            ClassroomDisciplineLink.google_sub == row.google_sub, ClassroomDisciplineLink.turma_id == body.turma_id))
        discipline = db.scalar(select(Discipline).where(Discipline.id == link.disciplina_id, Discipline.usuario_id == student.id)) if link else None
        return {"atividades": [{**t, "ja_importada": t["id"] in imported} for t in tasks], "conexao_versao": str(row.versao),
                "conteudos": contents, "curso_importado_id": str(discipline.curso_id) if discipline else None,
                "disciplina_importada_id": str(discipline.id) if discipline else None,
                "disciplina_excluida": bool(link and not discipline)}
    finally:
        google.close()


@router.post("/import", dependencies=write)
def import_items(body: ImportInput, request: Request, db: Db, student: Student):
    enabled(request)
    course = db.scalar(select(Course).where(Course.id == body.curso_id, Course.usuario_id == student.id)) if body.curso_id else None
    if body.curso_id and not course:
        raise HTTPException(404, "Curso de destino não encontrado.")
    if len({c.turma_id for c in body.turmas}) != len(body.turmas) or sum(len(c.atividades) for c in body.turmas) > 500:
        raise HTTPException(422, "Selecione turmas distintas e no máximo 500 atividades por importação.")
    google, access, conn = google_access(request, db, student, completo=any(t.modo == "completo" for t in body.turmas))
    if conn.versao != body.conexao_versao:
        google.close()
        raise HTTPException(409, "A conexão mudou. Atualize a prévia antes de importar.")
    snapshots = []
    try:
        remote_courses = {c["id"]: c for c in google.courses(access)}
        for selection in body.turmas:
            if selection.turma_id not in remote_courses:
                raise HTTPException(404, "Uma turma selecionada não está mais disponível.")
            tasks, contents = google.full_course(access, selection.turma_id) if selection.modo == "completo" else (google.coursework(access, selection.turma_id), [])
            items = {t["id"]: t for t in tasks}
            if selection.modo == "selecionadas" and not set(selection.atividades).issubset(items):
                raise HTTPException(409, "Uma atividade mudou ou foi removida. Atualize a prévia.")
            chosen = [items[i] for i in dict.fromkeys(selection.atividades)] if selection.modo == "selecionadas" else list(items.values())
            snapshots.append((remote_courses[selection.turma_id], chosen, contents))
            if sum(len(s[1]) for s in snapshots) > 500:
                raise HTTPException(422, "A importação excede 500 atividades. Nada foi gravado; importe uma turma de cada vez.")
    finally:
        google.close()
    # Serializa importações e desconexões da mesma conta sem manter lock durante chamadas Google.
    locked = db.execute(update(GoogleConnection).where(GoogleConnection.usuario_id == student.id,
        GoogleConnection.versao == body.conexao_versao).values(atualizado_em=utc_now()))
    if locked.rowcount != 1:
        db.rollback()
        raise HTTPException(409, "A conexão mudou. Consulte novamente suas turmas.")
    counts = {"disciplinas_criadas": 0, "tarefas_criadas": 0, "itens_preservados": 0,
              "conteudos_criados": 0, "conteudos_atualizados": 0, "disciplinas_ids": []}
    try:
        if body.novo_curso:
            course = Course(usuario_id=student.id, **body.novo_curso.model_dump())
            db.add(course)
            db.flush()
        for remote, items, contents in snapshots:
            filters = (ClassroomDisciplineLink.usuario_id == student.id, ClassroomDisciplineLink.google_sub == conn.google_sub,
                       ClassroomDisciplineLink.turma_id == remote["id"])
            link = db.scalar(select(ClassroomDisciplineLink).where(*filters))
            if link:
                discipline = db.scalar(select(Discipline).where(Discipline.id == link.disciplina_id, Discipline.usuario_id == student.id))
                if not discipline:
                    raise HTTPException(409, "Uma disciplina importada foi excluída. Cadastre-a manualmente para evitar recriar dados apagados.")
                if discipline.curso_id != course.id:
                    raise HTTPException(409, "Esta turma já foi importada em outro curso. Escolha o curso original.")
                counts["itens_preservados"] += 1
            else:
                discipline = Discipline(usuario_id=student.id, curso_id=course.id, nome=remote["nome"])
                db.add(discipline)
                db.flush()
                db.add(ClassroomDisciplineLink(usuario_id=student.id, google_sub=conn.google_sub, turma_id=remote["id"], disciplina_id=discipline.id))
                counts["disciplinas_criadas"] += 1
            counts["disciplinas_ids"].append(str(discipline.id))
            existing_ids = set(db.scalars(select(ClassroomTaskLink.atividade_id).where(ClassroomTaskLink.usuario_id == student.id,
                ClassroomTaskLink.google_sub == conn.google_sub, ClassroomTaskLink.turma_id == remote["id"])))
            new_tasks, new_links = [], []
            for item in items:
                if item["id"] in existing_ids:
                    counts["itens_preservados"] += 1
                    continue
                task = Task(id=uuid4(), usuario_id=student.id, disciplina_id=discipline.id, titulo=item["titulo"], descricao=item["descricao"],
                    data_prevista=datetime.fromisoformat(item["data_prevista"].replace("Z", "+00:00")).replace(tzinfo=None) if item["data_prevista"] else None, status="pendente")
                new_tasks.append(task)
                new_links.append(ClassroomTaskLink(usuario_id=student.id, google_sub=conn.google_sub, turma_id=remote["id"], atividade_id=item["id"], tarefa_id=task.id))
                counts["tarefas_criadas"] += 1
            db.add_all(new_tasks)
            db.flush()
            db.add_all(new_links)
            db.flush()
            # Conteúdos são cópias de leitura atualizáveis; tarefas pessoais são preservadas.
            saved = {(c.tipo, c.origem_id): c for c in db.scalars(select(ClassroomContent).where(
                ClassroomContent.usuario_id == student.id, ClassroomContent.google_sub == conn.google_sub,
                ClassroomContent.turma_id == remote["id"]))} if contents else {}
            for item in contents:
                key = (item["tipo"], item["origem_id"])
                values = {k: v for k, v in item.items() if k != "anexos"}
                values["anexos_json"] = json.dumps(item["anexos"], ensure_ascii=False)
                if key in saved:
                    if saved[key].disciplina_id != discipline.id:
                        raise HTTPException(409, "O conteúdo pertence a outra disciplina. Consulte a importação original.")
                    for field, value in values.items():
                        setattr(saved[key], field, value)
                    counts["conteudos_atualizados"] += 1
                else:
                    record = ClassroomContent(usuario_id=student.id, google_sub=conn.google_sub, turma_id=remote["id"], disciplina_id=discipline.id, **values)
                    db.add(record)
                    saved[key] = record
                    counts["conteudos_criados"] += 1
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Outra importação terminou ao mesmo tempo. Atualize a prévia; nenhum dado foi duplicado.") from None
    except HTTPException:
        db.rollback()
        raise
    return {**counts, "curso_id": str(course.id)}


@router.get("/disciplines/{discipline_id}/content")
def discipline_content(discipline_id: UUID, db: Db, student: Student,
                       tipo: Literal["atividade", "material", "aviso"] | None = None,
                       offset: int = Query(default=0, ge=0), limit: int = Query(default=30, ge=1, le=100)):
    """Leitura local isolada por aluno, disponível também após desconectar o Google."""
    if not db.scalar(select(Discipline.id).where(Discipline.id == discipline_id, Discipline.usuario_id == student.id)):
        raise HTTPException(404, "Disciplina não encontrada.")
    filters = [ClassroomContent.usuario_id == student.id, ClassroomContent.disciplina_id == discipline_id]
    if tipo:
        filters.append(ClassroomContent.tipo == tipo)
    total = db.scalar(select(func.count()).select_from(ClassroomContent).where(*filters))
    records = db.scalars(select(ClassroomContent).where(*filters).order_by(ClassroomContent.publicado_em.desc(), ClassroomContent.id).offset(offset).limit(limit))
    return {"total": total, "items": [{"id": str(c.id), "tipo": c.tipo, "titulo": c.titulo, "descricao": c.descricao,
        "topico": c.topico, "url": c.url, "anexos": json.loads(c.anexos_json),
        "publicado_em": c.publicado_em.isoformat() + "Z" if c.publicado_em else None} for c in records]}


@router.delete("/connection", dependencies=write)
def disconnect(request: Request, db: Db, student: Student):
    settings = enabled(request)
    row = connection(db, student.id)
    try:
        refresh = unseal(settings, student.id, row.refresh_cifrado)
    except HTTPException:
        # Uma chave perdida não impede remover o vínculo local; a revogação fica no painel Google.
        refresh = None
    db.delete(row)
    db.execute(delete(GoogleOAuthAttempt).where(GoogleOAuthAttempt.usuario_id == student.id))
    db.commit()
    google = request.app.state.google_client_factory(settings)
    try:
        revoked = google.revoke(refresh) if refresh else False
    finally:
        google.close()
    return {"connected": False, "revogado_no_google": revoked,
            "mensagem": "Conexão removida. Disciplinas e tarefas importadas foram preservadas." if revoked else "Conexão removida localmente. Remova também o acesso EduTrack em myaccount.google.com/permissions."}
