
frappe.pages['gerador-de-catalogos'].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		single_column: true
	});
	//let $btn = page.set_primary_action('New', () => show(), 'octicon octicon-plus')
	page.add_action_item('access', async () => await generate('access', 'Gestão de Acessos', 'E:P'));
	page.add_action_item('time', async () => await generate('time', 'Gestão de Assiduidade', 'E:T'));
	page.add_action_item('q.track', async () => await generate('Gestão de Filas de Espera', 'E:T'));
	page.add_action_item('fleet', async () => await generate('Gestão de Frotas', 'E:T'));
	page.add_action_item('logicpos', async () => await generate('POS', 'E:T'));
	page.add_action_item('library', async () => await generate('Gestão de Bibliotecas', 'E:T'));
	page.add_action_item('factory', async () => await generate('Gestão industrial', 'E:T'));
	page.add_action_item('cover', async () => await generate('Gestão de Acessos', 'E:P'));
	page.add_action_item('back cover', async () => await generate('Gestão de Acessos', 'E:P'));
	page.add_action_item('index', async () => await generate('Gestão de Acessos', 'E:P'));
	//page.add_menu_item('Send Email', () => open_email_dialog())

	$(frappe.render_template('gerador_de_catalogos', {})).appendTo(page.body);
}

async function generate(ref, sheet_name, cell_range) {
	const spreadsheet_id = '1Nm6YatjJrugBxM38yaXlIJgLHfVAMCnnMLw83lga5YQ'
	console.log('catalog_access');
	const pais = document.getElementById('pais') ? document.getElementById('pais').value : null;
	const tipoPreco = document.getElementById('tipo_preco') ? document.getElementById('tipo_preco').value : null;

	console.log('Pais selecionado:', pais);
	console.log('Tipo de preço selecionado:', tipoPreco);

	frappe.call({
		method: 'erpnext.test.page.gerador_de_catalogos.gerador_de_catalogos.catalog_access',
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
				console.log('res:', res);
				console.log('message:', res.message);

				// window.open(res.message, '_blank');
			}
			// if (resp.message) {
			// 	console.log(resp.message);
			// 	// faça algo com os dados
			// }
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