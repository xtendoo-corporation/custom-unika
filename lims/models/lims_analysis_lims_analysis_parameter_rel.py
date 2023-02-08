# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LimsAnalysisLimsAnalysisParameterRel(models.Model):
    _name = "lims.analysis.lims.analysis.parameter.rel"
    _description = "Analysis parameter REL LIMS"
    parameter_id = fields.Many2one(
        "lims.analysis.parameter", string="Parameter", ondelete="cascade", required=True
    )
    analysis_id = fields.Many2one(
        "lims.analysis", string="Analysis", ondelete="cascade", required=True
    )
