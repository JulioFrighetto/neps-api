import logging
import smtplib
import socket
from email.message import EmailMessage
from email.utils import formataddr

import requests

from app.core.settings import settings



logger = logging.getLogger(__name__)


class EmailDeliveryError(RuntimeError):
    pass


def send_email(to_email: str, subject: str, body: str) -> None:
    """Send email via MailerSend (preferred) or SMTP (fallback)."""
    # Try MailerSend first (preferred)
    if settings.MAILERSEND_API_TOKEN and settings.MAILERSEND_FROM_EMAIL:
        return _send_via_mailersend(to_email, subject, body)

    # Otherwise try SMTP first, and if it fails try SendGrid as fallback
    if settings.SMTP_HOST:
        try:
            return _send_via_smtp(to_email, subject, body)
        except EmailDeliveryError as smtp_exc:
            logger.warning("SMTP send failed, attempting SendGrid fallback", extra={"error": str(smtp_exc)})
            if settings.SENDGRID_API_KEY and settings.SENDGRID_FROM_EMAIL:
                try:
                    return _send_via_sendgrid(to_email, subject, body)
                except EmailDeliveryError as sg_exc:
                    logger.error("SendGrid fallback also failed", extra={"smtp_error": str(smtp_exc), "sendgrid_error": str(sg_exc)})
                    raise EmailDeliveryError(f"SMTP failed: {smtp_exc}; SendGrid fallback failed: {sg_exc}") from sg_exc
            # no SendGrid configured, re-raise original SMTP error
            raise
    
    # No email service configured
    if settings.DEBUG:
        logger.warning(
            "Email service não configurado (MailerSend ou SMTP)",
            extra={"to_email": to_email, "subject": subject},
        )
        return
    
    raise EmailDeliveryError("Nenhum serviço de email configurado (MailerSend ou SMTP)")


def _send_via_mailersend(to_email: str, subject: str, body: str) -> None:
    """Send email using MailerSend REST API."""
    try:
        url = "https://api.mailersend.com/v1/email"
        headers = {
            "Authorization": f"Bearer {settings.MAILERSEND_API_TOKEN}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "from": {
                "email": settings.MAILERSEND_FROM_EMAIL,
                "name": settings.MAILERSEND_FROM_NAME,
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "text": body,
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        
        logger.info(
            "Email sent via MailerSend",
            extra={"to_email": to_email, "subject": subject, "status": response.status_code},
        )
    except requests.RequestException as exc:
        logger.error(
            f"MailerSend delivery failed: {exc}",
            extra={"to_email": to_email, "subject": subject},
            exc_info=True,
        )
        raise EmailDeliveryError(f"Falha ao enviar e-mail via MailerSend: {exc}") from exc


def _send_via_smtp(to_email: str, subject: str, body: str) -> None:
    """Send email using SMTP."""
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
        
        logger.info("Email sent via SMTP", extra={"to_email": to_email, "subject": subject})
    except (smtplib.SMTPException, OSError, socket.timeout) as exc:
        logger.error(
            f"SMTP delivery failed: {exc}",
            extra={
                "to_email": to_email,
                "smtp_host": settings.SMTP_HOST,
                "smtp_port": settings.SMTP_PORT,
            },
            exc_info=True,
        )
        raise EmailDeliveryError(f"Falha ao enviar e-mail via SMTP: {exc}") from exc


def _send_via_sendgrid(to_email: str, subject: str, body: str) -> None:
    """Send email using SendGrid REST API (used as fallback)."""
    try:
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "personalizations": [{"to": [{"email": to_email}], "subject": subject}],
            "from": {"email": settings.SENDGRID_FROM_EMAIL, "name": settings.SENDGRID_FROM_NAME},
            "content": [{"type": "text/plain", "value": body}],
        }
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        logger.info("Email sent via SendGrid", extra={"to_email": to_email, "subject": subject, "status": resp.status_code})
    except requests.RequestException as exc:
        logger.error("SendGrid delivery failed", extra={"to_email": to_email, "error": str(exc)}, exc_info=True)
        raise EmailDeliveryError(f"Falha ao enviar e-mail via SendGrid: {exc}") from exc


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
