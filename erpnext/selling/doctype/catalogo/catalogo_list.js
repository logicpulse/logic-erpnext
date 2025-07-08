// Adiciona o botão na listagem (List View)
frappe.listview_settings['Catalogo'] = {
	// filters: [
    //     ['Name', 'Like', 1]
    // ],
	onload: function (listview) {
		listview.page.add_inner_button(__('Full Catalogo'), function () {
			const spreadsheet_id = '1Nm6YatjJrugBxM38yaXlIJgLHfVAMCnnMLw83lga5YQ';
			// Não há acesso direto aos campos do formulário na listagem, então use valores padrão ou personalize conforme necessário
			frappe.call({
				method: 'erpnext.selling.doctype.catalogo.catalogo.get_all_catalogs',
				args: {
					spreadsheet_id: spreadsheet_id,
					country: null,
					price_type: null
				},
				callback: function (res) {
					if (res.message) {
						frappe.msgprint(__('Ficheiro gerado com sucesso!'));
					}
				}
			});
		});
	}, 
	dropdown_button: {
		get_label: __("Dropdown"),
		buttons: [
			{
				get_label: __("Catalog"),
				show: function (doc) {
					return true;
				},
				get_description: function (doc) {
					return "Open catalog " + doc.name1;
				},
				action: async function (doc) {
					await generate(doc.ref, doc.sheet_name, doc.cell_range);
					frappe.msgprint("Catalog " + doc.name1 + " successfully opened.");
				}
			},
			{
				get_label: __("Details"),
				show: function (doc) {
					return true;
				},
				get_description: function (doc) {
					return "Open details " + doc.name1;
				},
				action: function (doc) {  
					window.open('/catalogos/' + doc.name, '_blank'); 
				}
			}
		]
	}
};

async function generate(ref, sheet_name, cell_range) {
	const spreadsheet_id = '1Nm6YatjJrugBxM38yaXlIJgLHfVAMCnnMLw83lga5YQ'
	const pais = document.getElementById('pais') ? document.getElementById('pais').value : null;
	const tipoPreco = document.getElementById('tipo_preco') ? document.getElementById('tipo_preco').value : null;

	frappe.call({
		method: 'erpnext.selling.doctype.catalogo.catalogo.get_catalog',
		args: {
			ref: ref,
			spreadsheet_id: spreadsheet_id,
			sheet_name: sheet_name,
			cell_range: cell_range,
			country: pais,
			price_type: tipoPreco
		},
		callback: function (res) {
			if (res.message) {
				// console.log('res:', res);
				// console.log('message:', res.message);
				console.log('Ficheiro gerado com sucesso!');
			}
		}
	});
}