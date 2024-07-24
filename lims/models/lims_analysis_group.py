# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class LimsAnalysisGroup(models.Model):
    _name = "lims.analysis.group"
    _description = "LIMS Analysis Group"
    name = fields.Char(string="Name", store=True)

    analysis_ids = fields.Many2many(
        "lims.analysis",
        "lims_analysis_group_lims_analysis_rel",
        "analysis_group_id",
        "analysis_id",
        string="Analysis",
    )
