from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    def get_subordinate_users(self):
        """
        Returns all users who are subordinates of the current user
        based on the employee-manager hierarchy (recursive)
        """

        # Get all employee records where this user is manager (directly or indirectly)
        employee_model = self.env['hr.employee']
        employee = employee_model.search([('user_id', '=', self.id)], limit=1)
        if not employee:
            return self.env['res.users']

        # Get all subordinate employees (recursive)
        subordinate_employees = employee_model.search([
            ('id', 'child_of', employee.id)
        ])

        # Get corresponding users
        subordinate_users = subordinate_employees.mapped('user_id')
        return subordinate_users