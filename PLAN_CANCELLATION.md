# Système de résiliation de plan

## Fonctionnement

Le système de résiliation de plan permet aux utilisateurs d'annuler leur abonnement Premium avec effet à la fin de leur période de facturation actuelle. **Aucun cron job n'est nécessaire** - le système gère automatiquement la rétrogradation.

## Architecture

### Champs de base de données (User)

- `plan_cancel_at_period_end` (Boolean) : Indique si une résiliation est programmée
- `plan_period_end_date` (DateTime) : Date de fin de la période actuelle (date effective de résiliation)

### Logique automatique

La vérification et la rétrogradation se font **automatiquement** via la méthode `check_and_process_plan_expiration()` qui est appelée à chaque fois que :
- `is_premium()` est appelé
- `can_add_subscription()` est appelé

Cela signifie que dès qu'un utilisateur accède à une fonctionnalité nécessitant une vérification Premium, le système :
1. Vérifie si une résiliation est programmée
2. Vérifie si la date de fin est dépassée
3. Si oui, rétrograde automatiquement l'utilisateur vers le plan gratuit
4. Réinitialise les flags de résiliation

### Routes disponibles

#### `/auth/cancel-plan` (POST)
Permet à un utilisateur de demander la résiliation de son plan.

**Comportement :**
- Vérifie que l'utilisateur a un plan Premium
- Calcule la date de fin de période :
  - Plan mensuel : +30 jours
  - Plan annuel : +365 jours
- Marque `plan_cancel_at_period_end = True`
- Enregistre `plan_period_end_date`
- Affiche un message confirmant la résiliation programmée

**Restrictions :**
- Impossible si l'utilisateur est déjà sur le plan gratuit

#### `/auth/reactivate-plan` (POST)
Permet à un utilisateur d'annuler sa demande de résiliation avant la date effective.

**Comportement :**
- Vérifie qu'une résiliation est programmée
- Réinitialise `plan_cancel_at_period_end = False`
- Réinitialise `plan_period_end_date = None`
- Affiche un message de confirmation

## Interface utilisateur (Profil)

### Affichage selon l'état

#### 1. Plan actif (pas de résiliation programmée)

```
┌─────────────────────────────────────────────┐
│ Plan actuel                                 │
├─────────────────────────────────────────────┤
│ Plan Premium                                │
│                                             │
│ ℹ️ Vous pouvez annuler votre abonnement    │
│   à tout moment. L'annulation prendra      │
│   effet à la fin de votre période de       │
│   facturation actuelle.                    │
│                                             │
│               [Annuler mon plan]            │
└─────────────────────────────────────────────┘
```

#### 2. Résiliation programmée

```
┌─────────────────────────────────────────────┐
│ Plan actuel                                 │
├─────────────────────────────────────────────┤
│ Plan Premium                                │
│                                             │
│ ⚠️ Annulation programmée                   │
│ Votre plan Premium sera annulé le          │
│ 15/02/2026. Vous conserverez l'accès       │
│ Premium jusqu'à cette date.                │
│                                             │
│         [Réactiver mon abonnement]          │
└─────────────────────────────────────────────┘
```

### Modal de confirmation

Lors du clic sur "Annuler mon plan", une modal s'affiche avec :
- Titre : "Confirmer l'annulation"
- Explications détaillées :
  - Le plan reste actif jusqu'à la fin de période
  - Tous les accès Premium sont conservés
  - Rétrogradation automatique vers le plan gratuit après la date
  - Possibilité de réactivation à tout moment
- Boutons :
  - "Non, garder mon plan" (annule)
  - "Oui, annuler mon plan" (confirme)

## Flux utilisateur

### Scénario 1 : Résiliation simple

1. Utilisateur Premium clique sur "Annuler mon plan"
2. Lit les explications dans la modal
3. Confirme l'annulation
4. → `plan_cancel_at_period_end = True`, date calculée
5. Voit l'alerte warning avec la date de fin
6. Continue à utiliser normalement avec accès Premium
7. Après la date de fin :
   - Premier appel à `is_premium()` → rétrogradation automatique
   - Perte des accès Premium
   - Passage au plan gratuit

### Scénario 2 : Résiliation puis réactivation

1. Utilisateur annule son plan (voir scénario 1)
2. Change d'avis avant la date de fin
3. Clique sur "Réactiver mon abonnement"
4. → `plan_cancel_at_period_end = False`, date réinitialisée
5. Garde son plan Premium normalement

## Avantages de cette approche

✅ **Pas de cron job nécessaire**
- Pas de configuration système complexe
- Pas de script externe à maintenir
- Rétrogradation à la demande lors de l'accès

✅ **Transparent pour l'utilisateur**
- Accès conservé jusqu'à la fin de période
- Rétrogradation automatique et invisible
- Pas de surprises

✅ **Simple et robuste**
- Logique centralisée dans le modèle User
- Vérification automatique à chaque accès
- Impossible d'oublier de traiter une résiliation

✅ **Réversible**
- L'utilisateur peut annuler sa résiliation à tout moment
- Un simple clic pour réactiver

## Notes techniques

### Performance

La méthode `check_and_process_plan_expiration()` est appelée fréquemment mais :
- Ne fait qu'une vérification de date simple
- N'effectue une requête SQL que si une résiliation est programmée ET expirée
- Impact négligeable sur les performances

### Base de données

Une seule requête supplémentaire est nécessaire lors de la rétrogradation :
```sql
SELECT * FROM plans WHERE name = 'Free' LIMIT 1;
```

Cette requête n'est exécutée qu'une seule fois par utilisateur au moment de l'expiration.

### Migration

Migration appliquée : `f1e1984ba151_add_plan_cancellation_fields.py`

Champs ajoutés :
- `users.plan_cancel_at_period_end` (Boolean, default False)
- `users.plan_period_end_date` (DateTime, nullable)

## Tests recommandés

1. **Test de résiliation :**
   - Créer un utilisateur Premium
   - Demander la résiliation
   - Vérifier que l'accès Premium est conservé
   - Vérifier l'affichage de l'alerte

2. **Test de réactivation :**
   - Partir d'un plan avec résiliation programmée
   - Cliquer sur "Réactiver"
   - Vérifier que l'alerte disparaît

3. **Test d'expiration :**
   - Créer un utilisateur avec résiliation programmée
   - Mettre `plan_period_end_date` dans le passé (via SQL)
   - Appeler `is_premium()`
   - Vérifier la rétrogradation automatique

## Améliorations futures possibles

- Ajouter un email de notification avant la date d'expiration
- Ajouter des statistiques sur les résiliations dans l'admin
- Permettre à l'admin d'annuler des résiliations
- Ajouter un champ "raison de résiliation" pour feedback
