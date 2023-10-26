# Copyright 2021 - Daniel Domínguez https://xtendoo.es/
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import datetime

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class LimsAnalysisLine(models.Model):
    _name = "lims.analysis.line"
    _inherit = ["mail.thread"]
    _description = "Analysis Line LIMS"

    analysis_warn_msg = fields.Text(compute="_compute_analysis_warn_msg")

    @api.depends(
        "state", "product_id.analysis_warn", "image_ids"
    )
    def _compute_analysis_warn_msg(self):

        for analysis in self:
            if analysis.state in ["cancel", "validated", "issued"]:
                analysis.analysis_warn_msg = False
                return
            if not self.product_id:
                analysis.analysis_warn_msg = False
                return
            if self.product_id.analysis_warn == 'required_images':
                if len(self.image_ids.ids) > 0:
                    analysis.analysis_warn_msg = False
                    return
            analysis.analysis_warn_msg = self.product_id.analysis_warn_msg

    image_ids = fields.One2many(
        "sample.image",
        "analysis_id",
        string="Extra Sample Media",
    )

    name = fields.Char(string="Name", store=True, readonly="1")
    analysis_id = fields.Many2one(
        "lims.analysis",
        "Analysis",
        invisible=True,
        tracking=True,
    )
    numerical_result = fields.One2many(
        "lims.analysis.numerical.result",
        "analysis_ids",
        tracking=True,
    )
    stock_move_line_id = fields.Many2one(
        "stock.move.line",
        "Stock Line Move",
        default=lambda self: self.env.context.get("stock_move_line_id"),
        tracking=True,
    )
    product_id = fields.Many2one(
        "product.template",
        "Products",
        default=lambda self: self.env.context.get("product_id"),
        tracking=True,
    )
    pricelist_id = fields.Many2one("product.pricelist", "pricelist")
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Low"), ("2", "Medium"), ("3", "High")],
        "Priority",
        default="1",
        tracking=True,
    )
    state = fields.Selection(
        [
            ("cancel", "Cancel"),
            ("draft", "Draft"),
            ("received", "Received"),
            ("started", "Started"),
            ("complete", "Complete"),
            ("validated", "Validated"),
            ("issued", "Issued"),
        ],
        "State",
        default="received",
        tracking=True,
    )
    result = fields.Selection(
        [
            ("none", "Unrealized"),
            ("pass", "Approved"),
            ("fail", "Failed"),
            ("warning", "Warning"),
        ],
        "Result",
        default="none",
        tracking=True,
    )
    is_duplicate = fields.Boolean(string="Is Duplicate", store=True)
    all_test_received = fields.Boolean(string="All Test Received", store=True)
    change = fields.Boolean(string="Change", store=True)
    # Request
    is_locked = fields.Boolean(string="Is Locked", store=True)
    incomplete = fields.Boolean(string="Incomplete", store=True)
    out_of_time = fields.Boolean(string="Out Of Time", store=True)
    # Sample information
    sample_name = fields.Char(
        string="Sample Name",
        store=True,
        tracking=True,
    )
    description = fields.Char(
        string="Description",
        store=True,
        tracking=True,
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Sample number",
        default=lambda self: self.env.context.get("lot_id"),
        tracking=True,
    )
    # Campo matrix indicara el conjunto de test al que pertenede
    # Matrix

    # Campo para registrar la regulacion
    # Regulation

    # General Information
    laboratory_id = fields.Many2one(
        comodel_name="res.partner",
        string="Laboratory",
        tracking=True,
    )
    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        default=lambda self: self.env.context.get("customer_id"),
        tracking=True,
    )
    maker_id = fields.Many2one(
        comodel_name="res.partner",
        string="Maker",
        tracking=True,
    )
    customer_contact_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer contact",
        default=lambda self: self.env.context.get("customer_id"),
        tracking=True,
    )
    reason = fields.Char(
        string="Reason",
        store=True,
        tracking=True,
    )
    note = fields.Text(
        string="Note",
        store=True,
        tracking=True,
    )
    reference = fields.Char(
        string="Reference",
        store=True,
        tracking=True,
    )
    active = fields.Boolean(
        string="Active",
        store=True,
        default=True,
        tracking=True,
    )
    is_locked = fields.Boolean(
        string="Is Locked",
        store=True,
        tracking=True,
    )
    # Ver que tags llevaran a que tabla conectarlo
    # tag_ids = fields.Many2one(
    #    comodel_name="",
    #    string="Tag",
    # )
    # Sampling information
    date_issue = fields.Date(
        string="Date Issue",
        tracking=True,
    )
    date_due = fields.Date(
        string="Date due",
        tracking=True,
    )
    date_sample = fields.Date(
        string="Date sample",
        tracking=True,
    )
    date_sample_receipt = fields.Date(
        string="Date sample receipt",
        tracking=True,
    )
    date_sample_begin = fields.Date(
        string="Date sample begin",
        tracking=True,
    )
    date_complete = fields.Date(
        string="Date Complete",
        tracking=True,
    )
    previous_analysis_date = fields.Date(
        string="Previous Analysis Date",
    )

    previous_analysis_result = fields.Selection(
        [
            ("none", "Unrealized"),
            ("pass", "Approved"),
            ("fail", "Failed"),
            ("warning", "Warning"),
        ],
        "Result Previous",
    )

    sampler = fields.Many2one(
        comodel_name="res.users",
        string="Sampler",
        default=lambda self: self.env.user.id,
        tracking=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.user.company_id.id,
    )

    parameter_type_in_lims = fields.Many2many(
        'lims.analysis.parameter.type.tags',
        'parameter_analysis_rel', 'analysis_id',
        'type_id',
        string='Types',
        default=lambda self: self._get_parameters_type(),
    )



    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("analysis.line.lims.code") or "/"
            )
            move_line_id = self.env["stock.move.line"].search(
                [
                    ("id", "=", vals.get("stock_move_line_id")),
                ]
            )
            parameter_method_ids = (
                move_line_id.move_id.purchase_line_id.sale_line_id.parameter_ids
            )
            vals["date_sample_receipt"] = datetime.datetime.now()
            #Buscamos analysis anterior
            vals["previous_analysis_date"] = self.get_previous_analysis_date(vals.get("product_id"), vals.get("customer_id"))
            vals["previous_analysis_result"] = self.get_previous_analysis_result(vals.get("product_id"), vals.get("customer_id"))

            result = super(LimsAnalysisLine, self).create(vals)
            for parameter_method in parameter_method_ids:
                result_comment = ""
                is_correct_default = False
                is_present_default = False
                use_acreditation = False
                use_normative = False
                for parameter in parameter_method.parameter_id:
                    limit_ids_filter = parameter.limits_ids.filtered(lambda r: r.uom_id == parameter_method.uom_id)
                    # ficha tecnica, Elegimos acreditado o no y si usa normativa.
                    technical_limit = ""
                    if parameter_method.use_acreditation:
                        use_acreditation = True
                        acreditation_ids_filter = self.env["lims.analysis.normative"].search(
                            [
                                ("parameter_ids", "=", parameter.id),
                                ("is_acreditation", "=", True),
                                ("uom_id", "=", parameter_method.uom_id.id)
                            ]
                        )
                        for line in acreditation_ids_filter.limit_result_line_ids.filtered(lambda r: r.state == 'conform'):
                            technical_limit = line.get_correct_limit()

                            if technical_limit == "Present":
                                is_present_default = True
                            if technical_limit == "Correct":
                                is_correct_default = True
                            technical_result = parameter.get_anlysis_result(
                                acreditation_ids_filter, 0.00, is_correct_default,
                                is_present_default)
                            technical_comment = parameter._get_limit_comment(
                                acreditation_ids_filter, 0.00, is_correct_default,
                                is_present_default)
                    elif parameter_method.use_normative:
                        use_normative = True
                        normative_ids_filter = self.env["lims.analysis.normative"].search(
                            [
                                ("parameter_ids", "=", parameter.id),
                                ("is_acreditation", "=", False),
                                ("uom_id", "=", parameter_method.uom_id.id)
                            ]
                        )
                        for line in normative_ids_filter.limit_result_line_ids.filtered(lambda r: r.state == 'conform'):
                            technical_limit = line.get_correct_limit()
                            if technical_limit == "Present":
                                is_present_default = True
                            if technical_limit == "Correct":
                                is_correct_default = True
                            technical_result = parameter.get_anlysis_result(
                                normative_ids_filter, 0.00, is_correct_default,
                                is_present_default)
                            technical_comment = parameter._get_limit_comment(
                                normative_ids_filter, 0.00, is_correct_default,
                                is_present_default)
                    else:
                        for limits_id in limit_ids_filter.filtered(lambda r: r.type == 'technical'):
                            for limit_line_ids in limits_id.limit_result_line_ids.filtered(lambda r: r.state == 'conform'):
                                technical_limit = limit_line_ids.get_correct_limit()
                                if technical_limit == "Present":
                                    is_present_default = True
                                if technical_limit == "Correct":
                                    is_correct_default = True
                        technical_result = parameter.get_anlysis_result(limit_ids_filter.filtered(lambda r: r.type == 'technical'), 0.00, is_correct_default, is_present_default)
                        technical_comment = parameter._get_limit_comment(limit_ids_filter.filtered(lambda r: r.type == 'technical'), 0.00, is_correct_default, is_present_default)
                    #legislacion
                    legislation_limit = ""
                    legislation_comment =""
                    legislation_name=""
                    for limits_id in limit_ids_filter.filtered(lambda r: r.type == 'legislation'):
                        legislation_name = limits_id.legislation_name
                        for limit_line_ids in limits_id.limit_result_line_ids.filtered(lambda r: r.state == 'conform'):
                            legislation_limit = limit_line_ids.get_correct_limit()
                    legislation_result = parameter.get_anlysis_result(
                        limit_ids_filter.filtered(lambda r: r.type == 'legislation'), 0.00, is_correct_default,
                        is_present_default)
                    legislation_comment = parameter._get_limit_comment(
                        limit_ids_filter.filtered(lambda r: r.type == 'legislation'), 0.00, is_correct_default,
                        is_present_default)
                    # etiquetado
                    # label_limit = ""
                    # label_comment = ""
                    # for limits_id in limit_ids_filter.filtered(lambda r: r.type == 'label'):
                    #     for limit_line_ids in limits_id.limit_result_line_ids.filtered(lambda r: r.state == 'conform'):
                    #         label_limit = limit_line_ids.get_correct_limit()
                    # label_result = parameter.get_anlysis_result(
                    #     limit_ids_filter.filtered(lambda r: r.type == 'label'), 0.00, is_correct_default,
                    #     is_present_default)
                    # label_comment = parameter._get_limit_comment(
                    #     limit_ids_filter.filtered(lambda r: r.type == 'label'), 0.00, is_correct_default,
                    #     is_present_default)
                    if parameter.required_comment:
                        result_comment = technical_comment
                        if legislation_result != 'pass' or legislation_result is not None:
                            result_comment = legislation_comment
                        # elif label_result != 'pass' or label_result is not None:
                        #     result_comment = label_comment
                    self.env["lims.analysis.numerical.result"].create(
                        {
                            "analysis_ids": result.id,
                            "parameter_ids": parameter_method.parameter_id.id,
                            "parameter_uom": parameter_method.uom_id.id,
                            "value": 0.00,
                            "data_sheet": technical_limit,
                            "legislation_value": legislation_limit,
                            "is_present": is_present_default,
                            "is_correct": is_correct_default,
                            "result_legislation": legislation_result,
                            "result_datasheet": technical_result,
                            "analytical_method_id": parameter_method.analytical_method_id.analytical_method_id.id,
                            "legislation_used_name": legislation_name,
                            "to_invoice": False,
                            "comment": result_comment,
                            "use_acreditation": use_acreditation,
                            "use_normative": use_normative,
                        }
                    )
                    # self.env["lims.analysis.numerical.result"].create(
                    #     {
                    #         "analysis_ids": result.id,
                    #         "parameter_ids": parameter_method.parameter_id.id,
                    #         "parameter_uom": parameter_method.uom_id.id,
                    #         "value": 0.00,
                    #         "data_sheet": technical_limit,
                    #         "legislation_value": legislation_limit,
                    #         "labeled": label_limit,
                    #         "is_present": is_present_default,
                    #         "is_correct": is_correct_default,
                    #         "result_legislation": legislation_result,
                    #         "result_label": label_result,
                    #         "result_datasheet": technical_result,
                    #         "analytical_method_id": parameter_method.analytical_method_id.analytical_method_id.id,
                    #         "to_invoice": False,
                    #         "comment": result_comment,
                    #     }
                    # )
        return result

    def unlink(self):
        if self.filtered(lambda a: a.state not in ["cancel"]):
            raise UserError(_("You only can delete Cancel analysis"))
        analysis_line = self.env["lims.analysis.numerical.result"].search(
            [
                ("analysis_ids", "=", self.id),
            ]
        )
        if analysis_line:
            for line in analysis_line:
                line.unlink()
        return super().unlink()

    def toggle_active(self):
        res = super().toggle_active()
        if self.filtered(lambda so: so.state not in ["cancel"]):
            raise UserError(_("Only 'Canceled' orders can be archived"))
        return res

    def action_cancel(self):
        if self.filtered(lambda self: self.state in ["cancel"]):
            raise UserError(_("You can't cancel Cancel analysis"))
        res = self.write(
            {
                "state": "cancel",
                "result": "none"
            }
        )
        return res

    def action_draft(self):
        if self.filtered(lambda self: self.state not in ["cancel"]):
            raise UserError(_("You can draft only Cancel analysis"))
        res = self.write({"state": "draft"})
        return res

    def action_received(self):
        if self.filtered(lambda self: self.state != "draft"):
            raise UserError(_("You can only received a draft analysis"))
        res = self.write(
            {"state": "received", "date_sample_receipt": datetime.datetime.now()}
        )
        return res

    def action_start_analysis(self):
        if self.filtered(lambda self: self.state != "received"):
            raise UserError(_("You can only Start Analysis a received analysis"))
        res = self.write(
            {"state": "started", "date_sample_begin": datetime.datetime.now()}
        )
        return res

    def action_complete(self):
        if self.filtered(lambda self: self.state != "started"):
            raise UserError(_("You can only Complete a started analysis"))
        if self.product_id.analysis_warn == 'required_images':
            if len(self.image_ids.ids) == 0:
                raise UserError(_("Image/s are required for complete the anañysis"))
        # TO-DO: Realizar el analisis y cambiar el result.
        analysis_result = "pass"
        result_value = []
        for result in self.numerical_result:
            result_value.append(result.result_datasheet)
            result_value.append(result.result_legislation)
            # result_value.append(result.result_label)

        for line in result_value:
            if line == "fail":
                analysis_result = line
                break
            if line == "warning":
                analysis_result = line
        res = self.write(
            {
                "state": "complete",
                "result": analysis_result,
                "date_complete": datetime.datetime.now(),
            }
        )
        return res

    def action_validate(self):
        if self.filtered(lambda self: self.state != "complete"):
            raise UserError(_("You can only Validate  a complete analysis"))
        res = self.write({"state": "validated", "date_due": datetime.datetime.now()})
        return res

    def action_issue(self):
        if self.filtered(lambda self: self.state != "validated"):
            raise UserError(_("You can only Issue a validated analysis"))
        res = self.write({"state": "issued", "date_issue": datetime.datetime.now()})
        return res

    def _get_parameters_type(self):
        type=self.env["lims.analysis.parameter.type.tags"].search([('id', '>', 0)])
        return type

    def get_previous_analysis_date(self, product_id, partner_id):
        previous_analysis = self.env["lims.analysis.line"].search(
            [
                ("product_id", "=", product_id),
                ("customer_id", "=", partner_id),
            ], order="date_complete DESC", limit=1
        )
        if previous_analysis:
            return previous_analysis.date_complete
        return

    def get_previous_analysis_result(self, product_id, partner_id):
        previous_analysis = self.env["lims.analysis.line"].search(
            [
                ("product_id", "=", product_id),
                ("customer_id", "=", partner_id),
            ], order="date_complete DESC", limit=1
        )
        if previous_analysis:
            return previous_analysis.result
        return
