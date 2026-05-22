// Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Maintenance Contract", {
    client: function (frm) {
        if (!frm.doc.client) {
            frm.set_value("email_contacto", "");
            return;
        }
        frm.call("get_email_contacto")
            .then((r) => {
                frm.refresh_field('email_contacto');
            })
            .catch((e) => {
                console.log('Error: ', e);
            });
    },
    validate: function (frm) {
        if (frm.doc.email_contacto) {
            return;
        }

        return new Promise((resolve, reject) => {
            frappe.confirm(
                __(
                    "O email de contacto não foi encontrado. Deseja continuar?<br>Sem o email de contacto, o cliente não será notificado sobre o contrato de manutenção, data de início e fim do contrato."
                ),
                () => resolve(),
                () => {
                    frappe.validated = false;
                    reject();
                }
            );
        });
    },
});
