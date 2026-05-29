frappe.pages['proposta'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Nova Proposta',
		single_column: true
	});

	frappe.breadcrumbs.add("Selling");
	wrapper.proposta_form = new PropostaForm(wrapper);
}


class PropostaForm {
	constructor(wrapper) {
		this.wrapper = wrapper;
		this.page = wrapper.page;
		this.item_rows = [];
		this.setup();
	}

	setup() {
		const me = this;

		this.$container = $(`
			<div class="proposta-form">
				<div class="row mt-4">
					<div class="col-md-6"><div class="customer-field"></div></div>
					<div class="col-md-3"><div class="artigo-field"></div></div>
					<div class="col-md-3"><div class="moeda-field"></div></div>
				</div>
				<hr class="my-4">
				<div class="items-header d-flex justify-content-between align-items-center flex-wrap">
					<h5 class="mb-0">${__("Itens")}</h5>
					<span class="text-muted small moeda-hint"></span>
				</div>
				<div class="table-responsive proposta-items-table-wrap mt-2">
					<table class="table table-bordered table-condensed proposta-items-table">
						<thead>
							<tr>
								<th style="min-width: 150px">${__("Artigo (Item)")}</th>
								<th style="width: 100px">${__("Quantidade")}</th>
								<th style="width: 145px">${__("Preço unitário")}</th>
								<th style="width: 145px">${__("Total")}</th>
								<th style="width: 48px"></th>
							</tr>
						</thead>
						<tbody class="items-tbody"></tbody>
						<tfoot>
							<tr class="proposta-add-row">
								<td colspan="5">
									<button type="button" class="btn btn-default btn-sm btn-add-item">
										${__("Adicionar linha")}
									</button>
								</td>
							</tr>
						</tfoot>
					</table>
				</div>
			</div>
		`);
		$('<div class="row proposta-main-row justify-content-center"></div>')
			.appendTo(this.page.main)
			.append($('<div class="col-md-6 col-lg-6"></div>').append(this.$container));

		this.customer_field = frappe.ui.form.make_control({
			df: {
				label: __("Cliente"),
				fieldtype: "Link",
				options: "Customer",
				reqd: 1,
				placeholder: __("Pesquisar cliente"),
			},
			parent: this.$container.find(".customer-field"),
			render_input: true,
		});

		this.artigo_field = frappe.ui.form.make_control({
			df: {
				label: __("Artigo"),
				fieldtype: "Select",
				options: ["q.track", "q.track.survey", "time.track", "access.track", "fatory.track", "library.track", "fleet.track", "logicPOS", "others"].join("\n"),
				reqd: 1,
			},
			parent: this.$container.find(".artigo-field"),
			render_input: true,
		});

		this.moeda_field = frappe.ui.form.make_control({
			df: {
				label: __("Moeda"),
				fieldtype: "Select",
				options: ["AOA", "EUR", "MZN"].join("\n"),
				default: "AOA",
				reqd: 1,
				change: () => {
					me.update_moeda_hint();
					me.refresh_all_item_rates();
				},
			},
			parent: this.$container.find(".moeda-field"),
			render_input: true,
		});

		this.update_moeda_hint();

		this.$container.find(".btn-add-item").on("click", () => this.add_item_row());

		this.page.set_primary_action(__("Gerar proposta"), () => me.submit());

		this.add_item_row();
	}

	update_moeda_hint() {
		const c = this.moeda_field.get_value() || "AOA";
		this.$container.find(".moeda-hint").text(__("Preços em {0}", [c]));
	}

	get_currency() {
		return this.moeda_field.get_value() || "AOA";
	}

	/** Preço conforme moeda + grupo, nome e unidade de stock do Item */
	async fetch_item_details(item_code) {
		const currency = this.get_currency();
		const fields = [
			"item_group",
			"item_name",
			"stock_uom",
			"image"
		];
		const item = (await frappe.db.get_value("Item", item_code, fields)).message;
		let rate = 0;
		if (currency === "EUR")
			rate = await this.fetch_item_price(item_code, "PVP-PT");
		else if (currency === "AOA")
			rate = await this.fetch_item_price(item_code, "PVP-AO");
		else if (currency === "MZN")
			rate = await this.fetch_item_price(item_code, "PVP-MZ");

		return {
			rate,
			item_group: item.item_group || "",
			item_name: item.item_name || "",
			stock_uom: item.stock_uom || "",
			image: item.image || ""
		};
	}

	async fetch_item_price(item_code, price_list) {
		const item_price = (await frappe.db.get_value(
			"Item Price",
			{ "item_code": item_code, "selling": 1, "price_list": price_list },
			"price_list_rate"
		)).message;
		return item_price.price_list_rate;
	}

	refresh_all_item_rates() {
		this.item_rows.forEach(async (row) => {
			const code = row.item_field.get_value();
			if (!code) {
				this.update_row_total(row);
				return;
			}
			await this.fetch_item_details(code).then((d) => {
				row.item_meta = {
					item_group: d.item_group,
					item_name: d.item_name,
					stock_uom: d.stock_uom,
					image: d.image
				};
				row.rate_field.set_value(d.rate);
				this.update_row_total(row);
			});
		});
	}

	on_item_link_change(row) {
		const code = row.item_field.get_value();
		if (!code) {
			row.item_meta = null;
			row.rate_field.set_value("");
			this.update_row_total(row);
			return;
		}
		row.qty_field.set_value(1);
		this.fetch_item_details(code).then((d) => {
			row.item_meta = {
				item_group: d.item_group,
				item_name: d.item_name,
				stock_uom: d.stock_uom,
				image: d.image
			};
			row.rate_field.set_value(d.rate);
			this.update_row_total(row);
		});
	}

	update_row_total(row) {
		const qty = flt(row.qty_field.get_value());
		const rate = flt(row.rate_field.get_value());
		const total = qty * rate;
		const currency = this.get_currency();
		const text = format_currency(total, currency);
		row.$tr.find(".line-total-cell").text(text);
	}

	add_item_row() {
		const me = this;
		const $tbody = this.$container.find(".items-tbody");

		const $tr = $(`
			<tr>
				<td class="item-cell"></td>
				<td class="qty-cell"></td>
				<td class="rate-cell"></td>
				<td class="line-total-cell text-right align-middle"></td>
				<td class="text-center align-middle">
					<button type="button" class="btn btn-link btn-xs text-danger btn-remove-row" title="${__(
			"Remover linha"
		)}">
						<i class="fa fa-trash"></i>
					</button>
				</td>
			</tr>
		`).appendTo($tbody);

		const item_field = frappe.ui.form.make_control({
			df: {
				fieldtype: "Link",
				options: "Item",
				label: __("Item"),
				reqd: 1,
				placeholder: __("Selecionar artigo"),
				get_query: function () {
					return { filters: { disabled: 0 } };
				},
			},
			parent: $tr.find(".item-cell"),
			render_input: true,
		});
		item_field.toggle_label(false);

		const qty_field = frappe.ui.form.make_control({
			df: {
				fieldtype: "Float",
				label: __("Quantidade"),
				default: 1,
				precision: 1,
			},
			parent: $tr.find(".qty-cell"),
			render_input: true,
		});
		qty_field.toggle_label(false);

		const rate_field = frappe.ui.form.make_control({
			df: {
				fieldtype: "Float",
				label: __("Preço"),
				precision: 2,
			},
			parent: $tr.find(".rate-cell"),
			render_input: true,
		});
		rate_field.toggle_label(false);

		const row = { $tr, item_field, qty_field, rate_field, item_meta: null };
		this.item_rows.push(row);

		item_field.df.change = function () {
			me.on_item_link_change(row);
		};
		qty_field.df.change = function () {
			me.update_row_total(row);
		};
		rate_field.df.change = function () {
			me.update_row_total(row);
		};

		this.update_row_total(row);

		$tr.find(".btn-remove-row").on("click", () => this.remove_item_row(row));
	}

	remove_item_row(row) {
		if (this.item_rows.length <= 1) {
			frappe.show_alert({
				message: __("É necessário pelo menos uma linha de itens."),
				indicator: "orange",
			});
			return;
		}
		this.item_rows = this.item_rows.filter((r) => r !== row);
		row.$tr.remove();
	}

	get_data() {
		// console.log("this.item_rows", this.item_rows);
		return {
			customer: this.customer_field.get_value(),
			artigo: this.artigo_field.get_value(),
			currency: this.moeda_field.get_value() || "AOA",
			items: this.item_rows.map((r) => {
				const qty = flt(r.qty_field.get_value());
				const rate = flt(r.rate_field.get_value());
				// console.log('r:', r);
				const m = r.item_meta || {};
				return {
					item_code: r.item_field.get_value(),
					item_name: m.item_name || "",
					item_group: m.item_group || "",
					stock_uom: m.stock_uom || "",
					image: m.image || "",
					qty,
					rate,
					amount: qty * rate,
				};
			}),
		};
	}

	submit() {
		const d = this.get_data();
		console.log('d:', d);

		if (!d.customer) {
			frappe.msgprint(__("Selecione um cliente."));
			return;
		}
		if (!d.artigo) {
			frappe.msgprint(__("Selecione o tipo de artigo."));
			return;
		}
		if (!d.currency) {
			frappe.msgprint(__("Selecione a moeda."));
			return;
		}

		const bad = d.items.filter(
			(i) =>
				!i.item_code ||
				!i.qty ||
				i.qty <= 0 ||
				i.rate === null ||
				i.rate === undefined ||
				isNaN(i.rate)
		);
		if (bad.length) {
			frappe.msgprint(
				__(
					"Preencha artigo, quantidade (> 0) e preço em todas as linhas."
				)
			);
			return;
		}

		frappe.call({
			method: "logicposintegration.logicpos_integration.proposals.generate.generate_proposal",
			freeze: true,
			freeze_message: "A gerar a proposta comercial...",
			args: {
				article: d.artigo,
				client: d.customer,
				currency: d.currency,
				items: d.items,
			},
			callback: function (res) {
				if (res.message) {
					window.open(res.message, '_blank');
					frappe.msgprint(__('Proposta comercial gerada com sucesso!'));
				} else {
					frappe.msgprint(__('Erro ao gerar a proposta comercial.'));
				}
			},
		});
	}
}
