# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"
    _order = "partner_id ASC"

    product_id = fields.Many2one(
        "product.product",
        "Product",
        domain=lambda self: self._domain_product_id(),
        required=False,
        check_company=True,
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        tracking=True,
        domain=[
            ('parent_id', '=', False),
            ('is_maker', '=', False),
            ('is_lab', '=', False)
        ]
    )

    # lot_image_ids = fields.One2many(
    #     "sample.image",
    #     "lot_id",
    #     string="Extra Sample Media",
    # )
