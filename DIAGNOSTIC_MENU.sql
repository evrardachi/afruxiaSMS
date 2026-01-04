-- Script de diagnostic pour vérifier si le menu existe dans la base de données

-- 1. Vérifier que l'action existe
SELECT id, name, res_model, view_mode, target
FROM ir_act_window
WHERE name LIKE '%masse%' OR res_model = 'sms.mass.sending.wizard';

-- 2. Vérifier que les menus existent
SELECT m.id, m.name, m.parent_id, m.action, m.sequence, p.name as parent_name
FROM ir_ui_menu m
LEFT JOIN ir_ui_menu p ON m.parent_id = p.id
WHERE m.name LIKE '%masse%' OR m.name LIKE '%SMS%';

-- 3. Vérifier les références dans ir_model_data
SELECT module, name, model, res_id
FROM ir_model_data
WHERE module = 'afruxiaSMS'
AND (name LIKE '%mass%' OR model = 'ir.ui.menu')
ORDER BY model, name;

-- 4. Vérifier le menu parent SMS
SELECT m.id, m.name, m.parent_id, m.sequence
FROM ir_ui_menu m
JOIN ir_model_data d ON d.res_id = m.id AND d.model = 'ir.ui.menu'
WHERE d.module = 'afruxiaSMS'
AND d.name = 'menu_afruxia_sms';

-- 5. Vérifier tous les sous-menus de SMS
SELECT m.id, m.name, m.action, m.sequence
FROM ir_ui_menu m
WHERE m.parent_id = (
    SELECT res_id FROM ir_model_data
    WHERE module = 'afruxiaSMS' AND name = 'menu_afruxia_sms'
)
ORDER BY m.sequence;
