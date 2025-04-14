from odoo import api, fields, models


class ResPartner(models.Model):

    _inherit = "res.partner"

    linkedin_url = fields.Char(string="LinkedIn")
