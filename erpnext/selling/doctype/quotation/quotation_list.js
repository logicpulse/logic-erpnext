frappe.listview_settings["Quotation"] = {
	add_fields: ["customer_name", "base_grand_total", "status", "company", "currency", "valid_till"],

	onload: function (listview) {
		if (listview.page.fields_dict.quotation_to) {
			listview.page.fields_dict.quotation_to.get_query = function () {
				return {
					filters: {
						name: ["in", ["Customer", "Lead"]],
					},
				};
			};
		}

		if (frappe.model.can_create("Sales Order")) {
			listview.page.add_action_item(__("Sales Order"), () => {
				erpnext.bulk_transaction_processing.create(listview, "Quotation", "Sales Order");
			});
		}

		if (frappe.model.can_create("Sales Invoice")) {
			listview.page.add_action_item(__("Sales Invoice"), () => {
				erpnext.bulk_transaction_processing.create(listview, "Quotation", "Sales Invoice");
			});
		}
	},

	dropdown_button: {
		get_label: __("Dropdown"),
		buttons: [
			{
				get_label: __("Imprimir"),
				show: async function (doc) {
					const quotation = await frappe.db.get_doc('Quotation', doc.name);
					return quotation.pos_id ? true : false;
				},
				get_description: function (doc) {
					return "Imprimir " + doc.name; 
				},
				action: async function (doc) { 
					const quotation = await frappe.db.get_doc('Quotation', doc.name);
					const params = new URLSearchParams({
						document_id: quotation.pos_id
					}).toString();


					window.open(
						`/api/method/erpnext.selling.doctype.quotation.quotation.generate_pdf_document?${params}`,
						"_blank"
					);
				}
			}
		]
	},

	get_indicator: function (doc) {
		if (doc.status === "Open") {
			return [__("Open"), "orange", "status,=,Open"];
		} else if (doc.status === "Partially Ordered") {
			return [__("Partially Ordered"), "yellow", "status,=,Partially Ordered"];
		} else if (doc.status === "Ordered") {
			return [__("Ordered"), "green", "status,=,Ordered"];
		} else if (doc.status === "Lost") {
			return [__("Lost"), "gray", "status,=,Lost"];
		} else if (doc.status === "Expired") {
			return [__("Expired"), "gray", "status,=,Expired"];
		}
	},
};
