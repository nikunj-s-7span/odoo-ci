from odoo import models, fields, api, _
from datetime import datetime, timedelta

class SaleReportAnalysis(models.Model):
    _inherit = 'sale.report'

    margin_percent = fields.Float(
        'Margin Percent',
        group_operator="avg",
        digits=(16, 2)
    )
    def _select_additional_fields(self):
        res = super()._select_additional_fields()
        res['margin_percent'] = """
                    CASE 
                        WHEN SUM(l.price_subtotal) != 0 
                        THEN (SUM(l.margin) / NULLIF(SUM(l.price_subtotal), 0)) * 100 
                        ELSE 0 
                    END
                """
        return res