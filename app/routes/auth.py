from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, current_user, login_required
from urllib.parse import urlparse
from authlib.integrations.flask_client import OAuth
from app import db
from app.models import User, Plan
from datetime import datetime
import os

bp = Blueprint('auth', __name__, url_prefix='/auth')

# Configuration OAuth
oauth = OAuth()


def init_oauth(app):
    oauth.init_app(app)

    # Google OAuth
    oauth.register(
        name='google',
        client_id=app.config['GOOGLE_CLIENT_ID'],
        client_secret=app.config['GOOGLE_CLIENT_SECRET'],
        server_metadata_url=app.config['GOOGLE_DISCOVERY_URL'],
        client_kwargs={'scope': 'openid email profile'}
    )


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash('Email ou mot de passe incorrect.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Votre compte a été désactivé. Veuillez contacter le support.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        next_page = request.args.get('next')
        if not next_page or urlparse(next_page).netloc != '':
            next_page = url_for('main.dashboard')

        flash(f'Bienvenue {user.first_name or user.email} !', 'success')
        return redirect(next_page)

    return render_template('auth/login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')

        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Cette adresse email est déjà utilisée.', 'danger')
            return redirect(url_for('auth.register'))

        # Créer l'utilisateur avec le plan gratuit par défaut
        free_plan = Plan.query.filter_by(name='Free').first()
        if not free_plan:
            # Créer le plan gratuit s'il n'existe pas
            free_plan = Plan(
                name='Free',
                price=0.0,
                max_subscriptions=5,
                description='Plan gratuit - Maximum 5 abonnements',
                features=['5 abonnements maximum', 'Catégories', 'Statistiques', 'Notifications']
            )
            db.session.add(free_plan)
            db.session.commit()

        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            plan=free_plan,
            trial_start_date=datetime.utcnow()  # Activer la période d'essai Premium de 7 jours
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        # Envoyer l'email de vérification
        from app.utils.email import send_verification_email
        send_verification_email(user)
        db.session.commit()

        flash('Votre compte a été créé avec succès ! Un email de confirmation a été envoyé à votre adresse. Vous bénéficiez de 7 jours d\'essai Premium gratuit.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté avec succès.', 'info')
    return redirect(url_for('main.index'))


@bp.route('/google')
def google_login():
    redirect_uri = url_for('auth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@bp.route('/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = token.get('userinfo')

        if user_info:
            email = user_info.get('email')
            user = User.query.filter_by(email=email).first()

            if not user:
                # Créer un nouveau compte
                free_plan = Plan.query.filter_by(name='Free').first()
                user = User(
                    email=email,
                    first_name=user_info.get('given_name'),
                    last_name=user_info.get('family_name'),
                    avatar_url=user_info.get('picture'),
                    oauth_provider='google',
                    oauth_id=user_info.get('sub'),
                    plan=free_plan,
                    trial_start_date=datetime.utcnow()  # Activer la période d'essai Premium de 7 jours
                )
                db.session.add(user)
                db.session.commit()

                # Envoyer l'email de vérification
                from app.utils.email import send_verification_email
                send_verification_email(user)
                db.session.commit()

                flash('Votre compte a été créé avec succès ! Un email de confirmation a été envoyé à votre adresse. Vous bénéficiez de 7 jours d\'essai Premium gratuit.', 'success')
            else:
                # Mettre à jour les infos OAuth si nécessaire
                if not user.oauth_provider:
                    user.oauth_provider = 'google'
                    user.oauth_id = user_info.get('sub')
                    db.session.commit()

            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            flash('Impossible de récupérer vos informations Google.', 'danger')
            return redirect(url_for('auth.login'))

    except Exception as e:
        flash(f'Erreur lors de la connexion avec Google: {str(e)}', 'danger')
        return redirect(url_for('auth.login'))


@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.first_name = request.form.get('first_name')
        current_user.last_name = request.form.get('last_name')
        current_user.default_currency = request.form.get('default_currency', 'EUR')

        # Changement de mot de passe
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        new_password_confirm = request.form.get('new_password_confirm')

        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('Mot de passe actuel incorrect.', 'danger')
                return redirect(url_for('auth.profile'))

            if new_password != new_password_confirm:
                flash('Les nouveaux mots de passe ne correspondent pas.', 'danger')
                return redirect(url_for('auth.profile'))

            current_user.set_password(new_password)
            flash('Votre mot de passe a été mis à jour.', 'success')

        db.session.commit()
        flash('Votre profil a été mis à jour avec succès.', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')


@bp.route('/verify-email/<token>')
def verify_email(token):
    """Vérifie l'email de l'utilisateur via le token"""
    user = User.query.filter_by(email_verification_token=token).first()

    if not user:
        flash('Le lien de vérification est invalide ou a expiré.', 'danger')
        return redirect(url_for('main.index'))

    if user.email_verified:
        flash('Votre email a déjà été vérifié.', 'info')
        return redirect(url_for('main.dashboard') if current_user.is_authenticated else url_for('auth.login'))

    user.verify_email()
    db.session.commit()

    flash('Votre adresse email a été confirmée avec succès ! Vous pouvez maintenant profiter pleinement de Subly Cloud.', 'success')

    if not current_user.is_authenticated:
        login_user(user)

    return redirect(url_for('main.dashboard'))


@bp.route('/resend-verification')
@login_required
def resend_verification():
    """Renvoie un email de vérification"""
    if current_user.email_verified:
        flash('Votre email est déjà vérifié.', 'info')
        return redirect(url_for('main.dashboard'))

    from app.utils.email import send_resend_verification_email

    if send_resend_verification_email(current_user):
        db.session.commit()
        flash('Un nouvel email de vérification a été envoyé à votre adresse.', 'success')
    else:
        flash('Erreur lors de l\'envoi de l\'email. Veuillez réessayer plus tard.', 'danger')

    return redirect(url_for('main.dashboard'))


@bp.route('/cancel-plan', methods=['POST'])
@login_required
def cancel_plan():
    """Annule le plan de l'utilisateur à la fin de la période actuelle"""
    if not current_user.plan or current_user.plan.name == 'Free':
        flash('Vous êtes déjà sur le plan gratuit.', 'info')
        return redirect(url_for('auth.profile'))

    # Calculer la date de fin de période (30 jours à partir d'aujourd'hui par défaut)
    # Dans un vrai système avec Stripe, cette date viendrait de l'API Stripe
    if current_user.plan.billing_period == 'yearly':
        period_end = datetime.utcnow() + timedelta(days=365)
    else:
        period_end = datetime.utcnow() + timedelta(days=30)

    current_user.plan_cancel_at_period_end = True
    current_user.plan_period_end_date = period_end

    db.session.commit()

    flash(f'Votre plan sera annulé le {period_end.strftime("%d/%m/%Y")}. Vous conserverez l\'accès Premium jusqu\'à cette date.', 'warning')
    return redirect(url_for('auth.profile'))


@bp.route('/reactivate-plan', methods=['POST'])
@login_required
def reactivate_plan():
    """Réactive le plan de l'utilisateur si l'annulation était programmée"""
    if not current_user.plan_cancel_at_period_end:
        flash('Votre plan n\'est pas programmé pour être annulé.', 'info')
        return redirect(url_for('auth.profile'))

    current_user.plan_cancel_at_period_end = False
    current_user.plan_period_end_date = None

    db.session.commit()

    flash('Votre plan a été réactivé avec succès ! L\'annulation a été annulée.', 'success')
    return redirect(url_for('auth.profile'))
