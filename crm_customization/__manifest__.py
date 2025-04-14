# -*- coding: utf-8 -*-
{
    "name": "CRM Customization",
    "summary": "CRM Customization",
    "description": """CRM Customization""",
    "author": "7span",
    "website": "https://www.7span.com",
    "category": "Sales",
    "version": "18.0.1.0.4",
    "license": "LGPL-3",
    "depends": ["base", "crm", "hr", "mail", "project", "sale_management"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "security/security_groups.xml",
        "data/server_actions_data.xml",
        "data/stage_data.xml",
        "views/crm_lead_views.xml",
        "views/crm_lead_stage_views.xml",
        "views/crm_skill_views.xml",
        "views/crm_sales_channel_views.xml",
        "views/res_partner_views.xml",
        "wizard/crm_lead2opportunity_view.xml",
        "views/crm_looking_for_views.xml",
        "report/crm_priority_report_views.xml",
        "report/crm_google_ads_report.xml",
        "views/crm_menu_views.xml"
    ],
}
