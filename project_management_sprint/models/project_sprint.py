from odoo import fields, models, api
from odoo.exceptions import AccessError, ValidationError


class ProjectSprint(models.Model):
    """Sprint in Project"""

    _name = "project.sprint"
    _inherit = "mail.thread"
    _description = "Project Sprint"

    name = fields.Char(string="Sprint Name", help="Name of the sprint")
    sprint_goal = fields.Text(string="Goal", help="Goal of the sprint")
    start_date = fields.Datetime(string="Start Date", help="Sprint start date")
    end_date = fields.Datetime(string="End Date", help="Sprint end date")
    project_id = fields.Many2one(
        "project.project", readonly=True, help="Respective Project"
    )
    state = fields.Selection(
        string="State",
        selection=[
            ("to_start", "To start"),
            ("ongoing", "Ongoing"),
            ("completed", "Completed"),
        ],
        default="to_start",
        help="State of the sprint",
    )

    @api.constrains("start_date", "end_date", "project_id")
    def _check_sprint_overlap(self):
        for record in self:
            # Ensure both dates are set before proceeding
            if not record.start_date or not record.end_date:
                return

            # Check that start_date is before end_date
            if record.start_date >= record.end_date:
                raise ValidationError("Start date must be before the end date.")

            # Find overlapping sprints for the same project
            overlapping_sprints = self.env["project.sprint"].search(
                [
                    ("project_id", "=", record.project_id.id),
                    ("id", "!=", record.id),
                    "|",
                    "&",
                    ("start_date", "<=", record.end_date),
                    ("end_date", ">=", record.start_date),
                    "&",
                    ("start_date", ">=", record.start_date),
                    ("start_date", "<=", record.end_date),
                ]
            )

            if overlapping_sprints:
                raise ValidationError(
                    "Sprint duration overlaps with an existing sprint for the same project."
                )

    def action_get_tasks(self):
        """Sprint added tasks"""
        return {
            "type": "ir.actions.act_window",
            "name": "Tasks",
            "view_mode": "kanban",
            "res_model": "project.task",
            "views": [[False, "kanban"], [False, "list"], [False, "form"]],
            "domain": [
                ("project_id", "=", self.project_id.id),
                ("sprint_id", "=", self.id),
            ],
            "context": "{'create': False}",
        }

    def action_get_backlogs(self):
        """Tasks without any sprint"""
        return {
            "type": "ir.actions.act_window",
            "name": "Backlogs",
            "view_mode": "kanban",
            "res_model": "project.task",
            "views": [[False, "kanban"], [False, "list"], [False, "form"]],
            "domain": [
                ("project_id", "=", self.project_id.id),
                ("sprint_id", "=", False),
            ],
            "context": "{'create': False}",
        }

    def action_get_all_tasks(self):
        """All tasks in the project"""
        return {
            "type": "ir.actions.act_window",
            "name": "All Tasks",
            "view_mode": "kanban",
            "res_model": "project.task",
            "views": [[False, "kanban"], [False, "list"], [False, "form"]],
            "domain": [("project_id", "=", self.project_id.id)],
            "context": "{'create': False}",
        }

    def action_start_sprint(self):
        """Sprint state to ongoing"""
        self.write({"state": "ongoing"})

    def action_finish_sprint(self):
        """Sprint state to completed"""
        self.write({"state": "completed"})

    def action_reset_states(self):
        """Sprint state to to_start"""
        self.write({"state": "to_start"})

    def _check_project_manager_access(self, action):
        messages = {
            "create": "You do not have permission to create a Project Sprint!",
            "write": "You do not have permission to modify a Project Sprint!",
            "unlink": "You do not have permission to delete a Project Sprint!",
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
