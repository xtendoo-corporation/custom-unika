# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LimsAnalysisParameterTypeTags(models.Model):
    _name = "lims.analysis.parameter.type.tags"
    _description = "Type Parameter tags"

    name = fields.Char(required=True)
    description = fields.Text(string="Description")
    color = fields.Integer(string="Color Index")
    active = fields.Boolean(string="Active", default=True)
    internal = fields.Boolean(string="Internal", default=False)
    sequence = fields.Integer(
        default=lambda self: self.env["ir.sequence"].next_by_code("sale.order.tag")
        or 0,
        required=True,
    )

    _sql_constraints = [("name_uniq", "unique (name)", "Tag name already exists!")]
