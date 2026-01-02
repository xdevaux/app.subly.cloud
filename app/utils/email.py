from flask import url_for, render_template_string
from flask_mail import Message, Mail
from app import mail
import os

def send_verification_email(user):
    """Envoie un email de vérification à l'utilisateur"""
    token = user.generate_verification_token()

    verification_url = url_for('auth.verify_email', token=token, _external=True)

    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 10px 10px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background: #667eea;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                color: #666;
                font-size: 12px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Bienvenue sur Subly Cloud !</h1>
            </div>
            <div class="content">
                <p>Bonjour {user.first_name or 'cher utilisateur'},</p>

                <p>Merci de vous être inscrit sur <strong>Subly Cloud</strong>, votre gestionnaire d'abonnements intelligent !</p>

                <p>Pour commencer à utiliser toutes nos fonctionnalités, veuillez confirmer votre adresse email en cliquant sur le bouton ci-dessous :</p>

                <div style="text-align: center;">
                    <a href="{verification_url}" class="button">Confirmer mon adresse email</a>
                </div>

                <p style="color: #28a745; font-weight: bold;">🎁 Bonus : Vous bénéficiez de 7 jours d'essai Premium gratuit !</p>

                <p>Avec Subly Cloud Premium, vous pouvez :</p>
                <ul>
                    <li>Gérer un nombre illimité d'abonnements</li>
                    <li>Créer des catégories et services personnalisés</li>
                    <li>Accéder aux statistiques avancées</li>
                    <li>Exporter vos données</li>
                </ul>

                <p>Si vous n'avez pas créé de compte sur Subly Cloud, vous pouvez ignorer cet email.</p>

                <p>À bientôt,<br>L'équipe Subly Cloud</p>
            </div>
            <div class="footer">
                <p>Cet email a été envoyé par Subly Cloud</p>
                <p>Si le bouton ne fonctionne pas, copiez ce lien dans votre navigateur :<br>
                {verification_url}</p>
            </div>
        </div>
    </body>
    </html>
    """

    text_body = f"""
    Bienvenue sur Subly Cloud !

    Bonjour {user.first_name or 'cher utilisateur'},

    Merci de vous être inscrit sur Subly Cloud, votre gestionnaire d'abonnements intelligent !

    Pour commencer à utiliser toutes nos fonctionnalités, veuillez confirmer votre adresse email en cliquant sur ce lien :
    {verification_url}

    🎁 Bonus : Vous bénéficiez de 7 jours d'essai Premium gratuit !

    Avec Subly Cloud Premium, vous pouvez :
    - Gérer un nombre illimité d'abonnements
    - Créer des catégories et services personnalisés
    - Accéder aux statistiques avancées
    - Exporter vos données

    Si vous n'avez pas créé de compte sur Subly Cloud, vous pouvez ignorer cet email.

    À bientôt,
    L'équipe Subly Cloud
    """

    msg = Message(
        subject='Bienvenue sur Subly Cloud - Confirmez votre email',
        sender=os.getenv('MAIL_DEFAULT_SENDER', 'noreply@subly.cloud'),
        recipients=[user.email],
        body=text_body,
        html=html_body
    )

    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email : {e}")
        return False


def send_resend_verification_email(user):
    """Renvoie un email de vérification"""
    return send_verification_email(user)
