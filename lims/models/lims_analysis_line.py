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
            if analysis.state in ["cancel", "validated", "issued"] or not analysis.product_id:
                analysis.analysis_warn_msg = False
            elif analysis.product_id.analysis_warn == 'required_images' and len(analysis.image_ids.ids) > 0:
                analysis.analysis_warn_msg = False
            else:
                analysis.analysis_warn_msg = analysis.product_id.analysis_warn_msg

    image_ids = fields.One2many(
        "sample.image",
        "analysis_id",
        string="Extra Sample Media",
    )
    lot_name = fields.Char(string="Lote", store=True, tracking=True)
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
    analysis_name = fields.Char(
        string="Análisis de",
        store=True,
        tracking=True,
    )
    description = fields.Char(
        string="Description",
        store=True,
        tracking=True,
    )
    capture_place = fields.Char(
        string="Lugar de recogida",
        store=True,
        tracking=True,
    )
    presentation = fields.Char(
        string="Presentación",
        store=True,
        tracking=True,
    )
    lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Sample number",
        default=lambda self: self.env.context.get("lot_id"),
        tracking=True,
    )

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
        string="Comentarios",
        store=True,
        tracking=True,
    )
#     observations = fields.Text(
#         string="Observaciones",
#         store=True,
#         tracking=True,
#         default="""-Las incertidumbres están calculadas y se encuentran a disposición del cliente que lo solicite.
# -Este informe sólo afecta a la muestra tal como es recibida en el laboratorio, no pudiéndose reproducir total o parcialmente sin la expresa autorización por escrito del laboratorio emisor.
# -Este informe está sometido a las normas de salvaguarda y seguridad establecidas, así como a las contractuales y legales que resulten aplicables.
# Sistema de Gestión de Calidad certificado por BUREAU VERITAS Certification, según la norma ISO 9001:2015 Nº Certificado: ES123521-2""",
#     )
    applied_legislation = fields.Text(
        string="Legislaciones aplicadas",
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

    # Sampling information
    date_issue = fields.Date(
        string="Date Issue",
        tracking=True,
    )
    date_expired = fields.Date(
        string="Caducidad",
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

    date_exit = fields.Date(
        string="Fecha de salida",
        tracking=True,
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
    temperature = fields.Selection(
        [
            ("ambient", "Ambiente"),
            ("refrigered", "Refrigerado"),
            ("freezed", "Congelado"),
        ],
        "Temperatura",
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
            vals["date_sample_receipt"] = move_line_id.move_id.picking_id.date_done
            #Buscamos analysis anterior
            vals["previous_analysis_date"] = self.get_previous_analysis_date(vals.get("product_id"), vals.get("customer_id"))
            vals["previous_analysis_result"] = self.get_previous_analysis_result(vals.get("product_id"), vals.get("customer_id"))
            if move_line_id.lot_id:
                if move_line_id.lot_id.container:
                    vals["presentation"] = move_line_id.lot_id.container
                if move_line_id.lot_id.description:
                    vals["description"] = move_line_id.lot_id.description
                if move_line_id.lot_id.conditions:
                    vals["temperature"] = move_line_id.lot_id.conditions
                if move_line_id.lot_name_sample:
                    vals["lot_name"] = move_line_id.lot_name_sample
                if move_line_id.lot_id.expiration_date:
                    vals["date_expired"] = move_line_id.lot_id.expiration_date
                if move_line_id.lot_id.place:
                    vals["capture_place"] = move_line_id.lot_id.place
                if move_line_id.lot_id.expiration_date:
                    vals["date_expired"] = move_line_id.lot_id.expiration_date
                if move_line_id.product_id:
                    vals["analysis_name"] = move_line_id.product_id.name
            result = super(LimsAnalysisLine, self).create(vals)
            result_comment = ""
            technical_result = None
            if move_line_id.product_id.number_of_samples > 1:
                result_comment = ""
                is_correct_default = False
                is_present_default = False
                use_acreditation = False
                use_normative = False
                for parameter_method in parameter_method_ids:
                    move_line_ids = self.env["stock.move.line"].search(
                        [
                            ("picking_id", "=", move_line_id.picking_id.id),
                            ("product_id", "=", move_line_id.product_id.id),
                        ]
                    )
                    for line_parameter in move_line_ids:
                        for parameter in parameter_method.parameter_id:
                            limit_ids_filter = parameter.limits_ids.filtered(
                                lambda r: r.uom_id == parameter_method.uom_id)
                            # ficha tecnica, Elegimos acreditado o no y si usa normativa.
                            technical_limit = ""
                            if parameter_method.use_acreditation:
                                eval_in_group = False
                                use_acreditation = True
                                acreditation_ids_filter = self.env["lims.analysis.normative"].search(
                                    [
                                        ("parameter_ids", "=", parameter.id),
                                        ("is_acreditation", "=", True),
                                        ("uom_id", "=", parameter_method.uom_id.id)
                                    ]
                                )
                                for line in acreditation_ids_filter.limit_result_line_ids.filtered(
                                        lambda r: r.state == 'conform'):
                                    technical_limit = line.get_correct_limit()

                                    if technical_limit == "Present":
                                        is_present_default = True
                                    if technical_limit == "Correct":
                                        is_correct_default = True
                                    technical_result, eval_in_group = parameter.get_anlysis_result(
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
                                for line in normative_ids_filter.limit_result_line_ids.filtered(
                                        lambda r: r.state == 'conform'):
                                    technical_limit = line.get_correct_limit()
                                    if technical_limit == "Present":
                                        is_present_default = True
                                    if technical_limit == "Correct":
                                        is_correct_default = True
                                    technical_result, eval_in_group = parameter.get_anlysis_result(
                                        normative_ids_filter, 0.00, is_correct_default,
                                        is_present_default)
                                    technical_comment = parameter._get_limit_comment(
                                        normative_ids_filter, 0.00, is_correct_default,
                                        is_present_default)
                            else:
                                for limits_id in limit_ids_filter.filtered(lambda r: r.type == 'technical'):
                                    for limit_line_ids in limits_id.limit_result_line_ids.filtered(
                                            lambda r: r.state == 'conform'):
                                        technical_limit = limit_line_ids.get_correct_limit()
                                        if technical_limit == "Present":
                                            is_present_default = True
                                        if technical_limit == "Correct":
                                            is_correct_default = True
                                technical_result, eval_in_group = parameter.get_anlysis_result(
                                    limit_ids_filter.filtered(lambda r: r.type == 'technical'), 0.00,
                                    is_correct_default, is_present_default)
                                technical_comment = parameter._get_limit_comment(
                                    limit_ids_filter.filtered(lambda r: r.type == 'technical'), 0.00,
                                    is_correct_default, is_present_default)
                            # legislacion
                            legislation_limit = ""
                            legislation_comment = ""
                            legislation_name = ""
                            for limits_id in limit_ids_filter.filtered(lambda r: r.type == 'legislation'):
                                legislation_name = limits_id.legislation_name
                                for limit_line_ids in limits_id.limit_result_line_ids.filtered(
                                        lambda r: r.state == 'conform'):
                                    legislation_limit = limit_line_ids.get_correct_limit()
                            legislation_result, eval_in_group = parameter.get_anlysis_result(
                                limit_ids_filter.filtered(lambda r: r.type == 'legislation'), 0.00, is_correct_default,
                                is_present_default)
                            legislation_comment = parameter._get_limit_comment(
                                limit_ids_filter.filtered(lambda r: r.type == 'legislation'), 0.00, is_correct_default,
                                is_present_default)
                            if parameter.required_comment:
                                result_comment = technical_comment
                                if legislation_result != 'pass' or legislation_result is not None:
                                    result_comment = legislation_comment
                            if not parameter.required_comment:
                                result_comment = ""
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
                                    "lot_name": line_parameter.lot_name_sample,
                                    "sample_sub_number": line_parameter.sample_sub_number,
                                    "global_result": "",
                                    "eval_in_group": eval_in_group,
                                }
                            )
            else:
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
                                technical_result, eval_in_group = parameter.get_anlysis_result(
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
                                technical_result, eval_in_group = parameter.get_anlysis_result(
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
                            technical_result, eval_in_group = parameter.get_anlysis_result(limit_ids_filter.filtered(lambda r: r.type == 'technical'), 0.00, is_correct_default, is_present_default)
                            technical_comment = parameter._get_limit_comment(limit_ids_filter.filtered(lambda r: r.type == 'technical'), 0.00, is_correct_default, is_present_default)
                        #legislacion
                        legislation_limit = ""
                        legislation_comment =""
                        legislation_name=""
                        for limits_id in limit_ids_filter.filtered(lambda r: r.type == 'legislation'):
                            legislation_name = limits_id.legislation_name
                            for limit_line_ids in limits_id.limit_result_line_ids.filtered(lambda r: r.state == 'conform'):
                                legislation_limit = limit_line_ids.get_correct_limit()
                        legislation_result, eval_in_group = parameter.get_anlysis_result(
                            limit_ids_filter.filtered(lambda r: r.type == 'legislation'), 0.00, is_correct_default,
                            is_present_default)
                        legislation_comment = parameter._get_limit_comment(
                            limit_ids_filter.filtered(lambda r: r.type == 'legislation'), 0.00, is_correct_default,
                            is_present_default)
                        if parameter.required_comment:
                            result_comment = technical_comment
                            if legislation_result != 'pass' or legislation_result is not None:
                                result_comment = legislation_comment
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
                                "lot_name": move_line_id.lot_name,
                                "sample_sub_number": move_line_id.sample_sub_number,
                                "global_result": "",
                                "eval_in_group": eval_in_group,
                            }
                        )
            return result

    def write(self, vals):
        result = super(LimsAnalysisLine, self).write(vals)
        parameters = []
        for line in self.numerical_result:
            if line.parameter_ids.max_samples_number > 1 and line.parameter_ids not in parameters:
                parameters.append(line.parameter_ids)
        for parameter in parameters:
            fail_num = sum(1 for line in self.numerical_result.filtered(lambda x: x.parameter_ids.id == parameter.id) if line.result_legislation == 'fail')
            if fail_num > 0:
                for line in self.numerical_result.filtered(lambda x: x.parameter_ids.id == parameter.id):
                    # line.eval_in_group = True
                    line.global_result = 'fail'
            else:
                between_limit = sum(1 for line in self.numerical_result.filtered(lambda x: x.parameter_ids.id == parameter.id) if line.eval_in_group == True)
                max_permited = parameter.max_samples_permitted
                for line in self.numerical_result.filtered(lambda x: x.parameter_ids.id == parameter.id):
                    if between_limit > max_permited:
                        line.global_result = 'fail'
                    else:
                        line.global_result = 'pass'
        return result
    def unlink(self):
        if any(analysis.state not in ["cancel"] for analysis in self):
            raise UserError(_("You can only delete Cancel analyses."))
        analysis_lines = self.env["lims.analysis.numerical.result"].search([
            ("analysis_ids", "in", self.ids),
        ])
        if analysis_lines:
            analysis_lines.unlink()
        return super(LimsAnalysisLine, self).unlink()

    def toggle_active(self):
        if any(record.state != "cancel" for record in self):
            raise UserError(_("Only 'Canceled' records can be archived"))
        res = super().toggle_active()
        return res

    def action_cancel(self):
        if any(analysis.state == "cancel" for analysis in self):
            raise UserError(_("You can't cancel already canceled analyses."))
        analyses_to_cancel = self.filtered(lambda analysis: analysis.state != "cancel")
        if analyses_to_cancel:
            analyses_to_cancel.write({
                "state": "cancel",
                "result": "none"
            })
        return True
    def action_draft(self):
        if any(analysis.state != "cancel" for analysis in self):
            raise UserError(_("You can only draft canceled analyses."))
        analyses_to_draft = self.filtered(lambda analysis: analysis.state == "cancel")
        if analyses_to_draft:
            analyses_to_draft.write({"state": "draft"})
        return True

    def action_received(self):
        if any(analysis.state != "draft" for analysis in self):
            raise UserError(_("You can only receive drafts analyses."))
        analyses_to_receive = self.filtered(lambda analysis: analysis.state == "draft")
        if analyses_to_receive:
            analyses_to_receive.write({"state": "received", "date_sample_receipt": fields.Datetime.now()})
        return True
    def action_start_analysis(self):
        if any(analysis.state != "received" for analysis in self):
            raise UserError(_("You can only start the analysis for received analyses."))
        analyses_to_start = self.filtered(lambda analysis: analysis.state == "received")
        if analyses_to_start:
            analyses_to_start.write({"state": "started", "date_sample_begin": fields.Datetime.now()})
        return True
    def action_complete(self):
        if any(analysis.state != "started" for analysis in self):
            raise UserError(_("You can only complete started analyses."))

        analyses_to_complete = self.filtered(lambda analysis: analysis.state == "started")

        if analyses_to_complete:
            for analysis in analyses_to_complete:
                if analysis.product_id.analysis_warn == 'required_images' and not analysis.image_ids:
                    raise UserError(_("Image/s are required to complete the analysis."))

                # TO-DO: Realizar el análisis y cambiar el result.
                analysis_result = "pass"
                result_value = []

                for result in analysis.numerical_result:
                    if result.parameter_ids.max_samples_number > 1:
                        result_value.append(result.global_result)
                    else:
                        result_value.append(result.result_datasheet)
                        result_value.append(result.result_legislation)

                for line in result_value:
                    if line == "fail":
                        analysis_result = line
                        break
                    if line == "warning":
                        analysis_result = line

                analysis.write({
                    "state": "complete",
                    "result": analysis_result,
                    "date_complete": fields.Datetime.now(),
                })

        return True

    def action_validate(self):
        if any(analysis.state != "complete" for analysis in self):
            raise UserError(_("You can only validate complete analyses."))
        analyses_to_validate = self.filtered(lambda analysis: analysis.state == "complete")
        if analyses_to_validate:
            analyses_to_validate.write({
                "state": "validated",
                "date_due": fields.Datetime.now(),
            })
        return True

    def action_issue(self):
        if any(analysis.state != "validated" for analysis in self):
            raise UserError(_("You can only issue validated analyses."))
        analyses_to_issue = self.filtered(lambda analysis: analysis.state == "validated")
        if analyses_to_issue:
            analyses_to_issue.write({
                "state": "issued",
                "date_issue": fields.Datetime.now(),
            })
        return True

    @api.model
    def _get_parameters_type(self):
        return self.env["lims.analysis.parameter.type.tags"].search([('id', '>', 0)])

    @api.model
    def get_previous_analysis_date(self, product_id, partner_id):
        try:
            previous_analysis = self.env["lims.analysis.line"].search(
                [
                    ("product_id", "=", product_id),
                    ("customer_id", "=", partner_id),
                ], order="date_complete DESC", limit=1
            )
            if previous_analysis:
                return previous_analysis.date_complete
            return None  # Devuelve None si no hay análisis previos
        except Exception as e:
            raise UserError(_("Error fetching previous analysis date: %s" % e))

    @api.model
    def get_previous_analysis_result(self, product_id, partner_id):
        try:
            previous_analysis = self.env["lims.analysis.line"].search(
                [
                    ("product_id", "=", product_id),
                    ("customer_id", "=", partner_id),
                ], order="date_complete DESC", limit=1
            )
            if previous_analysis:
                return previous_analysis.result
            return None  # Devuelve None si no hay análisis previos
        except Exception as e:
            raise UserError(_("Error fetching previous analysis result: %s" % e))
