# Created by Ryan Polasky | 10/22/25
# ACM MeteorMate | All Rights Reserved

import smtplib
from importlib import resources
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException

from config import settings


# noinspection DuplicatedCode
def send_verification_email(email: str, code: str):
    """Send verification code via email with MeteorMate branding"""
    try:
        # create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🌟 Verify Your MeteorMate Account'
        msg['From'] = settings.EMAIL_USER
        msg['To'] = email

        # load the template using python modules with importlib
        html = resources.files("backend.static").joinpath("email_template.html").read_text(
            encoding="utf-8"
        ).replace("{code}", code)

        msg.attach(MIMEText(html, 'html'))

        # send email via SMTP
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_USER, email, msg.as_string())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


def send_inactive_notices(email: str, notice_num: int):
    """Send inactivity notices via email with MeteorMate branding"""
    # notice num tells us which notice the user should receive
    email_subj: str = ""
    inactivity_warning: str = ""
    match notice_num:
        case 1:  # 1 month until inactive
            email_subj = "We miss you at MeteorMate! 🌟"
            inactivity_warning = (
                "Your MeteorMate account will be marked as <strong style=\"color: "
                "#FFFFFF;\">inactive in 1 month</strong> if you don't sign in. Once inactive, "
                "your profile won't be shown to potential roommates until you log back in."
            )
        case 2:  # 1 week until inactive
            email_subj = "Your profile goes inactive in 1 week ⚠️"
            inactivity_warning = (
                "Your MeteorMate account will be marked as <strong style=\"color: "
                "#FFFFFF;\">inactive in 1 week</strong> if you don't sign in. Once inactive, "
                "your profile won't be shown to potential roommates until you log back in."
            )
        case 3:  # account inactive
            email_subj = "Your MeteorMate account is now inactive 💤"
            inactivity_warning = (
                "Your MeteorMate account is now marked as <strong style=\"color: #FFFFFF;\">inactive</strong>. "
                "An inactive profile won't be shown to potential roommates until you log back in."
            )
    try:
        # create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = email_subj
        msg['From'] = settings.EMAIL_USER
        msg['To'] = email

        # load the template using python modules with importlib
        html = resources.files("backend.static").joinpath("reset_password.html").read_text(
            encoding="utf-8"
        ).replace("{inactivity_warning}", inactivity_warning)

        msg.attach(MIMEText(html, 'html'))

        # send email via SMTP
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_USER, email, msg.as_string())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
