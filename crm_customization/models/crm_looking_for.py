from odoo import api, fields, models


class CrmLookingFor(models.Model):
    _name = "crm.looking.for"
    _description = "Looking For"
    _rec_name = "looking_for"

    looking_for = fields.Selection(
        [
            (
                "Custom Software Development",
                "Custom Software Development (Web Apps, Mobile Apps, SaaS etc.)",
            ),
            (
                "E-commerce Solutions",
                "E-commerce Solutions (Shopify, WooCommerce, Webflow)",
            ),
            (
                "CMS & No-Code Platforms",
                "CMS & No-Code Platforms (Webflow, WordPress, Bubble etc.)",
            ),
            (
                "ERP & Enterprise Solutions",
                "ERP & Enterprise Solutions (Odoo, Custom ERP, Enterprise Portals)",
            ),
            (
                "Staff Augmentation",
                "Staff Augmentation (Dedicated Developers, Remote Teams)",
            ),
            (
                "Digital Marketing & Branding",
                "Digital Marketing & Branding (SEO, Social Media, Branding, Content)",
            ),
            (
                "UI/UX Design & Consulting",
                "UI/UX Design & Consulting (UI Design, UX Research)",
            ),
            ("Other", "Other"),
        ],
        required=True,
    )

    # User field (Many2one instead of Many2many)
    user_id = fields.Many2one("res.users", string="Salesperson", required=True)

    # Checkbox for India-specific assignment
    for_india = fields.Boolean(string="For India")

    # Constraint to ensure unique combinations
    _sql_constraints = [
        (
            "unique_looking_for_user",
            "UNIQUE(looking_for, user_id)",
            "This salesperson is already configured for this Looking For category!",
        )
    ]
