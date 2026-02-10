// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Maintenance Contract", {
    onload: function (frm) {
        // if (!frm.doc.start_date) {
        //     frm.set_value("start_date", frappe.datetime.get_today());
        // }
    },
    before_insert: function (frm) {
        if (!frm.doc.start_date) {
            frm.set_value("start_date", frappe.datetime.get_today());
        }
    },
    refresh: function (frm) {
        console.log(frm);
    },
});
