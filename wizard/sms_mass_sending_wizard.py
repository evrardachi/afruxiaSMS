# -*- coding: utf-8 -*-
"""
Wizard (Assistant) pour l'envoi de SMS en masse.
Permet de sélectionner plusieurs destinataires et d'envoyer le même message à tous.
"""

from odoo import models, fields, api
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class SmsMassSendingWizard(models.TransientModel):
    """
    Modèle transitoire (wizard) pour l'envoi en masse de SMS.
    TransientModel = Les données ne sont pas conservées longtemps (nettoyées automatiquement)
    """
    _name = 'sms.mass.sending.wizard'
    _description = 'Assistant d\'envoi de SMS en masse'

    # Méthode pour obtenir la config par défaut
    @api.model
    def _get_default_config(self):
        return self.env['afruxia.config'].get_default_config()

    # Champs du wizard
    config_id = fields.Many2one(
        'afruxia.config',
        string='Configuration API',
        default=_get_default_config,
        required=True,
        help='Configuration Afruxia à utiliser pour l\'envoi'
    )

    # Deux options pour sélectionner les destinataires
    recipient_selection = fields.Selection([
        ('manual', 'Saisie manuelle'),
        ('partners', 'Depuis les contacts')
    ], string='Mode de sélection', default='manual', required=True)

    # Pour la saisie manuelle (numéros séparés par des virgules ou retours à la ligne)
    recipients_manual = fields.Text(
        string='Numéros de téléphone',
        help='Entrez les numéros séparés par des virgules ou des retours à la ligne.\n'
             'Format : +242XXXXXXXXX'
    )

    # Pour sélectionner depuis les contacts Odoo
    partner_ids = fields.Many2many(
        'res.partner',
        string='Contacts',
        domain=[('phone', '!=', False)],  # Seulement les contacts avec un téléphone
        help='Sélectionnez les contacts à qui envoyer le SMS'
    )

    # Le message à envoyer
    message = fields.Text(
        string='Message',
        required=True,
        help='Le message qui sera envoyé à tous les destinataires'
    )

    # Informations calculées
    character_count = fields.Integer(
        string='Nombre de caractères',
        compute='_compute_character_count'
    )

    sms_count = fields.Integer(
        string='SMS par destinataire',
        compute='_compute_sms_count'
    )

    recipient_count = fields.Integer(
        string='Nombre de destinataires',
        compute='_compute_recipient_count'
    )

    total_sms_count = fields.Integer(
        string='Total de SMS',
        compute='_compute_total_sms_count',
        help='Nombre total de SMS qui seront envoyés (destinataires × SMS par message)'
    )

    @api.depends('message')
    def _compute_character_count(self):
        for wizard in self:
            wizard.character_count = len(wizard.message) if wizard.message else 0

    @api.depends('message')
    def _compute_sms_count(self):
        for wizard in self:
            if not wizard.message:
                wizard.sms_count = 0
            else:
                length = len(wizard.message)
                if length <= 160:
                    wizard.sms_count = 1
                else:
                    wizard.sms_count = (length // 153) + (1 if length % 153 > 0 else 0)

    @api.depends('recipient_selection', 'recipients_manual', 'partner_ids')
    def _compute_recipient_count(self):
        for wizard in self:
            if wizard.recipient_selection == 'manual':
                if wizard.recipients_manual:
                    # Compte les numéros (séparés par virgule ou retour à la ligne)
                    numbers = wizard._parse_manual_recipients()
                    wizard.recipient_count = len(numbers)
                else:
                    wizard.recipient_count = 0
            else:
                wizard.recipient_count = len(wizard.partner_ids)

    @api.depends('recipient_count', 'sms_count')
    def _compute_total_sms_count(self):
        for wizard in self:
            wizard.total_sms_count = wizard.recipient_count * wizard.sms_count

    def _parse_manual_recipients(self):
        """
        Parse les numéros saisis manuellement.
        Retourne une liste de numéros nettoyés.
        """
        if not self.recipients_manual:
            return []

        # Remplace les retours à la ligne par des virgules
        text = self.recipients_manual.replace('\n', ',').replace('\r', ',')

        # Sépare par virgule et nettoie
        numbers = []
        for num in text.split(','):
            num = num.strip()
            if num:
                # Vérifie le format basique
                if not num.startswith('+'):
                    raise UserError(f'Numéro invalide : {num}\nLe numéro doit commencer par + (ex: +242XXXXXXXXX)')
                numbers.append(num)

        return numbers

    def _get_all_recipients(self):
        """
        Récupère tous les destinataires selon le mode sélectionné.
        Retourne une liste de tuples (numéro, nom_optionnel)
        """
        recipients = []

        if self.recipient_selection == 'manual':
            numbers = self._parse_manual_recipients()
            for num in numbers:
                recipients.append((num, num))  # (numéro, nom = numéro)

        else:  # partners
            for partner in self.partner_ids:
                if partner.phone:
                    recipients.append((partner.phone, partner.name))

        return recipients

    def action_send_sms(self):
        """
        Méthode appelée quand l'utilisateur clique sur "Envoyer".
        Envoie le SMS à tous les destinataires.
        """
        self.ensure_one()

        # Validation
        if not self.message:
            raise UserError('Le message est obligatoire.')

        # Récupère tous les destinataires
        recipients = self._get_all_recipients()

        if not recipients:
            raise UserError('Aucun destinataire sélectionné.')

        # Compteurs pour le résumé
        success_count = 0
        failed_count = 0
        failed_details = []

        # Crée et envoie un SMS pour chaque destinataire
        for phone, name in recipients:
            try:
                # Crée l'enregistrement SMS
                sms = self.env['afruxia.sms'].create({
                    'recipient': phone,
                    'message': self.message,
                    'config_id': self.config_id.id,
                })

                # Envoie le SMS
                sms.action_send_sms()

                # Vérifie si l'envoi a réussi
                if sms.state == 'sent':
                    success_count += 1
                    _logger.info(f'SMS envoyé avec succès à {name} ({phone})')
                else:
                    failed_count += 1
                    failed_details.append(f'{name} ({phone}): {sms.error_message or "Erreur inconnue"}')
                    _logger.warning(f'Échec d\'envoi à {name} ({phone}): {sms.error_message}')

            except Exception as e:
                failed_count += 1
                error_msg = str(e)
                failed_details.append(f'{name} ({phone}): {error_msg}')
                _logger.error(f'Erreur lors de l\'envoi à {name} ({phone}): {error_msg}')

        # Prépare le message de résumé
        summary = f'{success_count} SMS envoyé(s) avec succès'
        if failed_count > 0:
            summary += f', {failed_count} échec(s)'

        # Affiche le résumé
        if failed_count == 0:
            # Tout a réussi
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Envoi réussi',
                    'message': summary,
                    'type': 'success',
                    'sticky': False,
                }
            }
        elif success_count == 0:
            # Tout a échoué
            error_details = '\n'.join(failed_details[:5])  # Montre les 5 premières erreurs
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Échec complet',
                    'message': f'{summary}\n\nPremières erreurs:\n{error_details}',
                    'type': 'danger',
                    'sticky': True,
                }
            }
        else:
            # Succès partiel
            error_details = '\n'.join(failed_details[:3])
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Envoi partiel',
                    'message': f'{summary}\n\nErreurs:\n{error_details}',
                    'type': 'warning',
                    'sticky': True,
                }
            }

    def action_preview(self):
        """
        Affiche un aperçu des destinataires avant l'envoi.
        """
        self.ensure_one()

        recipients = self._get_all_recipients()

        if not recipients:
            raise UserError('Aucun destinataire sélectionné.')

        # Prépare la liste des destinataires
        recipient_list = '\n'.join([f'• {name}: {phone}' for phone, name in recipients[:10]])
        if len(recipients) > 10:
            recipient_list += f'\n... et {len(recipients) - 10} autres'

        message = f'Message : {self.message}\n\n'
        message += f'Destinataires ({len(recipients)}):\n{recipient_list}\n\n'
        message += f'Total de SMS à envoyer : {self.total_sms_count}'

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Aperçu de l\'envoi',
                'message': message,
                'type': 'info',
                'sticky': True,
            }
        }
