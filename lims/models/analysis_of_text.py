# Copyright 2024 Xtendoo - Daniel Domínguez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _


class AnalysisOfText(models.Model):
    _name = "analysis.of.text"
    _description = "Analysis Of Text"

    name = fields.Char(
        string="Name",
        required=True,
    )
    active = fields.Boolean(default=True, string="Active")