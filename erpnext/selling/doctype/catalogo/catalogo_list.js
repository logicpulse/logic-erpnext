var compress = true;
// Adiciona o botão na listagem (List View)
frappe.listview_settings['Catalogo'] = {
	 // Variável para controlar a compressão
	// filters: [
	//     ['Name', 'Like', 1]
	// ],
	onload: function (listview) {
		listview.page.add_inner_button(__('Full Catalog'), function () {
			const spreadsheet_id = '1Nm6YatjJrugBxM38yaXlIJgLHfVAMCnnMLw83lga5YQ';
			// Seleciona o botão recém-criado
			const btns = document.querySelectorAll('.btn-inner-group .btn');
			let btn = null;
			btns.forEach(b => {
				if (b.innerText.trim() === 'Full Catalog') {
					console.log('Button found:', b);
					btn = b;
				}
			});
			if (btn) {
				btn.disabled = true;
				btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Gerando catálogo...';
			}
			frappe.call({
				method: 'erpnext.selling.doctype.catalogo.catalogo.get_all_catalogs',
				args: {
					spreadsheet_id: spreadsheet_id,
					country: 'PT',
					price_type: 'PVP'
				},
				callback: function (res) {
					if (btn) {
						btn.disabled = false;
						btn.innerHTML = 'Open Catalogs';
					}
					if (res.message) {
						console.log('res.message:', res.message);
						window.open(res.message, '_blank');
						frappe.msgprint(__('Ficheiro gerado com sucesso!'));
					} else {
						frappe.msgprint(__('No catalogs found or an error occurred.'));
					}
				}
			});
		});

		// Adiciona um checkbox customizado na barra de botões
		const checkbox = document.createElement('input');
		checkbox.type = 'checkbox';
		checkbox.id = 'toggle-catalogo';
		checkbox.style.marginLeft = '10px';
		checkbox.checked = compress; 

		const label = document.createElement('label');
		label.htmlFor = 'toggle-catalogo';
		label.innerText = 'Compress';
		label.style.marginLeft = '5px';

		// Adiciona o checkbox e label ao grupo de botões internos
		listview.page.inner_toolbar[0].appendChild(checkbox);
		listview.page.inner_toolbar[0].appendChild(label);

		// Evento de mudança do checkbox
		checkbox.addEventListener('change', function () {
			if (this.checked) {
				compress = true;
			} else {
				compress = false;
			}
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
					var ref, cell_range;
					frappe.db.get_doc('Catalogo', doc.name).then(async (doc) => {
						ref = doc.ref;
						cell_range = doc.cell_range;
						await generate(ref, doc.sheet_name, cell_range, compress);
					}).catch((error) => {
						console.error('Error fetching catalog data:', error);
					});
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

async function generate(ref, sheet_name, cell_range, compress = true) {
	const spreadsheet_id = '1Nm6YatjJrugBxM38yaXlIJgLHfVAMCnnMLw83lga5YQ'
	const pais = 'PT';
	const tipoPreco = 'PVP';
	console.log('Generating catalog with ref:', ref, 'sheet_name:', sheet_name, 'cell_range:', cell_range, 'pais:', pais, 'tipoPreco:', tipoPreco);

	frappe.call({
		method: 'erpnext.selling.doctype.catalogo.catalogo.get_catalog',
		args: {
			ref: ref,
			spreadsheet_id: spreadsheet_id,
			sheet_name: sheet_name,
			cell_range: cell_range,
			country: pais,
			price_type: tipoPreco,
			compress: compress 
		},
		callback: function (res) {
			if (res.message) {
				console.log('message:', res.message);
				window.open(res.message, '_blank');
				frappe.msgprint(__('Ficheiro gerado com sucesso!'));
			} else {
				frappe.msgprint(__('No catalogs found or an error occurred.'));
			}
		}
	});
}