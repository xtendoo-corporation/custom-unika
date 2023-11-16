odoo.define('lims.global_result', function (require) {
    "use strict";

    var core = require('web.core');
    var fieldRegistry = require('web.field_registry');
    var basicFields = require('web.basic_fields');

    var FieldFloat = basicFields.FieldFloat;

    var MyFieldFloat = FieldFloat.extend({
        events: _.extend({}, FieldFloat.prototype.events, {
            'change input': '_onValueChange',
        }),

        _onValueChange: function () {
            this._super.apply(this, arguments);
            var newValue = this._getValue();
            console.log("Nuevo valor:", newValue);
            // Puedes hacer más cosas aquí con el nuevo valor si es necesario
        },
    });

    fieldRegistry.add('my_field_float', MyFieldFloat);

    return {
        MyFieldFloat: MyFieldFloat,
    };
});
//odoo.define('lims.lims_analysis_numerical_result', function (require) {
//    "use strict";
//
//    var form_common = require('web.form_common');
//
//    form_common.WidgetButton.include({
//        onValueChange: function (value) {
//            this.field_manager.fields.result_legislation.set_value(value);
//            console.log("log consola")
//            console.log("this.field_manager.fields.result_legislation.get_value(value)a")
////            alert(this.field_manager.fields.result_legislation.get_value(value));
//
////            this._checkAndUpdateGlobalResult();
//        },
//
//        _checkAndUpdateGlobalResult: function () {
//            var self = this;
//            var parameterId = this.field_manager.fields.parameter_ids.get_value();
//            var maxSampleNumber = this.field_manager.fields.parameter_ids.max_sample_number;
//
//            // Filtra las líneas con el mismo parameter_ids
//            var linesWithSameParameter = this.dataset.get_domain().filter(function (filter) {
//                return filter[0] === 'parameter_ids' && filter[2] === parameterId;
//            }).map(function (lineId) {
//                return self.dataset.get_records({id: lineId})[0];
//            });
//
//            // Obtiene el número de líneas con 'pass'
//            var linesWithPass = linesWithSameParameter.filter(function (line) {
//                return line.get('result_legislation') === 'pass';
//            });
//
//            // Actualiza el campo 'global_result' en todas las líneas con el mismo parameter_ids
//            linesWithSameParameter.forEach(function (line) {
//                if (linesWithPass.length >= maxSampleNumber) {
//                    line.set('global_result', 'fail');
//                } else {
//                    line.set('global_result', 'pass');
//                }
//            });
//        },
//    });
//});