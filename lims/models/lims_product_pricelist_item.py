# Copyright 2017  Alexandre Díaz, Pablo Quesada, Darío Lodeiros
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.tools.misc import formatLang


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    analysis_group_ids = fields.Many2one(
        "lims.analysis",
        "Analysis Group",
        ondelete="cascade",
        check_company=True,
    )
    analitycal_method_ids = fields.Many2one(
        "analytical.method.price",
        "Method",
        ondelete="cascade",
        check_company=True,
    )

    applied_on = fields.Selection(
        [
            ("5_analytical_method", "Analytical Method"),
            ("4_analysis_group", "Analysis group"),
            ("3_global", "All Products"),
            ("2_product_category", "Product Category"),
            ("1_product", "Product"),
            ("0_product_variant", "Product Variant"),
        ],
        "Apply On",
        default="3_global",
        required=True,
        help="Pricelist Item applicable on selected option",
    )

    @api.depends(
        "applied_on",
        "categ_id",
        "product_tmpl_id",
        "product_id",
        "compute_price",
        "fixed_price",
        "pricelist_id",
        "percent_price",
        "price_discount",
        "price_surcharge",
        "analysis_group_ids",
        "analitycal_method_ids",
    )
    def _get_pricelist_item_name_price(self):
        for item in self:
            if item.categ_id and item.applied_on == "2_product_category":
                item.name = _("Category: %s") % (item.categ_id.display_name)
            elif item.product_tmpl_id and item.applied_on == "1_product":
                item.name = _("Product: %s") % (item.product_tmpl_id.display_name)
            elif item.product_id and item.applied_on == "0_product_variant":
                item.name = _("Variant: %s") % (
                    item.product_id.with_context(
                        display_default_code=False
                    ).display_name
                )
            elif item.analysis_group_ids and item.applied_on == "4_analysis_group":
                item.name = _("Paquete: %s") % (item.analysis_group_ids.name)
            elif (
                item.analitycal_method_ids and item.applied_on == "5_analytical_method"
            ):
                item.name = item.analitycal_method_ids.name
            else:
                item.name = _("All Products")

            if item.compute_price == "fixed":
                item.price = formatLang(
                    item.env,
                    item.fixed_price,
                    monetary=True,
                    dp="Product Price",
                    currency_obj=item.currency_id,
                )
            elif item.compute_price == "percentage":
                item.price = _("%s %% discount", item.percent_price)
            else:
                item.price = _(
                    "%(percentage)s %% discount and %(price)s surcharge",
                    percentage=item.price_discount,
                    price=item.price_surcharge,
                )
