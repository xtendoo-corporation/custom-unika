# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"
    _order = "partner_id ASC"


    #Campos etiquetado
    take_for = fields.Char(string="Muestreo por")
    conditions = fields.Selection(
        [
            ("ambient", "Ambiente"),
            ("refrigered", "Refrigerado"),
        ],
        "Temperatura",
    )
    description = fields.Char(string="Descripción")
    place = fields.Char(string="Lugar de recogida")
    container = fields.Char(string="Envase/material")
    weight = fields.Float(string="Peso/volumen")
    udm = fields.Many2one("uom.uom", string="UdM")
    collection_date = fields.Datetime(string="Fecha de recogida")
    recepcion_date = fields.Datetime(string="Fecha de recepción")

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

    is_sample_number = fields.Boolean(default=False)

    def _get_default_lot_serial(self):
        print("self.env.context: ", self.env.context.get('is_product_sample'))
        is_sample = self.env.context.get('default_is_sample_number')
        if is_sample:
            return self.env['ir.sequence'].next_by_code('stock.lot.serial')
        else:
            return self.env['ir.sequence'].next_by_code('stock.lot.no.sample')

    name = fields.Char(
        'Lot/Serial Number', default=lambda self: self._get_default_lot_serial(),
        required=True, help="Unique Lot/Serial Number", index=True)



