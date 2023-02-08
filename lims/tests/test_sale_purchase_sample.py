# Copyright 2022 - Daniel Domínguez <https://xtendoo.es>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestSalePurchase(TransactionCase):
    def _create_order(self):
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
            }
        )

    def _create_line(self, order, product_id):
        self.env["sale.order.line"].create(
            {
                "name": product_id.name,
                "product_id": product_id.id,
                "product_uom_qty": 1,
                "product_uom": product_id.uom_id.id,
                "price_unit": 1000.00,
                "order_id": order.id,
            }
        )

    def _delete_line(self, order, product_id):
        self.env["sale.order.line"].search(
            [("order_id", "=", order.id), ("name", "=", product_id.name)]
        ).unlink()

    def _get_purchase_order_by_origin(self, origin):
        return self.env["purchase.order"].search([("origin", "=", origin)])

    def _get_purchase_order_in_origin(self, origin):
        return self.env["purchase.order"].search([("origin", "in", origin)])

    def _get_mail_activity(self, purchase_order):
        return self.env["mail.activity"].search(
            [
                ("res_model_id", "=", self.env["ir.model"]._get("purchase.order").id),
                ("res_id", "=", purchase_order.id),
            ]
        )

    def setUp(self):
        super(TestSalePurchase, self).setUp()
        self.product_sample = self.env["product.product"].create(
            {
                "name": "Sample Product",
                "is_product_sample": True,
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )
        self.product_sample_2 = self.env["product.product"].create(
            {
                "name": "Sample Product 2",
                "is_product_sample": True,
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )
        self.partner = self.env["res.partner"].create(
            {
                "name": "Test",
            }
        )
        self.supplier = self.env["res.partner"].create(
            {
                "name": "Supplier Test",
            }
        )
        self.product_no_sample = self.env["product.product"].create(
            {
                "name": "Not Sample Product",
                "is_product_sample": False,
                "type": "product",
                "categ_id": self.env.ref("product.product_category_all").id,
            }
        )

        self.product_service_autopurchase = self.env["product.product"].create(
            {
                "name": "Service Product Autopurchase",
                "is_product_sample": False,
                "type": "service",
                "categ_id": self.env.ref("product.product_category_all").id,
                "service_to_purchase": True,
                "seller_ids": [
                    (
                        0,
                        0,
                        {
                            "name": self.supplier.id,
                            "price": 0.0,
                            "delay": 1,
                            "min_qty": 1,
                        },
                    )
                ],
            }
        )

    ## Crear venta sin muestra -> no crea compra
    def test_create_sale_not_sample(self):
        order = self._create_order()
        self._create_line(order, self.product_no_sample)
        order.action_confirm()
        purchase_order = self._get_purchase_order_by_origin(order.name)
        self.assertEqual(len(purchase_order), 0)

    ##Crear venta con muestra -> Crea una compra
    def test_create_sale_sample(self):
        order = self._create_order()
        self._create_line(order, self.product_sample)
        order.action_confirm()
        purchase_order = self._get_purchase_order_by_origin(order.name)

        self.assertEqual(len(purchase_order), 1)

        self.assertEqual(purchase_order.partner_id.id, order.partner_id.id)

        self.assertEqual(
            purchase_order.order_line[0].product_id, order.order_line[0].product_id
        )

    ## Creamos venta con servivio autocomprable -> Crea una compra ( para verificar que la abse de odoo sigue funcionando bien)
    def test_create_sale_service_to_purchase(self):
        order = self._create_order()
        self._create_line(order, self.product_service_autopurchase)
        order.action_confirm()
        purchase_order = self._get_purchase_order_by_origin(order.name)

        self.assertEqual(len(purchase_order), 1)

        self.assertEqual(purchase_order.partner_id.id, self.supplier.id)

        self.assertEqual(
            purchase_order.order_line[0].product_id, order.order_line[0].product_id
        )

    ##Creamos una venta con muestra y otro sin muestra -> Crea una compra con la muestra
    def test_create_sale_not_sample_and_sample(self):
        order = self._create_order()
        self._create_line(order, self.product_no_sample)
        self._create_line(order, self.product_sample)
        order.action_confirm()
        purchase_order = self._get_purchase_order_by_origin(order.name)

        self.assertEqual(len(purchase_order), 1)

        self.assertEqual(len(purchase_order.order_line), 1)

        self.assertEqual(purchase_order.partner_id.id, order.partner_id.id)

        self.assertEqual(
            purchase_order.order_line[0].product_id, order.order_line[1].product_id
        )

    ##Creamos servicio autopurchase y muestra
    def test_create_sale_service_autopurchase_and_sample(self):
        order = self._create_order()
        self._create_line(order, self.product_service_autopurchase)
        self._create_line(order, self.product_sample)
        order.action_confirm()
        purchase_order = self._get_purchase_order_by_origin(order.name)

        self.assertEqual(len(purchase_order), 2)

        self.assertEqual(len(purchase_order[0].order_line), 1)

        self.assertEqual(len(purchase_order[1].order_line), 1)

        self.assertEqual(purchase_order[1].partner_id.id, self.supplier.id)

        self.assertEqual(purchase_order[0].partner_id.id, order.partner_id.id)

        self.assertEqual(
            purchase_order[1].order_line[0].product_id, order.order_line[0].product_id
        )

        self.assertEqual(
            purchase_order[0].order_line[0].product_id, order.order_line[1].product_id
        )

    ##Creamos venta con servicio autopurchase, producto y muestra
    def test_create_sale_service_autopurchase_and_sample_and_not_sample(self):
        order = self._create_order()
        self._create_line(order, self.product_service_autopurchase)
        self._create_line(order, self.product_sample)
        self._create_line(order, self.product_no_sample)
        order.action_confirm()
        purchase_order = self._get_purchase_order_by_origin(order.name)

        self.assertEqual(len(purchase_order), 2)

        self.assertEqual(len(purchase_order[0].order_line), 1)
        self.assertEqual(len(purchase_order[1].order_line), 1)

        self.assertEqual(purchase_order[1].partner_id.id, self.supplier.id)

        self.assertEqual(purchase_order[0].partner_id.id, order.partner_id.id)

        self.assertEqual(
            purchase_order[1].order_line[0].product_id, order.order_line[0].product_id
        )

        self.assertEqual(
            purchase_order[0].order_line[0].product_id, order.order_line[1].product_id
        )

    ##Creamos venta con 2 muestra y confirmamos
    # Falla
    def test_create_2_sale_sample_and_confirm(self):
        order = self._create_order()
        self._create_line(order, self.product_sample)
        order.action_confirm()

        order_2 = self._create_order()
        self._create_line(order_2, self.product_sample)
        order_2.action_confirm()

        order.name + "," + order_2.name

        purchase_order = self._get_purchase_order_in_origin((order.name, order_2.name))

        self.assertEqual(len(purchase_order), 2)

        self.assertEqual(len(purchase_order[0].order_line), 1)
        self.assertEqual(len(purchase_order[1].order_line), 1)

        self.assertEqual(purchase_order[0].partner_id.id, order.partner_id.id)
        self.assertEqual(purchase_order[1].partner_id.id, order.partner_id.id)

        self.assertEqual(
            purchase_order[0].order_line[0].product_id, order.order_line[0].product_id
        )
        self.assertEqual(
            purchase_order[1].order_line[0].product_id, order_2.order_line[0].product_id
        )

    def test_create_2_sale_sample_and_2_confirm(self):
        order = self._create_order()
        self._create_line(order, self.product_sample)
        order.action_confirm()
        purchase_order = self._get_purchase_order_by_origin(order.name)
        purchase_order.button_confirm()

        order_2 = self._create_order()
        self._create_line(order_2, self.product_sample)
        order_2.action_confirm()

        purchase_order_2 = self._get_purchase_order_by_origin(order_2.name)
        purchase_order_2.button_confirm()

        purchase_orders = self._get_purchase_order_in_origin([order.name, order_2.name])

        self.assertEqual(len(purchase_orders), 2)

        self.assertEqual(len(purchase_orders[0].order_line), 1)
        self.assertEqual(len(purchase_orders[1].order_line), 1)

        self.assertEqual(purchase_orders[0].partner_id.id, order.partner_id.id)
        self.assertEqual(purchase_orders[1].partner_id.id, order.partner_id.id)

        self.assertEqual(
            purchase_orders[0].order_line[0].product_id, order.order_line[0].product_id
        )
        self.assertEqual(
            purchase_orders[1].order_line[0].product_id,
            order_2.order_line[0].product_id,
        )

    def test_create_sale_sample_sale_product_and_sale_service_sale_product_and_2_confirm(
        self,
    ):
        order = self._create_order()
        self._create_line(order, self.product_sample)
        self._create_line(order, self.product_no_sample)
        order.action_confirm()

        purchase_order = self._get_purchase_order_by_origin(order.name)
        purchase_order.button_confirm()

        order_2 = self._create_order()
        self._create_line(order_2, self.product_service_autopurchase)
        self._create_line(order_2, self.product_no_sample)
        order_2.action_confirm()

        purchase_order_2 = self._get_purchase_order_by_origin(order_2.name)
        purchase_order_2.button_confirm()

        purchase_orders = self._get_purchase_order_in_origin([order.name, order_2.name])

        self.assertEqual(len(purchase_orders), 2)

        self.assertEqual(len(purchase_orders[0].order_line), 1)
        self.assertEqual(len(purchase_orders[1].order_line), 1)

        self.assertEqual(purchase_orders[0].partner_id.id, self.supplier.id)

        self.assertEqual(purchase_orders[1].partner_id.id, order.partner_id.id)

        self.assertEqual(
            purchase_orders[1].order_line[0].product_id, order.order_line[0].product_id
        )

        self.assertEqual(
            purchase_orders[0].order_line[0].product_id,
            order_2.order_line[0].product_id,
        )

    def test_create_sale_2_samples(self):
        order = self._create_order()
        self._create_line(order, self.product_sample)
        self._create_line(order, self.product_sample_2)
        order.action_confirm()
        purchase_order = self._get_purchase_order_by_origin(order.name)

        self.assertEqual(len(purchase_order), 1)

        self.assertEqual(len(purchase_order.order_line), 2)

        self.assertEqual(purchase_order.partner_id.id, order.partner_id.id)

        self.assertEqual(
            purchase_order.order_line[0].product_id, order.order_line[0].product_id
        )

        self.assertEqual(
            purchase_order.order_line[1].product_id, order.order_line[1].product_id
        )
