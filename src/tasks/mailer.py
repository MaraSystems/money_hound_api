from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
from jinja2 import Environment, FileSystemLoader
import smtplib
import os

from src.config.queue import celery_app
from src.config.config import MAIL_USER, MAIL_PASSWORD, APP_NAME, ENV, ENVIRONMENTS
from src.lib.utils.logger import get_logger


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
template_dir = os.path.join(BASE_DIR, 'templates')
env = Environment(loader=FileSystemLoader(template_dir))

@celery_app.task
def send_mail(subject, email: str, data: dict, template_file: str, attachements = [], clear=True):
    if ENV == ENVIRONMENTS.TESTING:
        return

    logger = get_logger('Mail Logger')
    
    template = env.get_template(template_file)
    html_content = template.render(**data, app_name=APP_NAME)

    msg = MIMEMultipart("alternative")
    msg['Subject'] = subject
    msg['From'] = APP_NAME
    msg['To'] = email
    msg.attach(MIMEText(html_content, "html"))

    for attachment in attachements:
        filename = os.path.basename(attachment)
        with open(attachment, 'rb') as fh:
            payload = fh.read()
        maintype, subtype = 'application', 'octet-stream'
        path = MIMEBase(maintype, subtype)
        path.set_payload(payload)
        encode_base64(path)
        path.add_header('Content-Disposition', f'attachment; filename="{filename}"')
        msg.attach(path)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(MAIL_USER, MAIL_PASSWORD)
        server.sendmail(MAIL_USER, [email], msg.as_string())

    if clear:
        logger.info('Removing attatchments')
        for attachment in attachements:
            if os.path.exists(attachment):
                os.remove(attachment)

    logger.info(f'Mail sent successfully')


