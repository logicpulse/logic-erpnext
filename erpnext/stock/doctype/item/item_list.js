frappe.listview_settings["Item"] = {
	onload: function (listview) {
		frm.add_custom_button('Sincronizar', async function () {
			await show_form(frm);
		});
		// listview.page.add_inner_button(__('Completa'), async function (listview) {
		// 	await sync_with_google_sheet();
		// }, __('Sync'));
		// listview.page.add_inner_button(__('Gestão de Acessos'), async function (listview) {
		// 	await sync_with_google_sheet_single("access");
		// }, __('Sync'));
		// listview.page.add_inner_button(__('Gestão de Assiduidade'), async function (listview) {
		// 	await sync_with_google_sheet_single("time");
		// }, __('Sync'));
		// listview.page.add_inner_button(__('Gestão de Filas de Espera'), async function (listview) {
		// 	await sync_with_google_sheet_single("q");
		// }, __('Sync'));
		// listview.page.add_inner_button(__('Gestão de Frotas'), async function (listview) {
		// 	await sync_with_google_sheet_single("fleet");
		// }, __('Sync'));
		// listview.page.add_inner_button(__('POS'), async function (listview) {
		// 	await sync_with_google_sheet_single("pos");
		// }, __('Sync'));
		// listview.page.add_inner_button(__('Gestão de Bibliotecas'), async function (listview) {
		// 	await sync_with_google_sheet_single("library");
		// }, __('Sync'));
		// listview.page.add_inner_button(__('Gestão industrial'), async function (listview) {
		// 	await sync_with_google_sheet_single("factory");
		// }, __('Sync'));
	},
	add_fields: [
		"item_name",
		"stock_uom",
		"item_group",
		"image",
		"has_variants",
		"end_of_life",
		"disabled",
		"variant_of",
	],
	filters: [["disabled", "=", "0"]],

	get_indicator: function (doc) {
		if (doc.disabled) {
			return [__("Disabled"), "grey", "disabled,=,Yes"];
		} else if (doc.end_of_life && doc.end_of_life < frappe.datetime.get_today()) {
			return [__("Expired"), "grey", "end_of_life,<,Today"];
		} else if (doc.has_variants) {
			return [__("Template"), "orange", "has_variants,=,Yes"];
		} else if (doc.variant_of) {
			return [__("Variant"), "green", "variant_of,=," + doc.variant_of];
		}
	},

	reports: [
		{
			name: "Stock Summary",
			route: "/app/stock-balance",
		},
		{
			name: "Stock Ledger",
			report_type: "Script Report",
		},
		{
			name: "Stock Balance",
			report_type: "Script Report",
		},
		{
			name: "Stock Projected Qty",
			report_type: "Script Report",
		},
	],
};

frappe.help.youtube_id["Item"] = "qXaEwld4_Ps";


async function show_form(frm) {
	let d = new frappe.ui.Dialog({
		title: 'Sincronizar preços',
		fields: [
			{
				label: 'Sincronização Completa?',
				fieldname: 'is_complete',
				fieldtype: 'Check',
				default: 0,
			},
			{
				label: 'Grupo de itens',
				fieldname: 'sheet_name',
				fieldtype: 'Select',
				options: [
					"Gestão de Acessos",
					"Gestão de Assiduidade",
					"Gestão de Filas de Espera",
					"Gestão de Frotas",
					"POS",
					"Gestão de Bibliotecas",
					"Gestão industrial",
				],
				depends_on: 'eval:doc.is_complete == 1',
			},
		],
		size: 'small', // small, large, extra-large 
		primary_action_label: 'Sincronizar',
		primary_action: async function (values) {
			d.hide();
			frappe.show_progress(`Sincronizando preços para o grupo de itens: ${sheet_name}...`, 70, 100, 'Por favor, aguarde');
			await sync_prices_with_spreadsheet_sheet(values);
			frappe.hide_progress();
		}
	});
	
	d.show();
}

async function sync_prices_with_spreadsheet_sheet(values) {
	let { is_complete, sheet_name } = values;

	try {
		let message = '';
		if (is_complete) {
			// message = await frappe.call({
			// 	method: "erpnext.selling.doctype.catalogo.catalogo.synchronize_item_prices_with_spreadsheet",
			// 	args: { 
			// 		ref: frm.doc.item_code, 
			// 	},
			// 	freeze: true,
			// 	freeze_message: `Sincronizando item ${frm.doc.item_code} com Google Sheets...`
			// });
		} else {
			message = await frappe.call({
				method: "erpnext.selling.doctype.catalogo.catalogo.synchronize_item_prices_with_spreadsheet_by_sheet_name",
				args: { 
					sheet_name, 
				},
				freeze: false
			});
		} 
		 
		if (message.success) {
			frappe.show_alert({
				title: "Sucesso",
				message: `${message.message}`,
				indicator: "green"
			});
		} else {
			frappe.msgprint({
				title: "Erro",
				message: `Ocorreu um erro ao sincronizar item ${frm.doc.item_code} a partir do Google Sheets! ${message.message}`,
				indicator: "red"
			});
		}
	} catch (error) {
		console.error(error);
		frappe.show_alert({
			title: "Erro",
			message: `Ocorreu um erro ao sincronizar item ${frm.doc.item_code} a partir do Google Sheets! ${error.message}`,
			indicator: "red"
		});
	} 
}