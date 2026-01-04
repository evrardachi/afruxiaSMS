# -*- coding: utf-8 -*-
"""
Ce fichier gère l'envoi des SMS et conserve l'historique.
C'est le cœur du module : c'est ici qu'on envoie vraiment les SMS.
"""

from odoo import models, fields, api
from odoo.exceptions import UserError
import requests
import json
import logging

# Logger pour enregistrer les erreurs dans les logs Odoo
_logger = logging.getLogger(__name__)


class AfruxiaSMS(models.Model):
    """
    Modèle pour gérer l'envoi de SMS et conserver l'historique.
    Chaque SMS envoyé sera enregistré dans cette table.
    """
    _name = 'afruxia.sms'
    _description = 'SMS Afruxia'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # Pour le chatter et les activités
    _order = 'create_date desc'  # Trie par date de création décroissante
    _rec_name = 'recipient'

    # Informations du SMS
    recipient = fields.Char(
        string='Destinataire',
        required=True,
        help='Numéro de téléphone du destinataire (format: +242XXXXXXXXX)'
    )

    message = fields.Text(
        string='Message',
        required=True,
        help='Contenu du SMS à envoyer (max 160 caractères pour un SMS simple)'
    )

    sender = fields.Char(
        string='Expéditeur',
        help='Nom de l\'expéditeur (récupéré de la configuration)'
    )

    # État de l'envoi
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('sending', 'En cours d\'envoi'),
        ('sent', 'Envoyé'),
        ('failed', 'Échec'),
        ('delivered', 'Délivré')
    ], string='État', default='draft', tracking=True)

    # Informations techniques
    config_id = fields.Many2one(
        'afruxia.config',
        string='Configuration utilisée',
        help='Configuration API utilisée pour envoyer ce SMS'
    )

    sms_id = fields.Char(
        string='ID du SMS',
        readonly=True,
        help='Identifiant unique du SMS retourné par Afruxia'
    )

    response_message = fields.Text(
        string='Réponse de l\'API',
        readonly=True,
        help='Message de réponse de l\'API Afruxia'
    )

    error_message = fields.Text(
        string='Message d\'erreur',
        readonly=True,
        help='Détails de l\'erreur en cas d\'échec'
    )

    sent_date = fields.Datetime(
        string='Date d\'envoi',
        readonly=True,
        help='Date et heure d\'envoi du SMS'
    )

    delivery_date = fields.Datetime(
        string='Date de délivrance',
        readonly=True,
        help='Date et heure de délivrance du SMS au destinataire'
    )

    # Informations supplémentaires
    character_count = fields.Integer(
        string='Nombre de caractères',
        compute='_compute_character_count',
        help='Nombre de caractères dans le message'
    )

    sms_count = fields.Integer(
        string='Nombre de SMS',
        compute='_compute_sms_count',
        help='Nombre de SMS nécessaires (1 SMS = 160 caractères)'
    )

    @api.depends('message')
    def _compute_character_count(self):
        """Calcule le nombre de caractères dans le message."""
        for record in self:
            record.character_count = len(record.message) if record.message else 0

    @api.depends('message')
    def _compute_sms_count(self):
        """
        Calcule le nombre de SMS nécessaires.
        1 SMS = 160 caractères
        2 SMS = 306 caractères (153 par SMS à cause de l'en-tête)
        """
        for record in self:
            if not record.message:
                record.sms_count = 0
            else:
                length = len(record.message)
                if length <= 160:
                    record.sms_count = 1
                else:
                    # Pour les SMS multiples, on peut envoyer 153 caractères par segment
                    record.sms_count = (length // 153) + (1 if length % 153 > 0 else 0)

    def action_send_sms(self):
        """
        Méthode principale pour envoyer un SMS.
        Appelée quand l'utilisateur clique sur "Envoyer".
        """
        self.ensure_one()

        # Vérifie que le message n'est pas vide
        if not self.message or not self.recipient:
            raise UserError('Le destinataire et le message sont obligatoires.')

        # Récupère la configuration
        if not self.config_id:
            self.config_id = self.env['afruxia.config'].get_default_config()

        # Valide le numéro de téléphone (format basique)
        if not self.recipient.startswith('+'):
            raise UserError('Le numéro doit commencer par + (ex: +242XXXXXXXXX)')

        # Change l'état à "En cours d'envoi"
        self.write({
            'state': 'sending',
            'sender': self.config_id.sender_name
        })

        try:
            # Appel à l'API Afruxia
            result = self._call_afruxia_api()

            # Traite la réponse
            if result.get('success'):
                self.write({
                    'state': 'sent',
                    'sent_date': fields.Datetime.now(),
                    'sms_id': result.get('sms_id'),
                    'response_message': result.get('message', 'SMS envoyé avec succès')
                })

                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': 'Succès',
                        'message': f'SMS envoyé à {self.recipient}',
                        'type': 'success',
                        'sticky': False,
                    }
                }
            else:
                raise UserError(result.get('error', 'Erreur inconnue'))

        except Exception as e:
            error_msg = str(e)
            _logger.error(f'Erreur lors de l\'envoi du SMS : {error_msg}')

            self.write({
                'state': 'failed',
                'error_message': error_msg
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Erreur',
                    'message': f'Échec de l\'envoi : {error_msg}',
                    'type': 'danger',
                    'sticky': True,
                }
            }

    def _call_afruxia_api(self):
        """
        Méthode qui fait l'appel réel à l'API Afruxia.
        Adapté selon la documentation officielle Afruxia.
        """
        self.ensure_one()

        # Prépare l'URL et les en-têtes selon la doc Afruxia
        url = self.config_id.api_url
        headers = {
            'X-Client-ID': self.config_id.api_key,
            'X-Client-Secret': self.config_id.api_secret,
            'Content-Type': 'application/json',
        }

        # Prépare les données selon le format Afruxia
        payload = {
            'recipients': [self.recipient],  # Liste de destinataires
            'message': self.message,
            'sender_name': self.config_id.sender_name,
        }

        try:
            # Fait la requête HTTP POST
            _logger.info(f'Envoi SMS à {self.recipient} via Afruxia API')

            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30  # Timeout de 30 secondes
            )

            # Lève une exception si le code HTTP indique une erreur
            response.raise_for_status()

            # Parse la réponse JSON
            result = response.json()

            _logger.info(f'Réponse API Afruxia: {result}')

            # Traite la réponse selon le format Afruxia
            # La réponse exacte peut varier, adaptez si nécessaire
            if response.status_code == 200:
                # Succès
                return {
                    'success': True,
                    'sms_id': result.get('message_id', result.get('id', 'N/A')),
                    'message': result.get('message', 'SMS envoyé avec succès')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('error', result.get('message', 'Erreur inconnue de l\'API'))
                }

        except requests.exceptions.Timeout:
            _logger.error('Timeout lors de l\'appel à l\'API Afruxia')
            return {
                'success': False,
                'error': 'Timeout : l\'API Afruxia ne répond pas'
            }
        except requests.exceptions.ConnectionError:
            _logger.error('Erreur de connexion à l\'API Afruxia')
            return {
                'success': False,
                'error': 'Erreur de connexion à l\'API Afruxia. Vérifiez votre connexion internet.'
            }
        except requests.exceptions.HTTPError as e:
            error_msg = e.response.text
            try:
                error_json = e.response.json()
                error_msg = error_json.get('error', error_json.get('message', error_msg))
            except:
                pass

            _logger.error(f'Erreur HTTP {e.response.status_code}: {error_msg}')
            return {
                'success': False,
                'error': f'Erreur HTTP {e.response.status_code}: {error_msg}'
            }
        except ValueError as e:
            # Erreur de parsing JSON
            _logger.error(f'Erreur de parsing de la réponse: {str(e)}')
            return {
                'success': False,
                'error': f'Réponse invalide de l\'API : {str(e)}'
            }
        except Exception as e:
            _logger.error(f'Erreur inattendue lors de l\'appel API: {str(e)}')
            return {
                'success': False,
                'error': f'Erreur inattendue : {str(e)}'
            }

    def action_retry_send(self):
        """
        Bouton pour réessayer l'envoi d'un SMS échoué.
        """
        self.ensure_one()
        if self.state != 'failed':
            raise UserError('Vous ne pouvez réessayer que les SMS en échec.')

        self.write({'state': 'draft'})
        return self.action_send_sms()

    @api.model
    def send_sms(self, recipient, message, config_id=None):
        """
        Méthode utilitaire pour envoyer un SMS directement depuis le code Python.

        Utilisation dans d'autres modules :
        self.env['afruxia.sms'].send_sms('+242XXXXXXXXX', 'Votre message ici')

        :param recipient: Numéro du destinataire
        :param message: Message à envoyer
        :param config_id: ID de la configuration (optionnel)
        :return: Enregistrement du SMS créé
        """
        sms = self.create({
            'recipient': recipient,
            'message': message,
            'config_id': config_id or self.env['afruxia.config'].get_default_config().id
        })
        sms.action_send_sms()
        return sms
