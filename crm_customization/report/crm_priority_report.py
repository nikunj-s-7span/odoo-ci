from odoo import fields, models, tools

class PriorityReport(models.Model):
    """ CRM Lead Priority Report """

    _name = "crm.priority.report"
    _auto = False
    _description = "CRM Priority Analysis"
    _rec_name = 'id'

    date = fields.Datetime('Change Date', readonly=True)
    lead_create_date = fields.Datetime('Creation Date', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    team_id = fields.Many2one('crm.team', 'Sales Team', readonly=True)
    lead_id = fields.Many2one('crm.lead', "Opportunity/Lead", readonly=True)
    stage_id = fields.Many2one('crm.stage', 'Stage', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)
    lead_type = fields.Selection(
        string='Type',
        selection=[('lead', 'Lead'), ('opportunity', 'Opportunity')],
        help="Type is used to separate Leads and Opportunities",
        readonly=True)
    lead_active = fields.Char('Active/Lost', readonly=True)
    PRIORITY_SELECTION = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
        ('Very High', 'Very High'),
    ]

    old_priority = fields.Selection(
            PRIORITY_SELECTION,
            string="Old Priority",
            readonly = True
        )
    new_priority = fields.Selection(
            PRIORITY_SELECTION,
            string="To Priority",
            readonly = True
        )

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(f"""CREATE OR REPLACE VIEW crm_priority_report AS (
            SELECT
                lead.id AS id,
                lead.create_date AS lead_create_date,
                msg.date,
                lead.id as lead_id,
                lead.user_id,
                lead.team_id,
                lead.country_id,
                lead.company_id,
                lead.stage_id as stage_id,
                lead.partner_id,
                lead.type as lead_type,
                CASE 
                    WHEN lead.active = true THEN 'Active'
                    ELSE 'Lost'
                END as lead_active,
                track.old_value_char AS old_priority,
                track.new_value_char AS new_priority
            FROM crm_lead lead
            LEFT JOIN mail_message msg ON msg.res_id = lead.id AND msg.model = 'crm.lead'
            LEFT JOIN mail_tracking_value track ON track.mail_message_id = msg.id
            LEFT JOIN ir_model_fields fields ON track.field_id = fields.id
            WHERE fields.name = 'priority' AND track.old_value_char = 'Very High' AND lead.active in (true,false)
            ORDER BY msg.date DESC
            )
        """)
