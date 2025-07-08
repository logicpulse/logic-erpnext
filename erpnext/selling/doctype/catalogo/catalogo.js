// Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Catalogo", {
	refresh(frm) {
		frm.add_custom_button(__('Generate All'), async function () {
			console.log('generate_all called');
			const spreadsheet_id = '1Nm6YatjJrugBxM38yaXlIJgLHfVAMCnnMLw83lga5YQ'
			const pais = document.getElementById('pais') ? document.getElementById('pais').value : null;
			const tipoPreco = document.getElementById('tipo_preco') ? document.getElementById('tipo_preco').value : null;

			frappe.call({
				method: 'erpnext.selling.doctype.catalogo.catalogo.get_all_catalogs',
				args: {
					spreadsheet_id: spreadsheet_id,
					country: pais,
					price_type: tipoPreco
				},
				callback: function (res) {
					if (res.message) {
						console.log('Ficheiro gerado com sucesso!');
					}
				}
			});
		}, __('Actions'));

	},
});


