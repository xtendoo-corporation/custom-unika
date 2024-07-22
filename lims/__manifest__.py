# Copyright 2017-2019 MuK IT GmbH
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
{
    "name": "Laboratory Information Management System",
    "summary": """Laboratory Information Management System for Odoo""",
    "version": "15.0.4.0.1",
    "category": "Laboratory Information Management",
    "license": "LGPL-3",
    "website": "https://github.com/OCA/connector-lims",
    "author": "Xtendoo, Odoo Community Association (OCA)",
    "depends": [
        "base",
        "sale",
        "purchase",
        "stock",
        "product",
        "sale_purchase",
        "product_brand",
        "uom",
        "web",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_view.xml",
        "views/analytical_mehotd_price.xml",
        "views/stock_move_line_views.xml",
        "views/res_partner.xml",
        "views/menu.xml",
        "views/product_pricelist_item.xml",
        "views/lims_analysis_parameter_views.xml",
        "views/lims_analysis_parameter_type_views.xml",
        "views/lims_analysis_limit_result_line_views.xml",
        "views/lims_analysis_numerical_result_views.xml",
        "views/lims_parameter_method_uom_rel.xml",
        "views/lims_analysis_views.xml",
        "views/analysis_limit_view.xml",
        "views/analysis_normative_view.xml",
        "views/lims_analysis_line_views.xml",
        "views/res_config_settings.xml",
        "views/stock_picking_view.xml",
        "wizards/wizard_lot.xml",
        "views/stock_production_lot_view.xml",
        "views/lims_analytical_method_views.xml",
        "views/sale_order_view.xml",
        "views/parameter_extra_comment.xml",
        "views/analysis_of_text.xml",
        "views/layout/external_layout_boxed.xml",
        "views/layout/external_layout_boxed_sample_received.xml",
        # Formatos
        "views/label/label_print.xml",
        "report/analysis_report_unika.xml",
        "report/sample_received_report.xml",
        "data/mail_template.xml",

    ],
    "images": ["static/description/banner.png"],
    "application": True,
}
