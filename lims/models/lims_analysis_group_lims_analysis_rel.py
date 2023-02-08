# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LimsAnalysisGroupLimsAnalysisRel(models.Model):
    _name = "lims_analysis_group_lims_analysis_rel"
    _description = "Analysis REL LIMS"
    analysis_group_id = fields.Many2one(
        "lims.analysis.group",
        string="Analysis Group",
        ondelete="cascade",
        required=True,
    )
    analysis_id = fields.Many2one(
        "lims.analysis", string="Analysis", ondelete="cascade", required=True
    )
