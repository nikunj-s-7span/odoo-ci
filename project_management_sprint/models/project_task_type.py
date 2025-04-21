from odoo import api, fields, models, _


class ProjectTaskType(models.Model):
    _inherit = 'project.task.type'

    is_final_stage = fields.Boolean("Is Final Stage")