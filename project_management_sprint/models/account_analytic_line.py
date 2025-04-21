from odoo import models, api, exceptions, _


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def unlink(self):
        user = self.env.user
        if user.has_group("project_management_sprint.group_project_manager_user"):
            for record in self:
                if record.employee_id.user_id != user:
                    raise exceptions.UserError(
                        _(
                            "You can only delete timesheets linked to your own employee record."
                        )
                    )
        return super().unlink()
