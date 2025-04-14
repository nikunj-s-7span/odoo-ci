from odoo import api, fields, models


class CrmSkill(models.Model):
    _name = "crm.skill"
    _description = "Skills"

    name = fields.Char("Skill Name", required=True)
