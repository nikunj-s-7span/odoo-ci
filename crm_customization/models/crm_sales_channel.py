from odoo import api, fields, models


class SalesChannel(models.Model):
    _name = "crm.sales.channel"
    _description = "Sales Channel"

    name = fields.Char("Channel Name", required=True)
