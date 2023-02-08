# Copyright 2021 - Manuel Calero <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_lab = fields.Boolean(
        string="Laboratory",
    )
    is_maker = fields.Boolean(
        string="Maker",
    )
    send_by_mail = fields.Boolean(
        string="Enviar por correo",
        default=True,
    )
