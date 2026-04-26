from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
from jinja2 import Environment, FileSystemLoader
import smtplib
import os

from src.lib.utils.config import MAIL_USER, MAIL_PASSWORD, APP_NAME, ENV, ENVIRONMENTS
from src.lib.utils.logger import get_logger


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(BASE_DIR, 'templates')
env = Environment(loader=FileSystemLoader(template_dir))


def send_mail_task(subject: str, email: str, data: dict, template_file: str, attachments: list = [], clear: bool = True):
    """Send an email with HTML content and optional attachments.

    Renders an HTML template with provided data, attaches files if specified,
    and sends the email via SMTP. Attachments can be optionally deleted after sending.

    Args:
        subject: Email subject line
        email: Recipient email address
        data: Template context data for rendering
        template_file: Name of the Jinja2 template file
        attachments: List of file paths to attach
        clear: If True, delete attachment files after sending
    """
    if ENV == ENVIRONMENTS.TESTING:
        return

    logger = get_logger('Mail Logger')
    logger.info(f'Sending mail to {email} with subject: {subject}')

    template = env.get_template(template_file)
    html_content = template.render(**data, app_name=APP_NAME)

    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = APP_NAME
    msg['To'] = email
    msg.attach(MIMEText(html_content, "html"))

    for attachment in attachments:
        filename = os.path.basename(attachment)
        with open(attachment, 'rb') as fh:
            payload = fh.read()
        maintype, subtype = 'application', 'octet-stream'
        part = MIMEBase(maintype, subtype)
        part.set_payload(payload)
        encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(MAIL_USER, MAIL_PASSWORD)
        server.sendmail(MAIL_USER, [email], msg.as_string())

    if clear:
        logger.info('Removing attachments')
        for attachment in attachments:
            if os.path.exists(attachment):
                os.remove(attachment)

    logger.info('Mail sent successfully')


