# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError

class LimsAnalysisNormative(models.Model):
    _name = "lims.analysis.normative"
    _description = "parameter LIMS normative"

    name = fields.Char(string="Name", store=True)
    parameter_ids = fields.Many2one(
        "lims.analysis.parameter",
        "Analysis lims parameter",
    )
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    parameter_uom = fields.Many2many(related="parameter_ids.parameter_uom")
    limit_result_line_ids = fields.One2many('lims.analysis.normative.result.line', 'parent_id', string='Limits Line')
    is_acreditation = fields.Boolean(string="Is Acreditation", store=True)
    active = fields.Boolean(default=True, string="Active")







