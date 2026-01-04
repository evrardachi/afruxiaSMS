# -*- coding: utf-8 -*-
{
    'name': 'Afruxia SMS',
    'version': '19.0.1.0.1',
    'category': 'Tools',
    'summary': 'Envoi de SMS via l\'API Afruxia',
    'description': """
        Module d'envoi de SMS avec Afruxia
        ===================================
        Ce module permet d'envoyer des SMS en utilisant l'API Afruxia.

        Fonctionnalités :
        -----------------
        * Configuration des identifiants API Afruxia
        * Envoi de SMS individuels ou en masse
        * Historique des SMS envoyés
        * Gestion des erreurs d'envoi
    """,
    'author': 'Evrard ACHI',
    'website': 'https://www.afruxia.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],  # Dépendances : modules de base d'Odoo
    'data': [
        # Fichiers de sécurité (droits d'accès)
        'security/ir.model.access.csv',

        # Vues (interfaces utilisateur)
        'views/afruxia_config_views.xml',
        'views/afruxia_sms_views.xml',
        'views/sms_mass_sending_wizard_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/icon.png'],
    'installable': True,
    'application': True,  # Ce module apparaîtra comme une app dans Odoo
    'auto_install': False,
}
