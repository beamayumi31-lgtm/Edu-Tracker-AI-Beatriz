from fastapi import APIRouter, HTTPException, Request

from edutrack.agent import require_ai, run_agent
from edutrack.gemini import GeminiClient
from edutrack.planning import build_plan
from edutrack.routes import Db, Student
from edutrack.schemas import ChatInput, ChatMessage, ChatOutput, PlanInput, StudyPlan
from edutrack.study_context import study_context

router = APIRouter(prefix="/api/edu-ia", tags=["Edu IA"])


def rate_limit(request, student):
    request.app.state.limiter.check("ai:" + str(student.id), 8, 60)


def provider_limit(request):
    # Limite compartilhado por processo; produção atual executa um worker.
    request.app.state.limiter.check("ai-provider-global", 20, 60)


def external_context(request, db, student):
    return study_context(db, student.id, exclude_classroom=True)


@router.get("/status")
def status(request: Request, student: Student):
    settings = request.app.state.settings
    return {"configured": settings.ai_configured, "planejador_por_regras": True,
            "provider": settings.ai_provider, "academic_context_allowed": settings.ai_context_allowed,
            "classroom_sent_to_ai": False}


@router.get("/context")
def context(db: Db, student: Student):
    return study_context(db, student.id)


@router.post("/chat", response_model=ChatOutput)
def chat(body: ChatInput, request: Request, db: Db, student: Student):
    rate_limit(request, student)
    settings = request.app.state.settings
    require_ai(settings, body.enviar_dados_ia)
    if settings.ai_provider == "gemini" and not body.maior_de_idade:
        raise HTTPException(422, "O uso do Gemini nesta aplicação exige confirmação de idade igual ou superior a 18 anos.")
    provider_limit(request)
    if settings.ai_provider == "gemini" and not settings.ai_context_allowed:
        client = GeminiClient(settings)
        try:
            return client.general_chat(body.messages)
        finally:
            client.close()
    academic_context = external_context(request, db, student)
    return run_agent(settings, body.messages, academic_context)


@router.post("/study-plan", response_model=StudyPlan)
def plan(body: PlanInput, request: Request, db: Db, student: Student):
    rate_limit(request, student)
    context = study_context(db, student.id)
    proposal = build_plan(context, body)
    if not body.usar_ia:
        return proposal
    settings = request.app.state.settings
    require_ai(settings, body.enviar_dados_ia)
    if settings.ai_provider == "gemini" and not body.maior_de_idade:
        raise HTTPException(422, "O uso do Gemini nesta aplicação exige confirmação de idade igual ou superior a 18 anos.")
    if not settings.ai_context_allowed:
        raise HTTPException(422, "Este Gemini está no modo de dúvidas gerais. Use o planejador local, que inclui suas atividades sem enviá-las ao provedor.")
    provider_limit(request)
    context = external_context(request, db, student)
    result = run_agent(
        settings,
        [ChatMessage(role="user", text="Crie e explique meu plano de estudos: " + body.objetivo)],
        context,
        body,
    )
    if not result["plan"]:
        raise HTTPException(
            502, "A IA não gerou o plano. Tente novamente ou use o planejamento por regras."
        )
    proposal = result["plan"]
    proposal.origem = "ia"
    proposal.resumo = result["reply"]
    return proposal
