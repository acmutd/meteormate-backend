# Created by Ryan Polasky | 10/22/25
# ACM MeteorMate | All Rights Reserved

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from fastapi import HTTPException


async def send_verification_email(email: str, code: str):
    """Send verification code via email with MeteorMate branding"""
    try:
        # create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '🌟 Verify Your MeteorMate Account'
        msg['From'] = settings.EMAIL_USER
        msg['To'] = email

        # HTML email body with MeteorMate styling
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <meta name="color-scheme" content="light dark">
            <meta name="supported-color-schemes" content="light dark">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap');

                @media only screen and (max-width: 600px) {{
                    .container {{
                        width: 100% !important;
                        padding: 20px !important;
                    }}
                    .code-box {{
                        padding: 30px 20px !important;
                        font-size: 36px !important;
                        letter-spacing: 8px !important;
                    }}
                    .header-text {{
                        font-size: 28px !important;
                    }}
                }}
            </style>
        </head>
        <body style="margin: 0; padding: 0; font-family: 'Outfit', Arial, sans-serif; background-color: #000000;">
            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #000000;">
                <tr>
                    <td style="padding: 40px 20px;">
                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" class="container" style="margin: 0 auto; background-color: #000000; border-radius: 16px; overflow: hidden;">

                            <!-- Header with Logo -->
                            <tr>
                                <td style="padding: 40px 40px 20px 40px; text-align: center;">
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <tr>
                                            <td style="text-align: center;">
                                                <!-- Logo placeholder - replace with actual logo URL -->
                                                <div style="background-color: #2B2B2B; width: 80px; height: 80px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin: 0 auto;">
                                                    <span style="font-size: 40px; color: #FFFFFF;">🌠</span>
                                                </div>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="padding-top: 20px; text-align: center;">
                                                <h1 style="margin: 0; font-family: 'Oranienbaum', Georgia, serif; font-size: 32px; font-weight: 300; color: #FFFFFF; letter-spacing: 1px;">MeteorMate</h1>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>

                            <!-- Welcome Message -->
                            <tr>
                                <td style="padding: 20px 40px;">
                                    <h2 class="header-text" style="margin: 0 0 10px 0; font-family: 'Outfit', Arial, sans-serif; font-size: 32px; font-weight: 700; color: #FFFFFF; text-align: center;">Welcome! 👋</h2>
                                    <p style="margin: 0; font-family: 'Outfit', Arial, sans-serif; font-size: 16px; font-weight: 400; color: rgba(255, 255, 255, 0.8); text-align: center; line-height: 1.6;">
                                        You're one step away from finding your perfect roommate at UT Dallas!
                                    </p>
                                </td>
                            </tr>

                            <!-- Verification Code Box -->
                            <tr>
                                <td style="padding: 30px 40px;">
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <tr>
                                            <td style="text-align: center;">
                                                <p style="margin: 0 0 20px 0; font-family: 'Outfit', Arial, sans-serif; font-size: 16px; font-weight: 400; color: rgba(255, 255, 255, 0.9);">
                                                    Your verification code is:
                                                </p>
                                                <div class="code-box" style="background: linear-gradient(135deg, #FB923C 0%, #FCD34D 100%); padding: 40px 30px; border-radius: 12px; margin: 0 auto; max-width: 400px;">
                                                    <p style="margin: 0; font-family: 'Outfit', Arial, sans-serif; font-size: 48px; font-weight: 700; color: #000000; letter-spacing: 12px; text-align: center;">
                                                        {code}
                                                    </p>
                                                </div>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>

                            <!-- Expiration Notice -->
                            <tr>
                                <td style="padding: 0 40px 30px 40px;">
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: rgba(80, 146, 117, 0.15); border-left: 4px solid #509275; border-radius: 8px;">
                                        <tr>
                                            <td style="padding: 20px;">
                                                <p style="margin: 0; font-family: 'Outfit', Arial, sans-serif; font-size: 14px; font-weight: 400; color: rgba(255, 255, 255, 0.8); line-height: 1.5;">
                                                    <strong style="color: #509275;">⏰ Important:</strong> This code will expire in <strong style="color: #FFFFFF;">30 minutes</strong>. If you didn't create an account, you can safely ignore this email.
                                                </p>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>

                            <!-- CTA Section -->
                            <tr>
                                <td style="padding: 0 40px 40px 40px; text-align: center;">
                                    <p style="margin: 0 0 20px 0; font-family: 'Outfit', Arial, sans-serif; font-size: 16px; font-weight: 400; color: rgba(255, 255, 255, 0.7); line-height: 1.6;">
                                        Ready to find your perfect match? Enter your code and start swiping!
                                    </p>
                                </td>
                            </tr>

                            <!-- Divider -->
                            <tr>
                                <td style="padding: 0 40px;">
                                    <div style="height: 1px; background-color: rgba(255, 255, 255, 0.1);"></div>
                                </td>
                            </tr>

                            <!-- Footer -->
                            <tr>
                                <td style="padding: 30px 40px;">
                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                        <tr>
                                            <td style="text-align: center; padding-bottom: 20px;">
                                                <p style="margin: 0 0 15px 0; font-family: 'Outfit', Arial, sans-serif; font-size: 14px; font-weight: 400; color: rgba(255, 255, 255, 0.6);">
                                                    Need help? Contact us at
                                                </p>
                                                <a href="mailto:info@meteormate.com" style="font-family: 'Outfit', Arial, sans-serif; font-size: 14px; font-weight: 400; color: #509275; text-decoration: none;">
                                                    info@meteormate.com
                                                </a>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="text-align: center; padding-bottom: 10px;">
                                                <p style="margin: 0; font-family: 'Outfit', Arial, sans-serif; font-size: 12px; font-weight: 400; color: rgba(255, 255, 255, 0.4);">
                                                    © 2025 MeteorMate UTD. All rights reserved.
                                                </p>
                                                <p style="margin: 5px 0 0 0; font-family: 'Outfit', Arial, sans-serif; font-size: 12px; font-weight: 400; color: rgba(255, 255, 255, 0.4);">
                                                    Powered by ACM Development
                                                </p>
                                            </td>
                                        </tr>
                                        <tr>
                                            <td style="text-align: center; padding-top: 15px;">
                                                <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto;">
                                                    <tr>
                                                        <td style="padding: 0 8px;">
                                                            <a href="https://www.linkedin.com/company/acmutd/posts/?feedView=all" style="color: rgba(255, 255, 255, 0.5); text-decoration: none; font-size: 11px;">LinkedIn</a>
                                                        </td>
                                                        <td style="padding: 0 8px; color: rgba(255, 255, 255, 0.3);">•</td>
                                                        <td style="padding: 0 8px;">
                                                            <a href="https://www.instagram.com/acmutd/" style="color: rgba(255, 255, 255, 0.5); text-decoration: none; font-size: 11px;">Instagram</a>
                                                        </td>
                                                        <td style="padding: 0 8px; color: rgba(255, 255, 255, 0.3);">•</td>
                                                        <td style="padding: 0 8px;">
                                                            <a href="#" style="color: rgba(255, 255, 255, 0.5); text-decoration: none; font-size: 11px;">Privacy</a>
                                                        </td>
                                                    </tr>
                                                </table>
                                            </td>
                                        </tr>
                                    </table>
                                </td>
                            </tr>

                        </table>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        msg.attach(MIMEText(html, 'html'))

        # send email via SMTP
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_USER, email, msg.as_string())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


async def send_inactive_notices(email: str, notice_num: int):
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
            email_subj = "Your MeteorMate account is now inactive"
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

        # HTML email body with MeteorMate styling
        html = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <meta name="color-scheme" content="light dark">
                <meta name="supported-color-schemes" content="light dark">
                <style>
                    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&display=swap');
            
                    @media only screen and (max-width: 600px) {{
                        .container {{
                            width: 100% !important;
                            padding: 20px !important;
                        }}
                        .header-text {{
                            font-size: 28px !important;
                        }}
                        .button {{
                            padding: 16px 32px !important;
                            font-size: 14px !important;
                        }}
                    }}
                </style>
            </head>
            <body style="margin: 0; padding: 0; font-family: 'Outfit', Arial, sans-serif; background-color: #000000;">
                <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: #000000;">
                    <tr>
                        <td style="padding: 40px 20px;">
                            <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="600" class="container" style="margin: 0 auto; background-color: #000000; border-radius: 16px; overflow: hidden;">
            
                                <!-- Header with Logo -->
                                <tr>
                                    <td style="padding: 40px 40px 20px 40px; text-align: center;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                            <tr>
                                                <td style="text-align: center;">
                                                    <div style="background-color: #2B2B2B; width: 80px; height: 80px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin: 0 auto;">
                                                        <span style="font-size: 40px; color: #FFFFFF;">🌠</span>
                                                    </div>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="padding-top: 20px; text-align: center;">
                                                    <h1 style="margin: 0; font-family: 'Oranienbaum', Georgia, serif; font-size: 32px; font-weight: 300; color: #FFFFFF; letter-spacing: 1px;">MeteorMate</h1>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
            
                                <!-- Main Message -->
                                <tr>
                                    <td style="padding: 20px 40px;">
                                        <h2 class="header-text" style="margin: 0 0 10px 0; font-family: 'Outfit', Arial, sans-serif; font-size: 32px; font-weight: 700; color: #FFFFFF; text-align: center;">We Miss You! 😢</h2>
                                        <p style="margin: 0; font-family: 'Outfit', Arial, sans-serif; font-size: 16px; font-weight: 400; color: rgba(255, 255, 255, 0.8); text-align: center; line-height: 1.6;">
                                            It's been a while since we've seen you around campus...
                                        </p>
                                    </td>
                                </tr>
            
                                <!-- Warning Box -->
                                <tr>
                                    <td style="padding: 30px 40px;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background: linear-gradient(135deg, rgba(251, 146, 60, 0.15) 0%, rgba(252, 211, 77, 0.15) 100%); border-left: 4px solid #FB923C; border-radius: 12px;">
                                            <tr>
                                                <td style="padding: 30px;">
                                                    <p style="margin: 0 0 15px 0; font-family: 'Outfit', Arial, sans-serif; font-size: 18px; font-weight: 700; color: #FB923C;">
                                                        ⚠️ Account Inactivity Warning
                                                    </p>
                                                    <p style="margin: 0; font-family: 'Outfit', Arial, sans-serif; font-size: 15px; font-weight: 400; color: rgba(255, 255, 255, 0.85); line-height: 1.6;">
                                                        f{inactivity_warning}
                                                    </p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
            
                                <!-- What This Means -->
                                <tr>
                                    <td style="padding: 0 40px 30px 40px;">
                                        <p style="margin: 0 0 15px 0; font-family: 'Outfit', Arial, sans-serif; font-size: 16px; font-weight: 700; color: #FFFFFF;">
                                            What does this mean?
                                        </p>
                                        <ul style="margin: 0; padding-left: 20px; font-family: 'Outfit', Arial, sans-serif; font-size: 15px; font-weight: 400; color: rgba(255, 255, 255, 0.75); line-height: 1.8;">
                                            <li style="margin-bottom: 8px;">Your profile will be hidden from other users</li>
                                            <li style="margin-bottom: 8px;">You won't appear in matches or searches</li>
                                            <li style="margin-bottom: 8px;">Your account stays safe - it won't be deleted for ~2 years</li>
                                            <li>Simply log in anytime to reactivate your profile!</li>
                                        </ul>
                                    </td>
                                </tr>
            
                                <!-- CTA Button -->
                                <tr>
                                    <td style="padding: 0 40px 30px 40px; text-align: center;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto;">
                                            <tr>
                                                <td style="border-radius: 8px; background: linear-gradient(135deg, #FB923C 0%, #FCD34D 100%);">
                                                    <a href="https://meteormate.com/authentication" class="button" style="display: inline-block; padding: 18px 40px; font-family: 'Outfit', Arial, sans-serif; font-size: 16px; font-weight: 700; color: #000000; text-decoration: none; border-radius: 8px;">
                                                        Sign In Now
                                                    </a>
                                                </td>
                                            </tr>
                                        </table>
                                        <p style="margin: 15px 0 0 0; font-family: 'Outfit', Arial, sans-serif; font-size: 14px; font-weight: 400; color: rgba(255, 255, 255, 0.6);">
                                            Keep your profile active and never miss a match!
                                        </p>
                                    </td>
                                </tr>
            
                                <!-- Info Notice -->
                                <tr>
                                    <td style="padding: 0 40px 30px 40px;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%" style="background-color: rgba(80, 146, 117, 0.15); border-left: 4px solid #509275; border-radius: 8px;">
                                            <tr>
                                                <td style="padding: 20px;">
                                                    <p style="margin: 0; font-family: 'Outfit', Arial, sans-serif; font-size: 14px; font-weight: 400; color: rgba(255, 255, 255, 0.8); line-height: 1.5;">
                                                        <strong style="color: #509275;">ℹ️ Good to know:</strong> If your account remains inactive for a 2 years after being marked inactive, it will be permanently deleted. But don't worry - logging in anytime before that resets the timer!
                                                    </p>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
            
                                <!-- Divider -->
                                <tr>
                                    <td style="padding: 0 40px;">
                                        <div style="height: 1px; background-color: rgba(255, 255, 255, 0.1);"></div>
                                    </td>
                                </tr>
            
                                <!-- Footer -->
                                <tr>
                                    <td style="padding: 30px 40px;">
                                        <table role="presentation" cellspacing="0" cellpadding="0" border="0" width="100%">
                                            <tr>
                                                <td style="text-align: center; padding-bottom: 20px;">
                                                    <p style="margin: 0 0 15px 0; font-family: 'Outfit', Arial, sans-serif; font-size: 14px; font-weight: 400; color: rgba(255, 255, 255, 0.6);">
                                                        Need help? Contact us at
                                                    </p>
                                                    <a href="mailto:info@meteormate.com" style="font-family: 'Outfit', Arial, sans-serif; font-size: 14px; font-weight: 400; color: #509275; text-decoration: none;">
                                                        info@meteormate.com
                                                    </a>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="text-align: center; padding-bottom: 10px;">
                                                    <p style="margin: 0; font-family: 'Outfit', Arial, sans-serif; font-size: 12px; font-weight: 400; color: rgba(255, 255, 255, 0.4);">
                                                        © 2025 MeteorMate UTD. All rights reserved.
                                                    </p>
                                                    <p style="margin: 5px 0 0 0; font-family: 'Outfit', Arial, sans-serif; font-size: 12px; font-weight: 400; color: rgba(255, 255, 255, 0.4);">
                                                        Powered by ACM Development
                                                    </p>
                                                </td>
                                            </tr>
                                            <tr>
                                                <td style="text-align: center; padding-top: 15px;">
                                                    <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto;">
                                                        <tr>
                                                            <td style="padding: 0 8px;">
                                                                <a href="https://www.linkedin.com/company/acmutd/posts/?feedView=all" style="color: rgba(255, 255, 255, 0.5); text-decoration: none; font-size: 11px;">LinkedIn</a>
                                                            </td>
                                                            <td style="padding: 0 8px; color: rgba(255, 255, 255, 0.3);">•</td>
                                                            <td style="padding: 0 8px;">
                                                                <a href="https://www.instagram.com/acmutd/" style="color: rgba(255, 255, 255, 0.5); text-decoration: none; font-size: 11px;">Instagram</a>
                                                            </td>
                                                            <td style="padding: 0 8px; color: rgba(255, 255, 255, 0.3);">•</td>
                                                            <td style="padding: 0 8px;">
                                                                <a href="#" style="color: rgba(255, 255, 255, 0.5); text-decoration: none; font-size: 11px;">Privacy</a>
                                                            </td>
                                                        </tr>
                                                    </table>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
            
                            </table>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """

        msg.attach(MIMEText(html, 'html'))

        # send email via SMTP
        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
            server.sendmail(settings.EMAIL_USER, email, msg.as_string())

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")
