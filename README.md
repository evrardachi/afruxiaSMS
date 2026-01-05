# 📱 Afruxia SMS - Module Odoo 19

<div align="center">

**Module professionnel d'envoi de SMS via l'API Afruxia pour Odoo 19**

![Version](https://img.shields.io/badge/version-19.0.1.0.3-blue)
![Licence](https://img.shields.io/badge/licence-LGPL--3-green)
![Odoo](https://img.shields.io/badge/Odoo-19.0-purple)

</div>

---

## 📋 Description

**Afruxia SMS** est un module complet pour Odoo 19 qui vous permet d'envoyer des SMS directement depuis votre ERP en utilisant l'API Afruxia. Conçu pour être simple et efficace, ce module offre une interface intuitive pour gérer vos communications SMS professionnelles.

### 🎯 Cas d'usage

- **Marketing** : Campagnes SMS ciblées vers vos clients
- **Notifications** : Alertes automatiques pour vos équipes
- **Confirmations** : Validation de commandes, rendez-vous, livraisons
- **Service client** : Communication rapide avec vos partenaires
- **Rappels** : Notifications de paiement, échéances, événements

## ✨ Fonctionnalités principales

### 📤 Envoi de SMS

- **Envoi individuel** : Envoyez un SMS à un seul destinataire avec une interface simple
- **Envoi en masse** : Envoyez le même message à plusieurs destinataires simultanément
  - 📝 Saisie manuelle de numéros (séparés par lignes ou virgules)
  - 👥 Sélection depuis vos contacts Odoo
  - 📊 Statistiques en temps réel (caractères, nombre de SMS, coût estimé)
  - 👁 Prévisualisation avant envoi
  - ⚠️ Alertes intelligentes pour les envois massifs

### ⚙️ Configuration et gestion

- 🔧 Configuration facile des identifiants API Afruxia
- 🧪 Test de connexion intégré
- 📋 Historique complet de tous les SMS envoyés
- 🔄 Possibilité de réessayer les envois échoués
- 📈 Compteur automatique de caractères et de SMS
- 🔍 Recherche et filtres avancés par date, statut, destinataire
- 📱 Interface responsive (compatible mobile et tablette)
- 💬 Chatter intégré pour suivre les modifications

## 🔧 Installation

### 1. Prérequis

- Odoo 19
- Python 3.10+
- Bibliothèque `requests` (généralement déjà installée avec Odoo)
- Compte Afruxia avec accès API

### 2. Installation du module

```bash
# Copiez le dossier afruxiaSMS dans votre répertoire addons
cp -r afruxiaSMS /chemin/vers/odoo/addons/

# Redémarrez Odoo
sudo systemctl restart odoo
# ou
./odoo-bin -u afruxiaSMS
```

### 3. Activation dans Odoo

1. Connectez-vous à Odoo
2. Activez le **mode développeur** : `Paramètres > Activer le mode développeur`
3. Allez dans `Applications`
4. Cliquez sur `Mettre à jour la liste des applications`
5. Recherchez "Afruxia SMS"
6. Cliquez sur `Installer`

## ⚙️ Configuration

### 1. Configurer l'API Afruxia

1. Allez dans `Afruxia SMS > Configuration > Configuration API`
2. Cliquez sur `Nouveau`
3. Remplissez les informations :
   - **Nom** : Un nom pour identifier cette configuration (ex: "Production")
   - **URL de l'API** : L'URL fournie par Afruxia (pré-remplie)
   - **Clé API** : Votre clé API Afruxia
   - **Secret API** : Votre secret API Afruxia
   - **Nom de l'expéditeur** : Le nom qui apparaîtra comme expéditeur (max 11 caractères)
4. Cochez `Configuration par défaut` si c'est votre configuration principale
5. Cliquez sur `Tester la connexion` pour vérifier que tout fonctionne
6. Cliquez sur `Enregistrer`

### 2. Envoyer votre premier SMS

#### 📧 Envoi individuel

1. Allez dans `Afruxia SMS > SMS > Envoyer un SMS`
2. Cliquez sur `Nouveau`
3. Remplissez :
   - **Destinataire** : Le numéro de téléphone (format international : +242XXXXXXXXX)
   - **Message** : Votre message (surveillez le compteur de caractères)
   - **Configuration** : Sélectionnez une configuration (ou laissez la valeur par défaut)
4. Cliquez sur `Envoyer`
5. Le système vous informera du succès ou de l'échec de l'envoi

#### 📬 Envoi en masse

1. Allez dans `Afruxia SMS > SMS > Envoi en masse`
2. Choisissez votre méthode de sélection des destinataires :
   - **Saisie manuelle** : Collez vos numéros (un par ligne ou séparés par virgules)
   - **Depuis les contacts** : Sélectionnez les contacts depuis votre base Odoo
3. Rédigez votre message
4. Consultez les statistiques en temps réel :
   - Nombre de caractères
   - Nombre de SMS par destinataire
   - Nombre total de destinataires
   - Coût total estimé (nombre total de SMS)
5. Cliquez sur `👁 Aperçu` pour vérifier avant l'envoi (optionnel)
6. Cliquez sur `📤 Envoyer`
7. Le système enverra les SMS et vous informera du résultat

## 📖 Utilisation avancée

### 🐍 Envoyer un SMS depuis le code Python

Vous pouvez intégrer l'envoi de SMS dans vos propres modules Odoo pour automatiser vos notifications.

#### Envoi simple depuis le code

```python
# Dans votre module personnalisé
def mon_action(self):
    # Envoie un SMS avec la configuration par défaut
    self.env['afruxia.sms'].send_sms(
        recipient='+242XXXXXXXXX',
        message='Votre commande a été validée !'
    )
```

#### Envoi avec configuration spécifique

```python
# Utiliser une configuration API spécifique
def envoyer_avec_config(self):
    config = self.env['afruxia.config'].search([('name', '=', 'Production')], limit=1)
    self.env['afruxia.sms'].create({
        'config_id': config.id,
        'recipient': '+242065123456',
        'message': 'Message important',
    }).action_send()
```

#### Exemple : Notification SMS lors d'une vente

```python
class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        # Appelle la méthode originale
        res = super(SaleOrder, self).action_confirm()

        # Envoie un SMS au client si son numéro existe
        if self.partner_id.phone:
            try:
                self.env['afruxia.sms'].send_sms(
                    recipient=self.partner_id.phone,
                    message=f'Bonjour {self.partner_id.name}, votre commande {self.name} a été confirmée ! Merci pour votre confiance.'
                )
            except Exception as e:
                # Log l'erreur sans bloquer la confirmation
                _logger.warning(f"Impossible d'envoyer le SMS : {e}")

        return res
```

#### Exemple : Envoi en masse depuis le code

```python
def envoyer_rappel_paiement(self):
    # Récupérer les factures impayées
    factures = self.env['account.move'].search([
        ('state', '=', 'posted'),
        ('payment_state', '=', 'not_paid'),
        ('invoice_date_due', '<', fields.Date.today())
    ])

    # Préparer les destinataires
    recipients = []
    for facture in factures:
        if facture.partner_id.phone:
            recipients.append(facture.partner_id.phone)

    # Créer et lancer l'assistant d'envoi en masse
    wizard = self.env['sms.mass.sending.wizard'].create({
        'recipient_selection': 'manual',
        'recipients_manual': '\n'.join(recipients),
        'message': 'Rappel : Vous avez une facture en attente de paiement. Merci de régulariser votre situation.'
    })
    wizard.action_send_sms()
```

## 🔍 Structure du module

```
afruxiaSMS/
├── __init__.py                              # Point d'entrée du module
├── __manifest__.py                          # Manifeste (métadonnées du module)
├── README.md                                # Documentation principale
│
├── models/                                  # 📊 Logique métier (Models)
│   ├── __init__.py
│   ├── afruxia_config.py                   # Configuration API Afruxia
│   └── afruxia_sms.py                      # Gestion des SMS individuels
│
├── wizard/                                  # 🧙 Assistants (Wizards)
│   ├── __init__.py
│   └── sms_mass_sending_wizard.py          # Assistant d'envoi en masse
│
├── views/                                   # 🖼️ Interfaces utilisateur (Views)
│   ├── afruxia_config_views.xml            # Vues de configuration
│   ├── afruxia_sms_views.xml               # Vues d'envoi individuel
│   ├── sms_mass_sending_wizard_views.xml   # Vue d'envoi en masse
│   └── menu_views.xml                      # Menus de navigation
│
├── security/                                # 🔐 Sécurité et droits d'accès
│   └── ir.model.access.csv                 # Permissions utilisateurs
│
├── static/                                  # 📁 Fichiers statiques
│   └── description/
│       ├── icon.png                        # Icône du module
│       └── index.html                      # Page de présentation
│
└── doc/                                     # 📚 Documentation supplémentaire
    ├── GUIDE_DEBUTANT.md                   # Guide pour débutants
    └── INSTALLATION.md                     # Instructions d'installation
```

### 📦 Dépendances

Ce module dépend de :
- **base** : Module de base Odoo (contacts, utilisateurs, etc.)
- **mail** : Module de messagerie Odoo (chatter, activités)

### 🔑 Modèles de données

#### `afruxia.config`
Configuration des identifiants API Afruxia
- `name` : Nom de la configuration
- `api_url` : URL de l'API Afruxia
- `api_key` : Client ID (X-Client-ID)
- `api_secret` : Client Secret (X-Client-Secret)
- `sender_name` : Nom de l'expéditeur
- `is_default` : Configuration par défaut

#### `afruxia.sms`
Historique et gestion des SMS
- `recipient` : Numéro du destinataire
- `message` : Contenu du message
- `status` : Statut (draft, sent, failed)
- `config_id` : Configuration utilisée
- `error_message` : Message d'erreur si échec
- `sent_date` : Date d'envoi

#### `sms.mass.sending.wizard` (TransientModel)
Assistant d'envoi en masse
- `recipient_selection` : Mode de sélection (manual/partners)
- `recipients_manual` : Numéros saisis manuellement
- `partner_ids` : Contacts sélectionnés
- `message` : Message à envoyer
- `character_count` : Nombre de caractères
- `sms_count` : Nombre de SMS par destinataire
- `recipient_count` : Nombre de destinataires
- `total_sms_count` : Total de SMS à envoyer

## 🔐 Sécurité et permissions

Le module respecte les droits d'accès standards d'Odoo :

| Groupe | Configurations API | Envoi de SMS | Historique SMS |
|--------|-------------------|--------------|----------------|
| **Utilisateurs** (`base.group_user`) | Lecture, Écriture, Création | ✅ Complet | ✅ Complet |
| **Administrateurs** (`base.group_system`) | ✅ Complet (+ Suppression) | ✅ Complet | ✅ Complet |

### 🔒 Bonnes pratiques de sécurité

- ⚠️ Ne partagez jamais vos identifiants API (`X-Client-ID` et `X-Client-Secret`)
- 🔑 Stockez vos identifiants de manière sécurisée
- 👥 Limitez l'accès à la configuration API aux administrateurs de confiance
- 📊 Surveillez régulièrement l'historique des SMS pour détecter des anomalies
- 🔄 Changez vos identifiants API périodiquement

## 🌐 API Afruxia

### Format de l'API

Le module utilise l'API Afruxia avec le format suivant :

**Endpoint** : `https://marketing.afruxia.com/api/v1/sms/send`

**Headers** :
```
X-Client-ID: votre_client_id
X-Client-Secret: votre_client_secret
Content-Type: application/json
```

**Payload** :
```json
{
  "recipients": ["+242065123456", "+242064789012"],
  "message": "Votre message SMS",
  "sender_name": "VotreNom"
}
```

**Réponse en cas de succès** :
```json
{
  "status": "success",
  "message": "SMS envoyés avec succès"
}
```

### ⚙️ Personnalisation de l'API

Si l'API Afruxia évolue, vous pouvez adapter la méthode `_call_afruxia_api()` dans le fichier `models/afruxia_sms.py` :

```python
def _call_afruxia_api(self):
    """Méthode d'appel à l'API - à personnaliser selon vos besoins"""
    # Adaptez selon la documentation Afruxia
```

## 🐛 Dépannage

### ❌ Le module n'apparaît pas dans la liste des applications

**Solutions :**
1. Vérifiez que le dossier `afruxiaSMS` est bien dans votre répertoire `addons`
2. Redémarrez le serveur Odoo
3. Activez le mode développeur : `Paramètres > Activer le mode développeur`
4. Allez dans `Applications > Mettre à jour la liste des applications`
5. Cherchez "Afruxia SMS"

### ❌ Erreur lors de l'envoi de SMS

**Solutions :**
1. Vérifiez vos identifiants API dans `Configuration > Configuration API`
2. Utilisez le bouton `Tester la connexion` pour valider la configuration
3. Consultez les logs Odoo :
   - En mode développeur : `Paramètres > Technique > Logs`
   - Ou dans le terminal si vous lancez Odoo manuellement
4. Vérifiez que votre compte Afruxia est actif et dispose de crédits SMS

### ❌ Le numéro de téléphone est rejeté

**Format attendu :**
- ✅ Bon : `+242065123456` (avec indicatif pays, sans espaces)
- ❌ Mauvais : `065 12 34 56` (sans indicatif, avec espaces)
- ❌ Mauvais : `+242 065 123 456` (avec espaces)
- ❌ Mauvais : `065123456` (sans indicatif pays)

### ❌ Le menu "Envoi en masse" n'apparaît pas

**Solutions :**
1. Assurez-vous que le module est bien à jour (version 19.0.1.0.3 ou supérieure)
2. Dans `Applications`, recherchez "Afruxia SMS" et cliquez sur `Mettre à jour`
3. Videz le cache de votre navigateur (Ctrl + Shift + R)
4. Vérifiez que vous avez les droits d'accès au menu

### ❌ Erreur "Vous n'êtes pas autorisé à accéder..."

**Solution :**
- Assurez-vous d'être connecté avec un utilisateur ayant les droits suffisants
- Groupe requis : `Internal User` (`base.group_user`)
- Pour la configuration API : groupe `Settings` (`base.group_system`)

### ❌ Les SMS en masse ne sont pas tous envoyés

**Vérifications :**
1. Consultez l'historique dans `SMS > Envoyer un SMS` pour voir les erreurs
2. Vérifiez que tous les numéros sont au bon format
3. Assurez-vous d'avoir suffisamment de crédits SMS
4. Consultez les logs pour identifier les numéros en erreur

## 💡 Conseils d'utilisation

### 📊 Optimiser vos envois

- **Messages courts** : Un SMS fait 160 caractères. Au-delà, il est découpé en plusieurs SMS (153 caractères par SMS supplémentaire)
- **Horaires** : Évitez les envois tardifs (après 20h) ou trop matinaux (avant 8h)
- **Contenu** : Soyez clair et concis. Incluez un appel à l'action si nécessaire
- **Test** : Avant un envoi en masse, testez toujours avec un envoi individuel

### 🎯 Cas d'usage recommandés

| Scénario | Type d'envoi | Exemple |
|----------|--------------|---------|
| Confirmation de commande | Individuel | "Commande #1234 confirmée. Livraison prévue le 10/01" |
| Rappel de rendez-vous | Individuel | "Rappel : RDV demain 14h avec Dr. Martin" |
| Promotion | Masse | "Soldes -30% jusqu'au 15/01 ! Code: PROMO30" |
| Relance de factures | Masse | "Facture impayée. Merci de régulariser." |
| Alerte urgente | Masse | "Fermeture exceptionnelle ce jour" |

## 📝 Changelog

### Version 19.0.1.0.3 (2026-01-05)
- ✨ Interface simplifiée pour l'envoi en masse
- 🎨 Ajout d'emojis pour meilleure UX
- 📊 Statistiques en temps réel améliorées
- ⚠️ Alertes intelligentes pour les gros envois

### Version 19.0.1.0.2 (2026-01-05)
- 🐛 Correction des permissions pour l'envoi en masse
- 📱 Changement du champ `mobile` vers `phone` pour compatibilité

### Version 19.0.1.0.1 (2026-01-04)
- ✨ Ajout de l'envoi en masse
- 👥 Sélection depuis les contacts Odoo
- 📝 Saisie manuelle de numéros

### Version 19.0.1.0.0 (2026-01-04)
- 🎉 Version initiale
- ⚙️ Configuration API Afruxia
- 📤 Envoi de SMS individuels
- 📋 Historique des envois
- 🧪 Test de connexion API

## 👨‍💻 Auteur

**Evrard ACHI**

Développeur Odoo spécialisé dans les solutions de communication

## 📄 Licence

**LGPL-3** - Vous êtes libre d'utiliser, modifier et distribuer ce module selon les termes de la licence LGPL-3.

## 🤝 Contribution

Les contributions sont les bienvenues ! Si vous souhaitez améliorer ce module :

1. 🍴 Forkez le projet
2. 🔨 Créez une branche pour votre fonctionnalité (`git checkout -b feature/amelioration`)
3. ✅ Commitez vos changements (`git commit -m 'Ajout d'une fonctionnalité'`)
4. 📤 Pushez vers la branche (`git push origin feature/amelioration`)
5. 🔀 Ouvrez une Pull Request

## 📞 Support et questions

### 🆘 Besoin d'aide ?

- 📖 Consultez le `GUIDE_DEBUTANT.md` pour un tutoriel pas à pas
- 📄 Lisez le `INSTALLATION.md` pour des instructions détaillées
- 🐛 Signalez les bugs via les issues GitHub
- 💬 Contactez votre administrateur système

### 🔗 Ressources utiles

- [Documentation officielle Odoo 19](https://www.odoo.com/documentation/19.0/)
- [Documentation API Afruxia](https://www.afruxia.com)
- [Guide du développeur Odoo](https://www.odoo.com/documentation/19.0/developer.html)

---

<div align="center">

**Merci d'utiliser Afruxia SMS !**

Si ce module vous est utile, n'hésitez pas à le partager ⭐

</div>
