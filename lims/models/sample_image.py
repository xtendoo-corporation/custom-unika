# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductImage(models.Model):
    _name = "sample.image"
    _description = "Product Image"
    _inherit = ["image.mixin"]
    _order = "main DESC, sequence, id"

    name = fields.Char("Name", required=True)
    sequence = fields.Integer(default=10, index=True)

    image_1920 = fields.Image(required=True)

    analysis_id = fields.Many2one(
        "lims.analysis.line", "Analisis", index=True, ondelete="cascade"
    )

    main = fields.Boolean("Is main", default=False)
