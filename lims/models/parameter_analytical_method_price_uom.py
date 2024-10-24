# Copyright 2020 Xtendoo - Manuel Calero
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models, api, _
from odoo.exceptions import UserError

from odoo import api, SUPERUSER_ID


class ParameterAnalyticalMethodUomRel(models.Model):
    _name = "parameter.analytical.method.price.uom"
    _description = "Analytical Method Price UOM"

    parent_id = fields.Many2one(
        "lims.analysis",
        "Analysis lims",
    )
    parent_id_new = fields.Many2many(
        'lims.analysis',  # El modelo relacionado
        'parameter_method_analysis',  # Nombre de la tabla intermedia (debe ser el mismo que en el modelo Course)
        'parent_id_new',  # Campo que apunta al modelo 'Student'
        'parameter_method_id_new',  # Campo que apunta al modelo 'Course'
        string='Paquetes'
    )

    analytical_method_id = fields.Many2one(
        "analytical.method.price", string="Method", ondelete="cascade", required=True
    )
    name = fields.Char(related="analytical_method_id.name")
    parameter_id = fields.Many2one(
        related="analytical_method_id.parameter_id"
    )
    price = fields.Float(related="analytical_method_id.price")
    cost = fields.Float(related="analytical_method_id.cost")
    external_lab = fields.Many2one(
        related="analytical_method_id.external_lab"
    )
    company_id = fields.Many2one(
        related="analytical_method_id.company_id"
    )
    parameter_description = fields.Text(string="Descripción", store=True, related="analytical_method_id.parameter_id.description")

    @api.depends('parameter_uom')
    def _compute_required_uom(self):
        for line in self:
            line.required_uom = bool(line.parameter_uom)

    required_uom = fields.Boolean(
        string="Required UOM",
        compute='_compute_required_uom',
        store=True  # Store the result to improve performance
    )
    uom_id = fields.Many2one("uom.uom", string="Unit of Measure")
    parameter_uom = fields.Many2many(related="analytical_method_id.parameter_id.parameter_uom")
    parameter_used_ids = fields.Many2many(
        related="parent_id.parameter_used_ids"

    )

    # analytical_method_id = fields.Many2one(
    #     "analytical.method.price", string="Method", ondelete="cascade", required=True
    # )
    use_acreditation = fields.Boolean(string="Use acreditation", store=True)
    used_acreditation = fields.Many2one(
        "lims.analysis.normative",
        "Acreditation",
    )

    use_normative = fields.Boolean(string="Use normative", store=True)

    used_normative = fields.Many2one(
        "lims.analysis.normative",
        "Normative",
    )

    def _get_is_in_sale(self):
        for record in self:
            sale = self.env['sale.order.line'].search([('parameter_ids', '=', record.id)])
            if sale:
                record.is_in_sale = True
            else:
                record.is_in_sale = False

    is_in_sale = fields.Boolean(string="Ha sido vendido", compute="_get_is_in_sale")

    active = fields.Boolean(default=True, string="Active")

    is_active = fields.Boolean(default=True, string="Está activo")



    @api.onchange('use_acreditation')
    def set_use_acreditation(self):
        if self.use_acreditation and self.use_normative:
            raise UserError(_("Solo se puede acreditar un parámetro o se puede aplicar un criterio de calidad"))
        if not self.use_acreditation:
            self.used_acreditation = False

    @api.onchange('use_normative')
    def set_use_normative(self):
        if self.use_acreditation and self.use_normative:
            raise UserError(_("Solo se puede acreditar un parámetro o se puede aplicar un criterio de calidad"))
        if not self.use_normative:
            self.used_normative = False

    @api.model
    def create(self, vals):
        print("*" * 50)

        # Primero verificamos si el registro ya existe
        analytical_method_id = vals.get('analytical_method_id')
        uom_id = vals.get('uom_id')

        if analytical_method_id:
            method = self.env['analytical.method.price'].browse(analytical_method_id)
            if method:
                # Buscar el registro existente
                existing_method = self.env['parameter.analytical.method.price.uom'].search([
                    ('analytical_method_id', '=', method.id),
                    ('uom_id', '=', uom_id)
                ], limit=1)  # Limitar a 1 ya que solo necesitamos saber si existe uno

                if existing_method:
                    print("El registro ya existe.")
                    new_record = existing_method  # Usamos el registro existente
                else:
                    print("El registro no existe. Creando uno nuevo.")
                    new_record = super().create(vals)  # Crear el nuevo registro

                # Añadir el nuevo registro al campo Many2many si parent_id está presente
                if vals.get('parent_id'):
                    parent = self.env['lims.analysis'].browse(vals.get('parent_id'))
                    if parent:
                        # Verificar si el método ya está en la relación Many2many
                        if new_record not in parent.parameter_method_ids_new:
                            parent.parameter_method_ids_new = [(4, new_record.id)]  # Añadir el nuevo registro
                        else:
                            print("El método ya está en la relación Many2many.")
                else:
                    print("No se proporcionó parent_id. El método se creó o usó sin asignación al padre.")

        print("*" * 50)
        print("CREATE", vals)
        print("*" * 50)
        return new_record  # Retornar el registro creado o existente

    # @api.model
    # def create(self, vals):
    #     print("*" * 50)
    #     if vals.get('analytical_method_id'):
    #         method = self.env['analytical.method.price'].browse(vals['analytical_method_id'])
    #         if method:
    #             if vals.get('uom_id'):
    #                 print("CON UOM")
    #                 is_method_create = self.env['parameter.analytical.method.price.uom'].search(
    #                     [('analytical_method_id', '=', method.id), ('uom_id', '=', vals.get('uom_id'))])
    #             else:
    #                 print("SIN UOM")
    #                 is_method_create = self.env['parameter.analytical.method.price.uom'].search(
    #                     [('analytical_method_id', '=', method.id)])
    #                 print("IS METHOD CREATE", is_method_create)
    #             if not is_method_create:
    #                 print("NO EXISTE")
    #                 new_record = super().create(vals)
    #             if is_method_create:
    #                 if vals.get('parent_id'):
    #                     parent = self.env['lims.analysis'].browse(vals.get('parent_id'))
    #                     print("PARENT", parent)
    #                     if parent:
    #                         if parent.parameter_method_ids:
    #                             for method in parent.parameter_method_ids:
    #                                 if method.analytical_method_id.id == vals.get('analytical_method_id'):
    #                                     raise UserError(_("El método ya está creado"))
    #                                 else:
    #                                     print("AÑADIR")
    #                                     new_record = super().create(vals)
    #                                     parent.parameter_method_ids_new = [(4, new_record.id)]
    #                 else:
    #                     raise UserError(_("El método ya está creado"))
    #
    #     # res = super(ParameterAnalyticalMethodUomRel, self).create(vals)
    #     print("*" * 50)
    #     print("CREATE", vals)
    #     print("*" * 50)
    #     return new_record

    # @api.model
    # def init(self):
    #     #self.update_fields_not_udm()
    #     #self.update_fields_udm()

    def update_fields_not_udm(self):
        print("*" * 50)
        print("Entrando a la función update_fields")

        # Obtener todos los registros ordenados por método analítico y UoM
        records = self.env['parameter.analytical.method.price.uom'].search([], order='analytical_method_id, uom_id')

        # Diccionario para rastrear registros por parameter_id
        repetidos_por_parametro = {}

        # Iterar sobre los registros obtenidos
        for record in records:
            # Verificar si el parámetro no tiene unidades de medida asociadas
            if not record.parameter_id.parameter_uom.ids:
                # Verificar si la unidad de medida (UoM) está vacía o es False
                if not record.uom_id:
                    actual_parameter = record.parameter_id

                    # Si este parámetro ya está en el diccionario, añadir el registro
                    if actual_parameter in repetidos_por_parametro:
                        repetidos_por_parametro[actual_parameter].append(record)
                        print(f"Registro repetido añadido: {record.name}")
                    else:
                        # Si no está en el diccionario, lo añadimos con una lista
                        repetidos_por_parametro[actual_parameter] = [record]
                        print(f"Primer registro del parámetro añadido: {record.name}")

        # Procesar cada grupo de registros repetidos
        for param, registros in repetidos_por_parametro.items():
            if len(registros) > 1:  # Solo procesar si hay más de un registro
                print(f"//////////////////////////////////////////////////")
                print(f"registros {registros}")
                print(f"//////////////////////////////////////////////////")
                print("Ejecutando el método change_parameter_package...")

                # Llamar al método change_parameter_package con el grupo de repetidos
                self.change_parameter_package(registros)
                print("Eliminando duplicados")

        print("*" * 50)

    def update_fields_udm(self):
        print("*" * 50)
        print("Entrando a la función update_fields_udm")

        # Obtener todos los registros ordenados por método analítico y UoM
        records = self.env['parameter.analytical.method.price.uom'].search([], order='analytical_method_id, uom_id')
        print(f"Se encontraron {len(records)} registros.")

        # Diccionarios para agrupar registros
        agrupados_por_metodo_y_uom = {}
        sin_uom = {}

        # Iterar sobre los registros obtenidos
        for record in records:
            # Crear una clave basada en la combinación de analytical_method_id y uom_id (o False si uom_id es None)
            clave = (record.analytical_method_id, record.uom_id or False)

            # Si el registro no tiene uom_id, lo almacenamos temporalmente
            if not record.uom_id:
                if record.analytical_method_id in sin_uom:
                    sin_uom[record.analytical_method_id].append(record)
                else:
                    sin_uom[record.analytical_method_id] = [record]
                print(f"Registro sin uom añadido: {record.name}")
            else:
                # Si la combinación (analytical_method_id, uom_id) ya está en el diccionario, añadir el registro
                if clave in agrupados_por_metodo_y_uom:
                    agrupados_por_metodo_y_uom[clave].append(record)
                    print(f"Registro añadido al grupo existente: {record.name}")
                else:
                    # Si no está en el diccionario, lo añadimos con una lista
                    agrupados_por_metodo_y_uom[clave] = [record]
                    print(
                        f"Primer registro de la combinación {record.analytical_method_id.name} y {record.uom_id.name} añadido: {record.name}")

        # Procesar los grupos con uom_id
        for clave, registros in agrupados_por_metodo_y_uom.items():
            analytical_method_id, uom_id = clave

            # Verificar si hay registros sin uom para este analytical_method_id
            if analytical_method_id in sin_uom:
                # Añadir los registros sin uom al grupo de registros actuales
                for registro_sin_uom in sin_uom[analytical_method_id]:
                    print(
                        f"Añadiendo registro sin uom ({registro_sin_uom.name}) al grupo con uom_id={uom_id.name if uom_id else 'False'}")
                    registro_sin_uom.uom_id = uom_id  # Asignar el uom_id del grupo
                    registros.append(registro_sin_uom)

                # Eliminar el grupo sin uom después de procesarlo
                del sin_uom[analytical_method_id]

            # Si hay más de un registro en la combinación, procesamos el grupo
            if len(registros) > 1:
                print(f"//////////////////////////////////////////////////")
                print(
                    f"Registros para la combinación analytical_method_id={analytical_method_id.name} y uom_id={uom_id.name if uom_id else 'False'}:")
                for r in registros:
                    print(f" - {r.name}")
                print(f"//////////////////////////////////////////////////")
                print("Ejecutando el método change_parameter_package...")

                # Llamar al método change_parameter_package con el grupo de registros
                self.change_parameter_package(registros)
                print("Eliminando duplicados.")

        print("Proceso de actualización completado.")

    def change_parameter_package(self, parameter_repeats):
        if len(parameter_repeats) > 1:
            print("/"*50)
            print("registros", parameter_repeats)
            print("/"*50)
            first_parameter=parameter_repeats[0]
            new_method=[]
            for parameter in parameter_repeats:
                if parameter.parent_id:
                    new_method.append(parameter.parent_id.id)
            if len(new_method) > 0:
                first_parameter.write({
                    'parent_id_new': [(6, 0, new_method)]  # Actualización con una lista de IDs
                })
            self.change_parameter_sales(parameter_repeats)


    def change_parameter_sales(self, parameter_repeats):
        if len(parameter_repeats) > 1:
            first_parameter = parameter_repeats[0]
            for parameter in parameter_repeats:
                if parameter != first_parameter:
                    if parameter.is_in_sale:
                        sales = self.env['sale.order.line'].search([('parameter_ids', '=', parameter.id)])
                        if sales:
                            for sale in sales:
                                # Eliminar el parameter actual de las líneas de venta
                                sale.write({
                                    'parameter_ids': [(3, parameter.id)]  # Eliminar el parameter actual
                                })

                                # Añadir el first_parameter a las líneas de venta
                                sale.write({
                                    'parameter_ids': [(4, first_parameter.id)]  # Agregar el first_parameter
                                })
        self.delete_duplicates(parameter_repeats)

    def delete_duplicates(self, parameter_repeats):
        if len(parameter_repeats) > 1:
            first_parameter = parameter_repeats[0]
            for record in parameter_repeats:
                if record != first_parameter:
                    record.unlink()











