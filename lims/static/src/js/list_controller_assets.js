odoo.define("lims.list_controller_assets", function (require) {
    "use strict";
    var core = require("web.core");
    var Dialog = require("web.Dialog");
    var ListConfirmDialog = require("web.ListConfirmDialog");
    var _t = core._t;
    var ListController = require("web.ListController");

    ListController.include({
        _saveMultipleRecords: function (recordId, node, changes) {
            var fieldName = Object.keys(changes)[0];
            var value = Object.values(changes)[0];
            var recordIds = _.union([recordId], this.selectedRecords);
            var validRecordIds = recordIds.reduce((result, nextRecordId) => {
                var record = this.model.get(nextRecordId);
                var modifiers = this.renderer._registerModifiers(node, record);
                if (!modifiers.readonly && (!modifiers.required || value)) {
                    var oldValue = record.data[fieldName];
                    if (
                        oldValue &&
                        record.data.id !== this.model.get(recordId).data.id
                    ) {
                    } else {
                        result.push(nextRecordId);
                    }
                }
                return result;
            }, []);
            return new Promise((resolve, reject) => {
                const discardAndReject = () => {
                    this.model.discardChanges(recordId);
                    this._confirmSave(recordId).then(() => {
                        this.renderer.focusCell(recordId, node);
                        reject();
                    });
                };
                const saveRecords = () => {
                    this.model
                        .saveRecords(this.handle, recordId, validRecordIds, fieldName)
                        .then(async () => {
                            this.updateButtons("readonly");
                            const state = this.model.get(this.handle);
                            // We need to check the current multi-editable state here
                            // in case the selection is changed. If there are changes
                            // and the list was multi-editable, we do not want to select
                            // the next row.
                            this.selectedRecords = [];
                            await this._updateRendererState(state, {
                                keepWidths: true,
                                selectedRecords: [],
                            });
                            this._updateSelectionBox();
                            this.renderer.focusCell(recordId, node);
                            resolve(!Object.keys(changes).length);
                        })
                        .guardedCatch(discardAndReject);
                };
                if (validRecordIds.length > 0) {
                    if (recordIds.length === 1) {
                        // Save without prompt
                        return saveRecords();
                    }
                    const dialogOptions = {
                        confirm_callback: saveRecords,
                        cancel_callback: discardAndReject,
                    };
                    const record = this.model.get(recordId);
                    const dialogChanges = {
                        isDomainSelected: this.isDomainSelected,
                        fieldLabel:
                            node.attrs.string || record.fields[fieldName].string,
                        fieldName: node.attrs.name,
                        nbRecords: recordIds.length,
                        nbValidRecords: validRecordIds.length,
                    };
                    new ListConfirmDialog(
                        this,
                        record,
                        dialogChanges,
                        dialogOptions
                    ).open({shouldFocusButtons: true});
                } else {
                    Dialog.alert(this, _t("No valid record to save"), {
                        confirm_callback: discardAndReject,
                    });
                }
            });
        },
    });
    return ListController;
});
