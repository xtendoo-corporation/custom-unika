# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplateLimsAnalysisRel(models.Model):
    _name = "product.template.lims.analysis.rel"
    _description = "Analysis Group Product REL LIMS"
    product_id = fields.Many2one(
        "product.template", string="Product", ondelete="cascade", required=True
    )
    analysis_id = fields.Many2one(
        "lims.analysis", string="Analysis", ondelete="cascade", required=True
    )
