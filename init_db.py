#!/usr/bin/env python3
"""
Script d'initialisation de la base de données
Crée les tables et ajoute les données de base (plans, catégories)
"""

from app import create_app, db
from app.models import Plan, Category

def init_database():
    app = create_app()

    with app.app_context():
        print("Création des tables...")
        db.create_all()
        print("Tables créées avec succès !")

        # Vérifier si les plans existent déjà
        if Plan.query.count() == 0:
            print("\nCréation des plans...")

            # Plan gratuit
            free_plan = Plan(
                name='Free',
                price=0.0,
                currency='EUR',
                billing_period='monthly',
                max_subscriptions=5,
                description='Plan gratuit avec un maximum de 5 abonnements',
                features=[
                    '5 abonnements maximum',
                    'Accès aux catégories par défaut',
                    'Statistiques détaillées',
                    'Notifications de renouvellement',
                    'Support communautaire'
                ],
                is_active=True
            )

            # Plan Premium Mensuel
            premium_plan = Plan(
                name='Premium',
                price=4.99,
                currency='EUR',
                billing_period='monthly',
                max_subscriptions=None,
                description='Plan Premium mensuel avec abonnements illimités et catégories personnalisées',
                features=[
                    'Abonnements illimités',
                    'Catégories personnalisées (logos, couleurs, icônes)',
                    'Accès aux catégories par défaut',
                    'Statistiques avancées',
                    'Notifications personnalisables',
                    'Support prioritaire',
                    'Export des données (PDF, CSV)',
                    'Accès anticipé aux nouvelles fonctionnalités'
                ],
                is_active=True
            )

            # Plan Premium Annuel
            premium_annual_plan = Plan(
                name='Premium Annual',
                price=49.99,
                currency='EUR',
                billing_period='yearly',
                max_subscriptions=None,
                description='Plan Premium annuel avec abonnements illimités et catégories personnalisées',
                features=[
                    'Abonnements illimités',
                    'Catégories personnalisées (logos, couleurs, icônes)',
                    'Accès aux catégories par défaut',
                    'Statistiques avancées',
                    'Notifications personnalisables',
                    'Support prioritaire',
                    'Export des données (PDF, CSV)',
                    'Accès anticipé aux nouvelles fonctionnalités',
                    '2 mois gratuits (économie de 10€)'
                ],
                is_active=True
            )

            db.session.add(free_plan)
            db.session.add(premium_plan)
            db.session.add(premium_annual_plan)
            db.session.commit()
            print("Plans créés avec succès !")
        else:
            print("\nLes plans existent déjà.")

        # Vérifier si les catégories existent déjà
        if Category.query.count() == 0:
            print("\nCréation des catégories par défaut...")

            categories = [
                {
                    'name': 'Streaming Vidéo',
                    'description': 'Services de streaming vidéo et films',
                    'color': '#E50914',
                    'icon': 'fas fa-film'
                },
                {
                    'name': 'Streaming Audio',
                    'description': 'Services de musique et podcasts',
                    'color': '#1DB954',
                    'icon': 'fas fa-music'
                },
                {
                    'name': 'Cloud & Stockage',
                    'description': 'Services de stockage en ligne',
                    'color': '#4285F4',
                    'icon': 'fas fa-cloud'
                },
                {
                    'name': 'Productivité',
                    'description': 'Outils de productivité et bureautique',
                    'color': '#FF6900',
                    'icon': 'fas fa-briefcase'
                },
                {
                    'name': 'Développement',
                    'description': 'Outils pour développeurs',
                    'color': '#6366F1',
                    'icon': 'fas fa-code'
                },
                {
                    'name': 'Design & Créatif',
                    'description': 'Outils de design et création',
                    'color': '#FF0080',
                    'icon': 'fas fa-palette'
                },
                {
                    'name': 'Fitness & Santé',
                    'description': 'Applications de fitness et santé',
                    'color': '#00C851',
                    'icon': 'fas fa-heartbeat'
                },
                {
                    'name': 'Gaming',
                    'description': 'Services de jeux et gaming',
                    'color': '#9146FF',
                    'icon': 'fas fa-gamepad'
                },
                {
                    'name': 'Actualités & Médias',
                    'description': 'Abonnements à des journaux et médias',
                    'color': '#1E1E1E',
                    'icon': 'fas fa-newspaper'
                },
                {
                    'name': 'Autre',
                    'description': 'Autres types d\'abonnements',
                    'color': '#6C757D',
                    'icon': 'fas fa-ellipsis-h'
                }
            ]

            for cat_data in categories:
                category = Category(**cat_data)
                db.session.add(category)

            db.session.commit()
            print(f"{len(categories)} catégories créées avec succès !")
        else:
            print("\nLes catégories existent déjà.")

        print("\n✅ Initialisation terminée avec succès !")
        print("\nVous pouvez maintenant lancer l'application avec: python run.py")


if __name__ == '__main__':
    init_database()
