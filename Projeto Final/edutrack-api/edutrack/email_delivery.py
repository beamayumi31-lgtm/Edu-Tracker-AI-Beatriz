"""Adaptador SendGrid. Nunca registra destinatário, código, chave ou corpo de erro."""

import httpx

from edutrack.config import Settings


class EmailDeliveryError(Exception):
    pass


def send_message(settings: Settings, recipient: str, subject: str, message: str) -> None:
    if not settings.email_configured:
        raise EmailDeliveryError("Envio de e-mail não configurado.")
    body = {
        "personalizations": [{"to": [{"email": recipient}]}],
        "from": {"email": str(settings.email_from), "name": settings.email_from_name},
        "subject": subject,
        "content": [{"type": "text/plain", "value": message}],
        "tracking_settings": {
            "click_tracking": {"enable": False, "enable_text": False},
            "open_tracking": {"enable": False},
        },
    }
    try:
        # Sem retentativa automática: timeout pode ocorrer depois da aceitação do e-mail.
        with httpx.Client(timeout=12, follow_redirects=False, trust_env=False) as client:
            response = client.post(
                "https://api.sendgrid.com/v3/mail/send",
                headers={"Authorization": "Bearer " + settings.sendgrid_api_key.get_secret_value()},
                json=body,
            )
        if response.status_code != 202:
            raise EmailDeliveryError("SendGrid não aceitou o envio.")
    except httpx.HTTPError:
        raise EmailDeliveryError("Falha de comunicação com o serviço de e-mail.") from None


def send_verification(settings: Settings, recipient: str, code: str) -> None:
    send_message(settings, recipient, "Confirme sua conta no EduTrack", (
        f"Seu código de confirmação do EduTrack é: {code}\n\n"
        "Ele expira em 10 minutos. Volte à tela do EduTrack no computador e digite o código.\n"
        "Não compartilhe este código. Se você não solicitou, ignore esta mensagem."
    ))


def send_password_reset(settings: Settings, recipient: str, link: str) -> None:
    send_message(settings, recipient, "Redefina sua senha do EduTrack", (
        "Recebemos uma solicitação para redefinir sua senha do EduTrack.\n\n"
        f"Abra este link no navegador: {link}\n\n"
        "O link vale por 15 minutos e pode ser usado uma única vez. "
        "Depois da alteração, entre novamente nos seus dispositivos.\n"
        "Se não foi você, ignore esta mensagem. Sua senha permanece a mesma. "
        "Não compartilhe este link."
    ))
