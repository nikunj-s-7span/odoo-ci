import json

from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.addons.crm.models import crm_stage
from odoo.exceptions import ValidationError

class Lead(models.Model):
    _inherit = "crm.lead"

    linkedin_url = fields.Char(string="LinkedIn URL")

    priority = fields.Selection(crm_stage.AVAILABLE_PRIORITIES, string='Priority', index=True, tracking=True,
        default=crm_stage.AVAILABLE_PRIORITIES[0][0])

    project_type = fields.Selection(
        [("dedicated", "Dedicated"), ("fixed", "Fixed"), ("hourly", "Hourly")],
        string="Project Type",
    )
    skill_ids = fields.Many2many(
        "crm.skill",
        string="Skills",
    )

    department_ids = fields.Many2many(
        "hr.department",
        string="Departments",
    )

    sales_channel_id = fields.Many2one(
        "crm.sales.channel",
        string="Sales Channel",
    )

    task_created = fields.Boolean(string="Task Created", default=False)
    stage_id = fields.Many2one(
        "crm.stage",
        string="Stage",
        group_expand="_read_group_stage_ids",
        tracking=True,
        index=True,
        copy=False,
        ondelete="restrict",
        domain=lambda self: self._stage_domain(),
    )

    looking_for = fields.Selection(
        [
            (
                "custom_software_development",
                "Custom Software Development (Web Apps, Mobile Apps, SaaS etc.)",
            ),
            (
                "ecommerce_solutions",
                "E-commerce Solutions (Shopify, WooCommerce, Webflow)",
            ),
            (
                "cms_and_no_code_platforms",
                "CMS & No-Code Platforms (Webflow, WordPress, Bubble etc.)",
            ),
            (
                "erp_and_enterprise_solutions",
                "ERP & Enterprise Solutions (Odoo, Custom ERP, Enterprise Portals)",
            ),
            (
                "staff_augmentation",
                "Staff Augmentation (Dedicated Developers, Remote Teams)",
            ),
            (
                "digital_marketing_and_branding",
                "Digital Marketing & Branding (SEO, Social Media, Branding, Content)",
            ),
            (
                "ui_ux_design_and_consulting",
                "UI/UX Design & Consulting (UI Design, UX Research)",
            ),
            ("other", "Other"),
        ],
        string="Looking For",
    )

    budget = fields.Selection(
        [
            ("<2000", "Less than $2000"),
            ("2000-5000", "$2000 - $5000"),
            ("5000-10000", "$5000 - $10000"),
            ("10000-20000", "$10000 - $20000"),
            ("20000-50000", "$20000 - $50000"),
            (">50000", "$50000+"),
        ],
        string="Budget",
    )

    project_timeline = fields.Selection(
        [
            ("immediately", "Immediately"),
            ("within_a_month", "Within a Month"),
            ("two_to_three_months", "2-3 Months"),
            ("three_to_six_months", "3-6 Months"),
            ("not_sure", "Not Sure"),
        ],
        string="Project Timeline",
    )

    tracking_data = fields.Json(string="Tracking Data Json")
    tracking_data_dict = fields.Text(string="Tracking Data")
    for_india = fields.Boolean(string="For India", default=False)
    stage_name = fields.Char(string="Stage Name", compute="_compute_stage_name", store=True)

    @api.depends('stage_id')
    def _compute_stage_name(self):
        for record in self:
            record.stage_name = record.stage_id.name if record.stage_id else ''
            
    def _stage_find(self, team_id=False, domain=None, order='sequence, id', limit=1):
        """ Override to consider the is_lead_stage flag when finding appropriate stages """
        if domain is None:
            domain = []

        # Add is_lead_stage to domain based on record type or context
        lead_type = self.type if self else self.env.context.get('default_type')

        # When converting from lead to opportunity, we need to force is_lead_stage=False
        converting_to_opportunity = self.env.context.get('default_type') == 'opportunity' and getattr(self, 'type',
                                                                                                      False) == 'lead'

        if converting_to_opportunity or lead_type == 'opportunity':
            domain.append(('is_lead_stage', '=', False))
        elif lead_type == 'lead':
            domain.append(('is_lead_stage', '=', True))

        return super(Lead, self)._stage_find(team_id=team_id, domain=domain, order=order, limit=limit)

    def _convert_opportunity_data(self, customer, team_id=False):
        """ Override to ensure correct stage is set when converting from lead to opportunity """
        # Call the original method first to get base values
        vals = super(Lead, self)._convert_opportunity_data(customer, team_id)

        if self.type == 'lead':
            first_opportunity_stage = self.env["crm.stage"].search(
                [("is_lead_stage", "=", False)],
                order="sequence",
                limit=1
            )

            if first_opportunity_stage:
                vals['stage_id'] = first_opportunity_stage.id

        return vals

    def write(self, vals):
        qualified_stage = self.env["crm.stage"].search(
            [("name", "=", "Qualified")], limit=1
        )
        pre_sales_stage = self.env["crm.stage"].search(
            [("name", "=", "Pre-Sales")], limit=1
        )
        proposed_stage = self.env["crm.stage"].search(
            [("name", "=", "Proposed")], limit=1
        )

        won_stage = self.env['crm.stage'].search([('is_won', '=', True)], limit=1)

        if won_stage and vals.get("stage_id") == won_stage.id:
            for lead in self:
                sale_orders = self.env["sale.order"].search([("opportunity_id", "=", lead.id)])

                unconfirmed_orders = sale_orders.filtered(lambda order: order.state != "sale")

                if unconfirmed_orders:
                    unconfirmed_names = ", ".join(unconfirmed_orders.mapped("name"))
                    raise ValidationError(_(
                        "You cannot move to the Won stage because the following sale orders are not confirmed:\n%s"
                        % unconfirmed_names
                    ))

        if "user_id" in vals:
            # If user is explicitly setting a salesperson, respect that
            return super(Lead, self).write(vals)

        if "looking_for" in vals and not self.user_id:
            is_admin = self.env.user.has_group("sales_team.group_sale_manager")
            if is_admin:
                selected_country = self.country_id
                next_salesperson = self.sudo()._get_next_salesperson_for_looking_for(
                    vals["looking_for"],
                    selected_country.code if selected_country else None,
                )
                if next_salesperson:
                    vals["user_id"] = next_salesperson.id
                    if next_salesperson.sale_team_id:
                        vals["team_id"] = next_salesperson.sale_team_id.id

        for record in self:
            if "stage_id" in vals:
                new_stage = vals["stage_id"]

                if (
                    record.stage_id.id == qualified_stage.id
                    and new_stage == pre_sales_stage.id
                ):
                    self.activity_schedule(
                        activity_type_id=self.env.ref(
                            "mail.mail_activity_data_todo"
                        ).id,
                        summary=_("Please create margin calc/quotation."),
                        user_id=self.user_id.id,
                        date_deadline=datetime.today() + timedelta(days=1),
                    )

                if (
                    record.stage_id.id == pre_sales_stage.id
                    and new_stage == proposed_stage.id
                ):
                    quotation_count = self.env["sale.order"].search_count(
                        [("opportunity_id", "=", record.id)]
                    )

                    if quotation_count == 0:
                        raise UserError(
                            _(
                                "You must create a quotation before moving to the Proposed stage."
                            )
                        )

        if "project_type" in vals:
            quotations = self.env["sale.order"].search(
                [("opportunity_id", "=", self.id)]
            )
            if quotations:
                quotations.write({"project_type": vals["project_type"]})

        return super(Lead, self).write(vals)

    def get_team_members(self, args):
        user = self.env.user
        search_user_id = self._context.get("search_user_id")
        if search_user_id:
            user = self.env["res.users"].browse(search_user_id)

        subordinate_users = user.get_subordinate_users()

        users = self.env["res.users"].search([])
        for res_user in users:
            if res_user.id == user.id and (
                res_user.has_group("sales_team.group_sale_manager")
                or res_user.has_group("sales_team.group_sale_salesman_all_leads")
            ):
                return args

        return [("user_id", "in", [user.id] + subordinate_users.ids)] + args

    @api.model
    def search(self, args, offset=0, limit=None, order=None):
        public_user = self.env.user.has_group("base.group_public")
        if public_user or self.env.user.login == "__system__":
            return super().search(args, offset=offset, limit=limit, order=order)
        args = self.get_team_members(args)
        return super(Lead, self).search(args, offset=offset, limit=limit, order=order)

    def _search(self, args, offset=0, limit=None, order=None):
        public_user = self.env.user.has_group("base.group_public")
        if public_user or self.env.user.login == "__system__":
            return super(Lead, self)._search(
                args, offset=offset, limit=limit, order=order
            )
        args = self.get_team_members(args)
        return super(Lead, self)._search(args, offset=offset, limit=limit, order=order)

    @api.model
    def default_get(self, fields):
        """
        Override default_get to set default stage for new leads.
        """
        values = super(Lead, self).default_get(fields)
        if self.env.context.get("default_type") == "lead":  # Check if it's a lead
            open_stage = self.env.ref(
                "crm_customization.stage_lead_open", raise_if_not_found=False
            )
            if open_stage:
                values["stage_id"] = open_stage.id
        return values

    @api.model
    def _read_group_stage_ids(self, stages, domain):
        """
        Overrides the group expansion logic for the 'stage_id' field.
        - Fetches and returns stages based on the context ('default_type'):
            - If 'default_type' is 'lead', returns only lead stages.
            - Otherwise, returns opportunity stages.
        """

        # customization start
        context = self.env.context
        # lead stages based on condition
        lead_stages = self.env["crm.stage"].search([("is_lead_stage", "=", True)])
        # opportunity stages based on condition
        opportunity_stages = self.env["crm.stage"].search(
            [("is_lead_stage", "=", False)]
        )

        # Check if default_type is not 'lead', return opportunity stages if so
        if context.get("default_type") != "lead":
            return opportunity_stages

        # If default_type is 'lead', return lead stages
        return lead_stages
        # customization end

    @api.model
    def _stage_domain(self):
        """Method will check the default_type of stage.
        If default_type == lead, return it as lead stage,
        otherwise opportunity stage.
        """
        if self.env.context.get("default_type") == "lead":
            return [("is_lead_stage", "=", True)]
        return [("is_lead_stage", "=", False)]

    @api.model
    def update_lead_stage(self):
        """
        This method updates the stage of all leads to the specific stage 'Open Lead'.
        """
        open_stage = self.env.ref(
            "crm_customization.stage_lead_open", raise_if_not_found=False
        )

        if not open_stage:
            raise ValueError("The 'Open Lead' stage was not found.")
        leads = self.env["crm.lead"].search(
            [("type", "=", "lead"), ("stage_id", "!=", open_stage.id)]
        )
        leads.write({"stage_id": open_stage.id})

    def action_create_task(self):
        """
        Action method to create a task and its subtasks for each record in the model.
        - Searches for a specific project named 'Odoo Pre-Sales'.
        - Creates a main task linked to the project and associates subtasks with it.
        """
        for record in self:
            if record.task_created:
                raise UserError(
                    f"A task for this opportunity '{record.name}' has already been created."
                )

            project = self.env["project.project"].search(
                [("name", "=", "Odoo Pre-Sales")], limit=1
            )
            if not project:
                raise UserError(
                    "Project 'Odoo Pre-Sales' not found. Please create the project first."
                )

            task = self.env["project.task"].create(
                {
                    "display_name": record.name,
                    "project_id": project.id,
                    "partner_id": record.partner_id.id,
                    "user_ids": False,
                }
            )

            sub_task_names = [
                "Requirement Mapping and Gathering",
                "Analysis & R&D",
                "Demo Configuration",
                "Client Call",
                "Proposal",
                "Estimation",
                "Suggestion PPT",
                "Internal Discussion",
                "Dry Run",
                "MOM",
            ]

            for sub_task_name in sub_task_names:
                self.env["project.task"].create(
                    {"name": sub_task_name, "parent_id": task.id, "user_ids": False}
                )

            # Mark the task as created
            record.task_created = True

            record.message_post(body="Task and subtasks created.")

        return True

    def action_new_quotation(self):
        action = super(Lead, self).action_new_quotation()
        if action.get("context"):
            action["context"].update(
                {
                    "default_project_type": self.project_type,
                }
            )
        return action

    def _get_next_salesperson_for_looking_for(
        self,
        looking_for,
        selected_country=None,
        current_salesperson=None,
        existing_lead_create_date=None,
    ):
        # Map selection to crm.looking.for selection
        looking_for_mapping = {
            "custom_software_development": "Custom Software Development",
            "ecommerce_solutions": "E-commerce Solutions",
            "cms_and_no_code_platforms": "CMS & No-Code Platforms",
            "erp_and_enterprise_solutions": "ERP & Enterprise Solutions",
            "staff_augmentation": "Staff Augmentation",
            "digital_marketing_and_branding": "Digital Marketing & Branding",
            "ui_ux_design_and_consulting": "UI/UX Design & Consulting",
            "other": "Other",
        }

        # Get the corresponding looking_for value
        mapped_looking_for = looking_for_mapping.get(looking_for, looking_for)

        # Find matching records in crm.looking.for
        domain = [("looking_for", "=", mapped_looking_for)]

        if looking_for == "custom_software_development":
            is_india = (
                self.country_id.code == "IN" or selected_country == "IN"
                if self.country_id or selected_country
                else False
            )
            domain.append(("for_india", "=", is_india))

        looking_for_records = self.env["crm.looking.for"].sudo().search(domain)

        if not looking_for_records:
            return None

        salespersons = looking_for_records.sudo().mapped("user_id")

        if not salespersons:
            return None

        if looking_for == "custom_software_development":
            last_lead = self.env["crm.lead"].search(
                [
                    ("looking_for", "=", looking_for),
                    ("for_india", "=", self.for_india),
                    ("id", "!=", self.id),
                    ("type", "=", "lead"),
                ],
                order="create_date desc",
                limit=1,
            )
        else:
            last_lead = self.env["crm.lead"].search(
                [
                    ("looking_for", "=", looking_for),
                    ("id", "!=", self.id),
                    ("type", "=", "lead"),
                ],
                order="create_date desc",
                limit=1,
            )

        # If no existing lead or no last lead, start round-robin from the first salesperson
        if not last_lead:
            return salespersons[0]

        # If existing lead's create date is provided, check if it's less than the last lead
        if existing_lead_create_date and last_lead:
            if existing_lead_create_date < last_lead.create_date:
                # If the existing lead is older, return the current salesperson
                return current_salesperson

        # Find the last lead's assigned salesperson
        last_assigned_salesperson = last_lead.user_id

        # If last assigned salesperson is not in current salespersons list, use first salesperson
        if last_assigned_salesperson not in salespersons:
            return salespersons[0]

        # Get the index of the last assigned salesperson
        current_index = salespersons.ids.index(last_assigned_salesperson.id)

        # Calculate the next index for round-robin
        next_index = (current_index + 1) % len(salespersons)

        return salespersons[next_index]

    @api.model_create_multi
    def create(self, vals_list):
        modified_vals_list = []

        for vals in vals_list:
            is_admin = self.env.user.has_group("sales_team.group_sale_manager")
            selected_country = self.env["res.country"].search(
                [("id", "=", vals.get("country_id"))], limit=1
            )

            if is_admin:
                if vals.get("looking_for"):
                    temp_record = self.new(vals)
                    self_sudo = self.sudo()
                    next_salesperson = self_sudo._get_next_salesperson_for_looking_for(
                        temp_record.looking_for, selected_country.code
                    )
                    if next_salesperson:
                        vals["user_id"] = next_salesperson.id

                        if next_salesperson.sale_team_id:
                            vals["team_id"] = next_salesperson.sale_team_id.id

            modified_vals_list.append(vals)

        # Create the leads using the modified values
        leads = super(Lead, self).create(modified_vals_list)

        for record in leads:
            is_admin = self.env.user.has_group("sales_team.group_sale_manager")
            if is_admin and record.user_id and record.looking_for:
                activities = {
                    'call': {
                        'type': self.env.ref('mail.mail_activity_data_call'),
                        'summary': 'Call the client'
                    },
                    'email': {
                        'type': self.env.ref('mail.mail_activity_data_email'),
                        'summary': 'Contact on email'
                    },
                    'whatsapp': {
                        'type': self.env.ref('mail.mail_activity_data_todo'),
                        'summary': 'Send a message on WhatsApp'
                    }
                }

                for activity_name, activity_info in activities.items():
                    activity_type = activity_info['type']
                    days = activity_type.delay_count

                    today = fields.Date.today()
                    deadline = today + relativedelta(days=days)
                    self.env['mail.activity'].create({
                        'activity_type_id': activity_type.id,
                        'summary': activity_info['summary'],
                        'note': f"Follow up with the customer regarding their inquiry.",
                        'user_id': record.user_id.id,
                        'res_id': record.id,
                        'res_model_id': self.env['ir.model'].search([('model', '=', self._name)], limit=1).id,
                        'date_deadline': deadline,

                    })

        # Update tracking_data_dict for each lead
        for lead in leads:
            if not lead.tracking_data:
                continue
            formatted_data = str(json.dumps(lead.tracking_data))
            lead.update({"tracking_data_dict": formatted_data})
        return leads

    @api.onchange("looking_for", "country_id")
    def onchange_looking_for(self):
        is_admin = self.env.user.has_group("sales_team.group_sale_manager")

        if is_admin:
            # Retrieve the existing lead's create date
            lead_data = self.env["crm.lead"].search(
                [("id", "=", self._origin.id)], limit=1
            )

            next_salesperson = self._get_next_salesperson_for_looking_for(
                self.looking_for,
                current_salesperson=self.user_id,
                existing_lead_create_date=lead_data.create_date if lead_data else None,
            )

            if next_salesperson:
                if self.looking_for == lead_data.looking_for:
                    self.user_id = lead_data.user_id
                else:
                    self.user_id = next_salesperson
