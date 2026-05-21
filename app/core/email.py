import logging
import smtplib
import socket
from email.message import EmailMessage
from email.utils import formataddr

from app.core.settings import settings


logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    pass


def send_email(to_email: str, subject: str, body: str) -> None:
    if not settings.SMTP_HOST:
        if settings.DEBUG:
            logger.warning(
                "SMTP não configurado; e-mail não enviado",
                extra={"to_email": to_email, "subject": subject},
            )
            return
        raise EmailDeliveryError("SMTP_HOST não configurado")

    message = EmailMessage()
    from_email = settings.SMTP_FROM or settings.SMTP_USERNAME or "no-reply@localhost"
    message["From"] = formataddr((settings.SMTP_FROM_NAME, from_email))
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        if settings.SMTP_USE_SSL:
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
                smtp.ehlo()
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                smtp.send_message(message)
            return

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as smtp:
            smtp.ehlo()
            if settings.SMTP_USE_TLS:
                smtp.starttls()
                smtp.ehlo()
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(message)
    except (smtplib.SMTPException, OSError, socket.timeout) as exc:
        logger.exception(
            "Falha no envio de e-mail",
            extra={
                "to_email": to_email,
                "smtp_host": settings.SMTP_HOST,
                "smtp_port": settings.SMTP_PORT,
                "smtp_use_ssl": settings.SMTP_USE_SSL,
                "smtp_use_tls": settings.SMTP_USE_TLS,
            },
        )
        raise EmailDeliveryError(f"Falha ao enviar e-mail: {exc}") from exc


def build_password_reset_body(reset_link: str) -> str:
    return (
        "Você solicitou a redefinição da senha.\n\n"
        f"Acesse o link abaixo para redefinir sua senha:\n{reset_link}\n\n"
        "Se você não solicitou isso, pode ignorar este e-mail."
    )


def build_welcome_body(reset_link: str, name: str) -> str:
    return (
        f"Olá, {name}!\n\n"
        "Seu cadastro na NEPS API foi criado com sucesso.\n\n"
        "Para acessar o sistema pela primeira vez, defina sua senha usando o link abaixo:\n"
        f"{reset_link}\n\n"
        "Se você não esperava este cadastro, entre em contato com o suporte."
    )