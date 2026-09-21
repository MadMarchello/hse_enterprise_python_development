import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def format_result_body(
    full_name: str,
    md5_hex: str,
    sha256_hex: str,
    types_section: str,
) -> str:
    return (
        f"ФИО: {full_name}\n"
        f"MD5:{md5_hex}\n"
        f"SHA-256:{sha256_hex}\n"
        f"\n"
        f"{types_section}"
    )


def send_email(
    subject: str,
    body: str,
    to_email: str,
    from_email: str,
    password: str,
    smtp_host: str = "smtp.yandex.ru",
    smtp_port: int = 465,
) -> None:
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
        _ = server.login(from_email, password)
        _ = server.sendmail(from_email, to_email, msg.as_string())

    print(f"Письмо успешно отправлено на {to_email}")
