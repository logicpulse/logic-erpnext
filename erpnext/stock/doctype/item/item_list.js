frappe.listview_settings["Item"] = {
	onload: function (listview) {
		listview.page.set_secondary_action('Sincronizar', async function () {
			await show_form();
		}, "octicon octicon-sync");
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


async function show_form() {
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
				depends_on: 'eval:doc.is_complete == 0'
			},
		],
		size: 'small', // small, large, extra-large 
		primary_action_label: 'Sincronizar',
		primary_action: async function (values) {
			console.log(values);
			if (values.is_complete == 0 && !values.sheet_name) {
				frappe.show_alert({
					title: "Erro",
					message: "Selecione um grupo de itens",
					indicator: "red"
				});
				return;
			}
			d.hide();
			const title = __("A Sincronizar preços...");
			const max_before_done = 95; // nunca 100 até terminar
			const start = Date.now();
			// estimativa opcional (ms); a barra aproxima-se disso mas não passa de max_before_done
			const estimated_ms = 120_000;
			frappe.show_progress(title, 0, 100, "Por favor, aguarde");
			const tick = setInterval(() => {
				const elapsed = Date.now() - start;
				const pct = Math.min(
					max_before_done,
					Math.floor((elapsed / estimated_ms) * 100)
				);
				frappe.show_progress(title, pct, 100, __("Por favor, aguarde"));
			}, 300);
			try {
				await sync_prices_with_spreadsheet_sheet(values);
				frappe.show_progress(title, 100, 100, "Concluído");
				setTimeout(() => frappe.hide_progress(), 400);
			} finally {
				clearInterval(tick);
			}
			// d.hide();
			// frappe.show_progress(`Sincronizando preços...`, 70, 100, 'Por favor, aguarde');
			// await sync_prices_with_spreadsheet_sheet(values);
			// frappe.hide_progress();
		}
	});

	d.show();
}

async function sync_prices_with_spreadsheet_sheet(values) {
	let { is_complete, sheet_name } = values;

	try {
		let response = '';
		if (is_complete == 1) {
			response = await frappe.call({
				method: "erpnext.selling.doctype.catalogo.catalogo.synchronize_all_item_prices_with_spreadsheet",
				freeze: false
			});
		} else {
			response = await frappe.call({
				method: "erpnext.selling.doctype.catalogo.catalogo.synchronize_item_prices_with_spreadsheet_by_sheet_name",
				args: {
					sheet_name,
				},
				freeze: false
			});
		}
		console.log(response.message);
		if (response.message.success) {
			frappe.show_alert({
				title: "Sucesso",
				message: `${response.message.message}`,
				indicator: "green"
			});
		} else {
			frappe.msgprint({
				title: "Erro",
				message: `Ocorreu um erro ao sincronizar preços! ${response.message.message}`,
				indicator: "red"
			});
		}
	} catch (error) {
		console.error(error);
		frappe.show_alert({
			title: "Erro",
			message: `Ocorreu um erro ao sincronizar preços! ${error.message}`,
			indicator: "red"
		});
	}
}