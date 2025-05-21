frappe.pages['gerador-de-catalogos'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Gerador de Catalogos',
		single_column: true
	});
	let $btn = page.set_primary_action('New', () => show(), 'octicon octicon-plus')



	$(frappe.render_template('gerador_de_catalogos', {})).appendTo(page.body);
	//set up our empty datatable
	// let el = document.querySelector('.layout-main-section')
	// let button_formatter = (value) => `<button onclick="alert('This is ${value}')">Action!</button>`
	// let columns = ['Name', 'Territory', 'Account Manager',
	// 	{ name: "Action Button", focusable: false, format: button_formatter }]
	// let datatable = new frappe.DataTable(el, { columns: columns, data: [], layout: "fluid" });

	// //use regular ajax api methods to fetch document data, then refresh
	// frappe.db.get_list("Customer",
	// 	{ fields: ['customer_name', 'territory', 'account_manager', 'name'] }
	// ).then((r) => {
	// 	let data = r.map(Object.values)
	// 	datatable.refresh(data, columns)
	// })
}

function show() {
	alert('clicked');

}