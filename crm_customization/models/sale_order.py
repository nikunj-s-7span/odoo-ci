from odoo import models, fields, api, _
from datetime import datetime, timedelta

class SaleOrder(models.Model):
    _inherit = "sale.order"

    approval_requested = fields.Boolean(string="Approval Requested", default=False)


    def action_confirm(self):
        allowed_user_email = "kaushal@7span.com"
        current_user = self.env.user

        margin_percent = self.margin / self.amount_total * 100 if self.amount_total else 0

        if margin_percent <= 50 and current_user.login != allowed_user_email:
            if not self.approval_requested:
                self.message_post(
                    body=_(
                        "Quotation confirmation is restricted. Only Kaushal Gajjar can confirm this quotation when margin is below 50%."),
                    subtype_xmlid="mail.mt_note"
                )

                user = self.env["res.users"].search([("login", "=", allowed_user_email)], limit=1)

                if user:
                    self.activity_schedule(
                        activity_type_id=self.env.ref("mail.mail_activity_data_todo").id,
                        summary=_("Quotation Needs Approval"),
                        note=_("Please review and confirm this quotation as the margin is below 50%."),
                        user_id=user.id,
                        date_deadline=datetime.today() + timedelta(weeks=2)
                    )
                self.approval_requested = True


            return False

        return super(SaleOrder, self).action_confirm()