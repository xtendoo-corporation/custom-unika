# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LineParameterMeThodRel(models.Model):
    _name = "line.parameter.method.rel"
    _description = "Analysis parameter line REL LIMS"
    parameter_id = fields.Many2one(
        "parameter.analytical.method.price.uom", string="Parameter", ondelete="cascade", required=True
    )
    sale_line_id = fields.Many2one(
        "sale.order.line", string="Line", ondelete="cascade", required=True
    )
