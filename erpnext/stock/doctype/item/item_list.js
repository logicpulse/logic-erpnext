// const { on } = require("ace-builds-internal/config");

frappe.listview_settings["Item"] = {
	onload: function (listview) {
		listview.page.add_inner_button(__('Completa'), async function (listview) {
			await sync_with_google_sheet();
		}, __('Sync'));
		listview.page.add_inner_button(__('Gestão de Acessos'), async function (listview) {
			await sync_with_google_sheet_single("access");
		}, __('Sync'));
		listview.page.add_inner_button(__('Gestão de Assiduidade'), async function (listview) {
			await sync_with_google_sheet_single("time");
		}, __('Sync'));
		listview.page.add_inner_button(__('Gestão de Filas de Espera'), async function (listview) {
			await sync_with_google_sheet_single("q");
		}, __('Sync'));
		listview.page.add_inner_button(__('Gestão de Frotas'), async function (listview) {
			await sync_with_google_sheet_single("fleet");
		}, __('Sync'));
		listview.page.add_inner_button(__('POS'), async function (listview) {
			await sync_with_google_sheet_single("pos");
		}, __('Sync'));
		listview.page.add_inner_button(__('Gestão de Bibliotecas'), async function (listview) {
			await sync_with_google_sheet_single("library");
		}, __('Sync'));
		listview.page.add_inner_button(__('Gestão industrial'), async function (listview) {
			await sync_with_google_sheet_single("factory");
		}, __('Sync'));
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

async function sync_with_google_sheet() {
	// frappe.show_progress('Loading..', 0, 100, 'Please wait');
	const { message } = await frappe.call({
		method: 'logicposintegration.logicpos_integration.spreadsheet.load.sync_datas',
		args: {},
		freeze: true,
		freeze_message: "Sincronizando itens com Google Sheets..."
	});

	if (message.success) {
		frappe.msgprint({
			title: "Itens sincronizados com sucesso a partir do Google Sheets",
			message: `${message.message}`,
			indicator: "green"
		}); 
		console.log('datas => ', message.message);
		// listview.refresh();
	} 
}

async function sync_with_google_sheet_single(ref) {
	try {  
		const { message } = await frappe.call({
			method: 'logicposintegration.logicpos_integration.spreadsheet.load.sync_single_sheet_data',
			args: { ref },
			freeze: true,
			freeze_message: `Sincronizando ${ref} com Google Sheets...`
		});

		if (!message.success) {
			throw new Error(message.message || "Erro desconhecido");
		}

		frappe.show_alert({
			message: `${ref} sincronizado com sucesso!\n${message.message}`,
			indicator: "green"
		});

		if (window.cur_list?.refresh) {
			cur_list.refresh();
		}
	} catch (error) {
		console.error(error);
		frappe.msgprint({
			title: "Erro",
			message: `Ocorreu um erro ao sincronizar ${ref} a partir do Google Sheets.\n${error.message}`,
			indicator: "red"
		});
	}
}