
frappe.pages['gerador-de-catalogos'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		single_column: true
	});
	//let $btn = page.set_primary_action('New', () => show(), 'octicon octicon-plus')
	page.add_action_item('access', async () => await access('1Nm6YatjJrugBxM38yaXlIJgLHfVAMCnnMLw83lga5YQ'));
	page.add_action_item('time', () => delete_items());
	page.add_action_item('q.track', () => delete_items());
	page.add_action_item('fleet', () => delete_items());
	page.add_action_item('logicpos', () => delete_items());
	page.add_action_item('library', () => delete_items());
	page.add_action_item('factory', () => delete_items());
	page.add_action_item('cover', () => delete_items());
	page.add_action_item('back cover', () => delete_items());
	page.add_action_item('index', () => delete_items());
	//page.add_menu_item('Send Email', () => open_email_dialog())

	$(frappe.render_template('gerador_de_catalogos', {})).appendTo(page.body);
}

async function access(spreadsheetId) {
	console.log('catalog_access');
	const pais = document.getElementById('pais') ? document.getElementById('pais').value : null;
	const tipoPreco = document.getElementById('tipo_preco') ? document.getElementById('tipo_preco').value : null;

	console.log('Pais selecionado:', pais);
	console.log('Tipo de preço selecionado:', tipoPreco);

	frappe.call({
		method: 'erpnext.test.page.gerador_de_catalogos.gerador_de_catalogos.catalog_access',
		args: {
			spreadsheet_id: spreadsheetId,
			sheet_name: 'Gestão de Acessos',
			cell_range: 'E:P' // ou 'E1:P100' por exemplo
		},
		callback: function (r) {
			if (r.message) {
				console.log(r.message);
				// faça algo com os dados
			}
		}
	});
}

function show() {
	alert('clicked');
}

function showTab(tabId) {
	console.log('showTab', tabId);

	// Remove 'active' das abas
	document.querySelectorAll('.nav-link').forEach(el => el.classList.remove('active'));
	// Adiciona 'active' à aba clicada
	document.getElementById('tab-' + tabId).classList.add('active');

	// Esconde todos os conteúdos das abas
	document.querySelectorAll('.tab-pane').forEach(el => {
		el.classList.remove('show', 'active');
	});
	// Mostra o conteúdo da aba selecionada
	document.getElementById(tabId).classList.add('show', 'active');
}