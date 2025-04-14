from odoo import models, fields, api

class Stage(models.Model):
    _inherit = "crm.stage"

    is_lead_stage = fields.Boolean("Lead Stage", default=False)

