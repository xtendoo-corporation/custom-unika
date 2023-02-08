# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LineAnalysisGroupRel(models.Model):
    _name = "line.analysis.group.rel"

    analysis_group_id = fields.Many2one(
        "lims.analysis", string="Analysis Group", ondelete="cascade", required=True
    )
    sale_line_id = fields.Many2one(
        "sale.order.line", string="Line", ondelete="cascade", required=True
    )
