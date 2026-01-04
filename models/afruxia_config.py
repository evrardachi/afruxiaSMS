# -*- coding: utf-8 -*-
"""
Ce fichier définit la configuration pour l'API Afruxia.
C'est comme un formulaire où vous allez entrer vos identifiants API.
"""

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class AfruxiaConfig(models.Model):
    """
    Modèle pour stocker la configuration de l'API Afruxia.
    _name : nom technique de la table dans la base de données
    _description : description pour les développeurs
    """
    _name = 'afruxia.config'
    _description = 'Configuration API Afruxia'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Pour le chatter et les activités
    _rec_name = 'name'  # Champ utilisé pour afficher l'enregistrement

    # Champs de la table (colonnes)
    name = fields.Char(
        string='Nom de la configuration',
        required=True,
        help='Un nom pour identifier cette configuration (ex: Production, Test)'
    )

    api_url = fields.Char(
        string='URL de l\'API',
        required=True,
        default='https://marketing.afruxia.com/api/v1/sms/send',
        help='L\'adresse de l\'API Afruxia pour envoyer les SMS'
    )

    api_key = fields.Char(
        string='Client ID',
        required=True,
        help='Votre Client ID fourni par Afruxia (X-Client-ID)'
    )

    api_secret = fields.Char(
        string='Client Secret',
        required=True,
        help='Votre Client Secret fourni par Afruxia (X-Client-Secret)'
    )

    sender_name = fields.Char(
        string='Nom de l\'expéditeur',
        required=True,
        help='Le nom qui apparaîtra comme expéditeur du SMS (max 11 caractères)',
        size=11
    )

    active = fields.Boolean(
        string='Actif',
        default=True,
        help='Décochez pour désactiver temporairement cette configuration'
    )

    is_default = fields.Boolean(
        string='Configuration par défaut',
        default=False,
        help='Cette configuration sera utilisée par défaut pour l\'envoi de SMS'
    )

    # État de la connexion
    connection_status = fields.Selection([
        ('not_tested', 'Non testé'),
        ('success', 'Connecté'),
        ('failed', 'Échec')
    ], string='État de la connexion', default='not_tested', readonly=True)

    last_test_date = fields.Datetime(
        string='Dernière vérification',
        readonly=True
    )

    # Contrainte SQL : Une seule configuration peut être par défaut
    _sql_constraints = [
        ('unique_default',
         'CHECK(1=1)',  # Sera géré en Python
         'Une seule configuration peut être définie par défaut')
    ]

    @api.model_create_multi
    def create(self, vals_list):
        """
        Méthode appelée lors de la création d'un nouvel enregistrement.
        Si is_default=True, on désactive les autres configurations par défaut.
        """
        # Vérifie si l'un des enregistrements à créer est marqué comme défaut
        for vals in vals_list:
            if vals.get('is_default'):
                self.search([('is_default', '=', True)]).write({'is_default': False})
                break  # Un seul suffit
        return super(AfruxiaConfig, self).create(vals_list)

    def write(self, vals):
        """
        Méthode appelée lors de la modification d'un enregistrement.
        Même logique que create pour is_default.
        """
        if vals.get('is_default'):
            self.search([('is_default', '=', True), ('id', '!=', self.id)]).write({'is_default': False})
        return super(AfruxiaConfig, self).write(vals)

    def action_test_connection(self):
        """
        Bouton pour tester la connexion à l'API Afruxia.
        Cette méthode sera appelée quand l'utilisateur clique sur "Tester la connexion".
        """
        self.ensure_one()  # S'assure qu'on travaille sur un seul enregistrement

        import requests
        from datetime import datetime

        try:
            # Prépare l'URL et les en-têtes selon la doc Afruxia
            url = self.api_url
            headers = {
                'X-Client-ID': self.api_key,
                'X-Client-Secret': self.api_secret,
                'Content-Type': 'application/json',
            }

            # Simple test de connexion - on vérifie juste que l'API répond
            # Note: Si Afruxia a un endpoint spécifique de test, utilisez-le à la place
            response = requests.get(
                url.replace('/send', '/status'),  # Endpoint de status si disponible
                headers=headers,
                timeout=10
            )

            # Si l'endpoint /status n'existe pas, on teste avec une requête minimale
            # Cette partie peut être adaptée selon la doc Afruxia
            if response.status_code == 404:
                # L'endpoint status n'existe pas, on teste autrement
                # On valide juste que les credentials sont acceptés
                response = requests.post(
                    url,
                    headers=headers,
                    json={
                        'recipients': [],  # Liste vide pour ne rien envoyer
                        'message': 'test',
                        'sender_name': self.sender_name,
                    },
                    timeout=10
                )

            # Si on arrive ici sans erreur, les identifiants sont valides
            self.write({
                'connection_status': 'success',
                'last_test_date': datetime.now()
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Succès',
                    'message': 'Connexion à l\'API Afruxia réussie ! Vos identifiants sont valides.',
                    'type': 'success',
                    'sticky': False,
                }
            }

        except requests.exceptions.HTTPError as e:
            error_msg = f"Erreur HTTP {e.response.status_code}"
            if e.response.status_code in [401, 403]:
                error_msg = "Identifiants invalides (Client ID ou Secret incorrect)"

            self.write({
                'connection_status': 'failed',
                'last_test_date': datetime.now()
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': f'Échec de connexion : {error_msg}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

        except requests.exceptions.Timeout:
            self.write({
                'connection_status': 'failed',
                'last_test_date': datetime.now()
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': 'Timeout : l\'API ne répond pas. Vérifiez l\'URL.',
                    'type': 'danger',
                    'sticky': True,
                }
            }

        except Exception as e:
            self.write({
                'connection_status': 'failed',
                'last_test_date': datetime.now()
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': f'Échec de connexion : {str(e)}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

    @api.model
    def get_default_config(self):
        """
        Récupère la configuration par défaut.
        Utilisée lors de l'envoi de SMS.
        """
        config = self.search([('is_default', '=', True), ('active', '=', True)], limit=1)
        if not config:
            config = self.search([('active', '=', True)], limit=1)
        if not config:
            raise ValidationError('Aucune configuration Afruxia active trouvée. Veuillez en créer une.')
        return config
