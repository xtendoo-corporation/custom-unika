# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LimsAnalysisLimsAnalysisParameterMethodRel(models.Model):
    _name = "lims.analysis.lims.analysis.parameter.method.rel"
    _description = "Analysis parameter REL LIMS"

    name = fields.Char(String="parameter_id.name")

    analysis_id = fields.Many2one(
        'lims.analysis',
        string='Analysis',
        ondelete='cascade',
        required=True
    )
    parameter_method_ids = fields.Many2one(
        'analytical.method.price',
        string='Parameter',
        ondelete='cascade',
        required=True
    )
