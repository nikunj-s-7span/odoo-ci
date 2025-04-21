from odoo import fields, models, api
from odoo.exceptions import AccessError


class ProjectProject(models.Model):
    """Inheriting project_project model to add sprint features"""

    _inherit = "project.project"
    team_members_ids = fields.Many2many(
        "res.users",
        string="Team Members",
        domain="[('share','=',False),('active','=',True)]",
    )

    def action_get_sprint(self):
        """Getting sprint inside the project"""
        return {
            "type": "ir.actions.act_window",
            "name": "Sprints",
            "view_mode": "list,form",
            "res_model": "project.sprint",
            "context": {"default_project_id": self.id},
            "domain": [("project_id", "=", self.id)],
        }

    def _check_project_manager_access(self, action):
        messages = {
            "create": "You do not have permission to create a Project!",
            "write": "You do not have permission to modify a Project!",
            "unlink": "You do not have permission to delete a Project!",
        }
        if not self.env.user.has_group(
            "project.group_project_manager"
        ) or self.env.user.has_group(
            "project_management_sprint.group_project_manager_user"
        ):
            raise AccessError(
                messages.get(
                    action, "You do not have permission to perform this action."
                )
            )

    @api.model_create_multi
    def create(self, vals_list):
        self._check_project_manager_access("create")
        return super().create(vals_list)

    def write(self, vals):
        for record in self:
            if not record.env.user.has_group(
                "project_management_sprint.group_project_manager_user"
            ) and not record.env.user.has_group("project.group_project_manager"):
                raise AccessError("You do not have permission to modify projects.")
        return super().write(vals)

    def unlink(self):
        for record in self:
            record._check_project_manager_access("unlink")
        return super().unlink()

    def project_update_all_action(self):
        return {
            "type": "ir.actions.client",
            "tag": "action_spreadsheet_dashboard",
            "name": "Dashboards",
            "target": "current",
            "context": {
                "default_project_id": self.id,
            },
        }
