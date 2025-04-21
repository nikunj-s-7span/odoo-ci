from odoo import api, fields, models, _
from odoo.exceptions import UserError, AccessError


class ProjectTask(models.Model):
    """Inheriting project_task model to add sprint features"""

    _inherit = "project.task"

    sprint_id = fields.Many2one(
        "project.sprint",
        string="Sprint",
        help="Sprint",
        domain="[('project_id', '=', project_id)]",
    )
    available_user_ids = fields.Many2many(
        "res.users", compute="_compute_available_users", store=True
    )

    @api.depends("project_id", "project_id.user_id", "project_id.team_members_ids")
    def _compute_available_users(self):
        for task in self:
            if not task.project_id:
                task.available_user_ids = self.env.user
                continue
            task.available_user_ids = (
                task.project_id.team_members_ids + task.project_id.user_id
            )

    @api.onchange("project_id", "project_id.team_members_ids")
    def _onchange_project_id(self):
        if not self.project_id:
            self.available_user_ids = self.env.user
            return
        self.available_user_ids = self.project_id.team_members_ids

    @api.onchange('stage_id')
    def _onchange_stage_id(self):
        for task in self:
            if task.stage_id and task.stage_id.is_final_stage:
                task.state = '1_done'

    def unlink(self):
        for record in self:
            if not (
                record.env.user.has_group(
                    "project_management_sprint.group_project_manager_user"
                )
                or record.env.user.has_group("project.group_project_manager")
            ):
                raise AccessError(
                    "You don’t have permission to delete this task. Please contact to your Project Manager."
                )

        return super().unlink()
