# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LimsAnalysisParameterLimitResult(models.Model):
    _name = "lims.analysis.limit.result"
    _description = "parameter LIMS Limit Result"
    name = fields.Char(string="Name", store=True)
    parameter_ids = fields.Many2one(
        "lims.analysis.parameter",
        "Analysis lims parameter",
    )
    limit_result_line_ids = fields.One2many(
        "lims.analysis.limit.result.line",
        "limit_result_id",
    )
