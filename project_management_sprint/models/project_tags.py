from odoo import fields, models, api
from odoo.exceptions import AccessError


class ProjectTags(models.Model):
    _inherit = "project.tags"

    def _check_project_manager_access(self, action):
        messages = {
            "create": "You do not have permission to create a Tags!",
            "write": "You do not have permission to modify a Tags!",
            "unlink": "You do not have permission to delete a Tags!",
        }
        if not (
            self.env.user.has_group(
                "project_management_sprint.group_project_manager_user"
            )
            or self.env.user.has_group("project.group_project_manager")
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
        self._check_project_manager_access("write")
        return super().write(vals)

    def unlink(self):
        for record in self:
            record._check_project_manager_access("unlink")
        return super().unlink()
