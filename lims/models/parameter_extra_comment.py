# Copyright 2024 Xtendoo - Daniel Domínguez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _


class ParameterExtraComment(models.Model):
    _name = "parameter.extra.comment"
    _description = "Parameter Extra Comment"

    name = fields.Char(
        string="Name",
        required=True,
    )
    active = fields.Boolean(default=True, string="Active")