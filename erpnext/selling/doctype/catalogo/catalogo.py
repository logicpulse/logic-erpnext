# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
import math
# from frappe.website.website_generator import WebsiteGenerator
import frappe 
import os 
import webbrowser 
from fpdf import FPDF, Align
from dataclasses import dataclass 
from datetime import datetime 
from frappe.model.document import Document


class Catalogo(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		cell_range: DF.Data | None
		image: DF.AttachImage | None
		image_desc: DF.AttachImage | None
		name1: DF.Data | None
		published: DF.Check
		ref: DF.Data | None
		route: DF.Data | None
		sheet_name: DF.Data | None
		website: DF.Data | None
	# end: auto-generated types

	pass


@dataclass
class ProdutModel:
    Sub_Familia: str
    Produto: str
    Ref: str
    URL: str
    Imagem: str
    Pct_PVR: str
    Qt: str
    PVR_PT: str
    PVP_PT: str
    Extra: str 
    PVP_AO: str
    PVP_MZ: str 

@dataclass
class ProdutModelToExcel(ProdutModel):
    Unit_Measure: str

DEFAULT_CATALOG_SPREADSHEET_ID = "1Nm6YatjJrugBxM38yaXlIJgLHfVAMCnnMLw83lga5YQ"
SHORT_SHEETS = ["Gestão de Bibliotecas", "Gestão industrial"]

def get_catalog_spreadsheet():
	"""Abre a planilha do catálogo com a conta de serviço (gspread).
	`spreadsheet_id`: opcional; senão usa `frappe.conf.catalog_spreadsheet_id` ou o ID por defeito.
	"""
	import gspread
	from oauth2client.service_account import ServiceAccountCredentials

	key = DEFAULT_CATALOG_SPREADSHEET_ID
	creds_path = os.path.join(
		frappe.get_app_path("erpnext", "selling", "doctype", "catalogo", "utils", "app_client_secret.json")
	)
	scope = [
		"https://www.googleapis.com/auth/spreadsheets",
		"https://spreadsheets.google.com/feeds",
	]
	creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
	client = gspread.authorize(creds)
	return client.open_by_key(key)

@frappe.whitelist()
def get_catalog(ref: str, spreadsheet_id: str, sheet_name: str, cell_range: str, country: str, price_type: str, compress: bool):
    try:
        # if (True):
        #     return 'http://development.localhost:8000/files/catalogo_access_pt_pvp.pdf'
        # Caminho absoluto para o arquivo de credenciais
        values = get_values(spreadsheet_id, sheet_name, cell_range)
        # print(f"Valores obtidos: {values}")
        
        # Validação dos parâmetros de entrada
        if not values or len(values) < 3:
            frappe.throw("No sufficient data found in the catalog.")

        if not ref or not ref.strip():
            frappe.throw("Catalog reference cannot be empty.")

        valid_countries = {'PT', 'AO', 'MZ'}
        if country not in valid_countries:
            frappe.throw("Invalid country. Use 'PT', 'AO' or 'MZ'.")

        valid_price_types = {'pvr', 'pvp'}
        if price_type.lower() not in valid_price_types:
            frappe.throw("Invalid price type. Use 'PVR' or 'PVP'.")
        
        show_pvr = 'pvr' in price_type.lower()
        file_name = generate_pdf(ref, values, show_pvr, country, compress=compress) 
        # get_url() já inclui host e porta (evita duplicar, ex. :28000:8000)
        full_path = frappe.utils.get_url().rstrip("/") + "/files/" + file_name
        print(f"Catalog generated at: {full_path}")
        return full_path
    except Exception as err:
        frappe.log_error(frappe.get_traceback(), "Catalog Access Error")
        frappe.throw(f"Erro ao acessar o catálogo: {str(err)}")

@frappe.whitelist()
def get_all_catalogs(spreadsheet_id: str, country: str, price_type: str, compress: bool = True):
    datas = [
        {
            "ref": "access",
            "sheet_name": "Gestão de Acessos",
            "cell_range": "E:P"
        },
        {
            "ref": "time",
            "sheet_name": "Gestão de Assiduidade",
            "cell_range": "E:T"
        },
        {
            "ref": "q",
            "sheet_name": "Gestão de Filas de Espera",
            "cell_range": "E:T"
        },
        {
            "ref": "fleet",
            "sheet_name": "Gestão de Frotas",
            "cell_range": "E:T"
        },
        {
            "ref": "pos",
            "sheet_name": "POS",
            "cell_range": "E:T"
        },
        {
            "ref": "library",
            "sheet_name": "Gestão de Bibliotecas",
            "cell_range": "E:T"
        },
        {
            "ref": "factory",
            "sheet_name": "Gestão industrial",
            "cell_range": "E:T"
        }
    ]
    try: 
        # dts = frappe.parse_json(datas)
        doc = FPDF()
        doc = get_cover(country, price_type, doc)  
        doc = get_index(doc) 

        for data in datas:
            ref = data.get("ref")
            sheet_name = data.get("sheet_name")
            cell_range = data.get("cell_range")

            if not ref or not sheet_name or not cell_range:
                continue  # Pula entradas incompletas

            values = get_values(spreadsheet_id, sheet_name, cell_range)
            if not values or len(values) < 3:
                continue  # Pula se não houver dados suficientes

            show_pvr = 'pvr' in price_type.lower() 
            doc = generate_pdf(ref, values, show_pvr, country, doc, compress)
            
        doc = get_back_cover(country, price_type, doc)  # Gera a back cover
 
        file_name = f"catalogo_{country.lower()}_{'pvr' if show_pvr else 'pvp'}_all.pdf" 
        # Salvar na pasta pública de arquivos do site
        public_files_path = frappe.utils.get_site_path("public", "files", file_name)
        doc.output(public_files_path)
		# Retorna a URL completa do PDF para o frontend abrir
        # porta = frappe.conf.webserver_port or 8080 
        # url_base = frappe.utils.get_url()
        # if f":{porta}" not in url_base:
        #     url_base += f":{porta}"
        # full_path = url_base + '/files/' + file_name

        full_path = frappe.utils.get_url().rstrip("/") + "/files/" + file_name

        print(f"Catalog generated at: {full_path}")

        return full_path

        # Salva o PDF final
        # file_name = f"catalogo_{country.lower()}_{'pvr' if show_pvr else 'pvp'}_all.pdf" 
        # pdf_output_path = os.path.join(frappe.get_app_path(
        #     'erpnext', 'selling', 'doctype', 'catalogo', 'utils', file_name 
        # ))
        
        # doc.output(pdf_output_path)  

        # # Abrir o PDF no navegador
        # webbrowser.open_new_tab(frappe.utils.get_url() + '/files/' + pdf_output_path) 
    except Exception as err:
        frappe.log_error(frappe.get_traceback(), "Catalogs Access Error")
        frappe.throw(f"Erro ao acessar os catálogos: {str(err)}")

@frappe.whitelist()
def get_cover(country: str, price_type: str, doc: FPDF = None) -> str | FPDF:
    try:
        # Caminho para a imagem de capa
        root_dir = os.path.join(frappe.get_app_path('erpnext', 'selling', 'doctype', 'catalogo'))
        cover_image_path = os.path.join(root_dir, 'utils', 'catalog_cover.jpg')

        if not os.path.exists(cover_image_path):
            frappe.throw(f"Capa não encontrada!!!")

        font_path = os.path.join(root_dir, 'utils', 'DejaVuSans.ttf')  

        pdf_cover = doc if doc else FPDF()
        pdf_cover.set_page_background(cover_image_path)
        pdf_cover.add_page()
        pdf_cover.add_font('DejaVu', '', font_path, uni=True)
        
        year = datetime.now().year
        title = f'CATÁLOGO {country.upper()} V2.{year}' 
        caption = f'ref {country.upper()} - {price_type.upper()}01{year}'
        description = f'em vigor a partir Fevereiro de {year}'
  
        # Definindo a posição do título
        pdf_cover.set_font("LiberationSans", size=30)
        pdf_cover.set_text_color(255, 255, 255) 
        pdf_cover.set_xy(30, 195)
        pdf_cover.cell(0, 10, title, fill=False, ln=1)

        # Definindo a posição da legenda 
        pdf_cover.set_font_size(16)
        pdf_cover.set_text_color(63, 63, 63)  
        pdf_cover.set_xy(30, 215)
        pdf_cover.cell(0, 8, caption, fill=False, ln=1)

        # Definindo a posição da descrição
        pdf_cover.set_font_size(10)
        pdf_cover.set_xy(30, 223)
        pdf_cover.cell(0, 8, description, fill=False, ln=1)

        file_name = f"catalog_cover.pdf" 
        pdf_output_path = os.path.join(
            frappe.get_app_path('erpnext', 'selling', 'doctype', 'catalogo', 'utils', file_name)
        ) 
        if doc is None: 
            pdf_cover.output(pdf_output_path)  
            webbrowser.open_new_tab(frappe.utils.get_url() + '/files/' + pdf_output_path) 
            return pdf_output_path 
        else:
            return pdf_cover
    except Exception as err:
        frappe.log_error(frappe.get_traceback(), "Cover Access Error")
        frappe.throw(f"Erro ao acessar a capa: {str(err)}")

@frappe.whitelist()
def get_back_cover(country: str, price_type: str, doc: FPDF = None):
    try:
        # Caminho para a imagem de capa
        root_dir = os.path.join(frappe.get_app_path('erpnext', 'selling', 'doctype', 'catalogo'))
        pdf_back_cover = doc if doc else FPDF()

        imagens = [
            os.path.join(root_dir, 'utils', 'condicoes.jpg'),
            os.path.join(root_dir, 'utils', 'contactos.jpg'),
            os.path.join(root_dir, 'utils', 'fim.jpg')
        ]
        for img_path in imagens:
            pdf_back_cover.set_page_background(img_path)
            pdf_back_cover.add_page()
             
        file_name = f"catalog_back_cover.pdf" 
        pdf_output_path = os.path.join(
            frappe.get_app_path('erpnext', 'selling', 'doctype', 'catalogo', 'utils', file_name)
        )
        if doc is None:
            pdf_back_cover.output(pdf_output_path)  
            webbrowser.open_new_tab(frappe.utils.get_url() + '/files/' + pdf_output_path) 
            return pdf_output_path
        else:
            return pdf_back_cover
    except Exception as err:
        frappe.log_error(frappe.get_traceback(), "Back Cover Access Error")
        frappe.throw(f"Erro ao acessar a back cover: {str(err)}")

@frappe.whitelist()
def get_index(doc: FPDF = None):
    root_dir = os.path.join(frappe.get_app_path('erpnext', 'selling', 'doctype', 'catalogo'))
    pdf_index = doc if doc else FPDF()

    img_path = os.path.join(root_dir, 'utils', 'index.jpg')
    pdf_index.set_page_background(img_path)
    pdf_index.add_page()

    if doc is None:
        file_name = f"catalog_index.pdf" 
        pdf_output_path = os.path.join(
            frappe.get_app_path('erpnext', 'selling', 'doctype', 'catalogo', 'utils', file_name)
        )
        pdf_index.output(pdf_output_path)  
        webbrowser.open_new_tab(frappe.utils.get_url() + '/files/' + pdf_output_path) 
        return pdf_output_path
    else:
        return pdf_index

def get_values(spreadsheet_id, sheet_name, cell_range):
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    creds_path = os.path.join(frappe.get_app_path('erpnext', 'selling', 'doctype', 'catalogo', 'utils', 'app_client_secret.json'))

    scope = [ 'https://www.googleapis.com/auth/spreadsheets', 'https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    values = sheet.get(cell_range)
    valuesForm = sheet.get(cell_range, value_render_option='FORMULA')
 
    for i, row in enumerate(valuesForm):
        for j, cell in enumerate(row): 
            if isinstance(cell, str) and cell.startswith('=image'):  
                values[i][j] = valuesForm[i][j]

    return values

@frappe.whitelist()
def synchronize_item_prices_with_spreadsheet(ref: str):
    """ 
    Sincroniza os preços dos itens com a planilha do Google Sheets.
    Args:
        spreadsheet_id: ID da planilha do Google Sheets.
        ref: Referência do item.
    Returns:
        dict: Dicionário com o resultado da sincronização:
            - success: bool: True se a sincronização foi bem-sucedida, False caso contrário.
            - message: str: Mensagem de sucesso ou erro.
    Raises:
        Exception: Se ocorrer um erro ao sincronizar os preços dos itens.
    """
    
    datas = [
        {
            "ref": "access",
            "sheet_name": "Gestão de Acessos",
            "cell_range": "E:P"
        },
        {
            "ref": "time",
            "sheet_name": "Gestão de Assiduidade",
            "cell_range": "E:P"
        },
        {
            "ref": "q",
            "sheet_name": "Gestão de Filas de Espera",
            "cell_range": "E:P"
        },
        {
            "ref": "fleet",
            "sheet_name": "Gestão de Frotas",
            "cell_range": "E:P"
        },
        {
            "ref": "pos",
            "sheet_name": "POS",
            "cell_range": "E:P"
        },
        {
            "ref": "library",
            "sheet_name": "Gestão de Bibliotecas",
            "cell_range": "D:P"
        },
        {
            "ref": "factory",
            "sheet_name": "Gestão industrial",
            "cell_range": "D:R"
        }
    ] 

    doc_name = "Item Price"

    ref_key = (ref or "").strip()
    if not ref_key:
        return {"success": False, "message": "Referência não encontrada"}

    spreadsheet = get_catalog_spreadsheet()
    
    try:
        for data in datas:
            sheet_name = data.get("sheet_name")  
            sheet, col_g = get_catalog_worksheet_and_ref_column(spreadsheet, sheet_name)
            row_number = find_row_number_for_ref(col_g, ref_key)
    
            if row_number is not None:
                print(f'sheet_name: {sheet_name} | row_number: {row_number}') 
                item_price_pt_pvr, item_price_pt, item_price_ao, item_price_mz = get_catalog_item_prices_for_item(ref_key, doc_name)
            
                line = sheet.row_values(row_number, value_render_option="UNFORMATTED_VALUE")
                price_pt_pvr, price_pt, price_ao, price_mz = get_sheet_prices_from_line(line, sheet_name)

                ok, err = validate_sheet_prices(price_pt_pvr, price_pt, price_ao, price_mz)
                if not ok:
                    return {"success": False, "message": err}

                apply_catalog_prices_to_item_prices(
                    doc_name, 
                    [(item_price_pt_pvr, price_pt_pvr), 
                    (item_price_pt, price_pt), 
                    (item_price_ao, price_ao), 
                    (item_price_mz, price_mz)]
                ) 
                return {
                    "success": True,
                    "message": f'Item Price atualizado com sucesso: {ref_key}'
                }
    except Exception as e:
        return {
            "success": False,
            "message": f"Ocorreu um erro ao sincronizar preços do catálogo: {str(e)}"
        }
       
        
    return {
        "success": False,
        "message": f'A referência não foi encontrada: {ref_key}',
    }

def get_catalog_worksheet_and_ref_column(spreadsheet, sheet_name: str):
    sheet = spreadsheet.worksheet(sheet_name)
    ref_col = 7 if sheet_name not in SHORT_SHEETS else 5
    col_values = sheet.col_values(ref_col)
    return sheet, col_values

def find_row_number_for_ref(col_values: list[int | float | str | None], ref_key: str) -> int | None: 
    key = (ref_key or "").strip()
    for i, cell in enumerate(col_values):
        if str(cell).strip() == key:
            return i + 1
    return None

def get_catalog_item_prices_for_item(ref_key: str, doc_name: str = "Item Price"):
    """Carrega os quatro Item Price de venda para o item. Ordem: Standard Selling, Venda PT, AO, MZ."""
    common = {"item_code": ref_key, "selling": 1}
    fields_std = ["price_list_rate", "note", "name"]
    item_price_pt_pvr = frappe.db.get_value(
        doc_name,
        {**common, "price_list": "Standard Selling"},
        fieldname=fields_std,
        as_dict=True,
    )
    item_price_pt = frappe.db.get_value(
        doc_name,
        {**common, "price_list": "Venda PT"},
        fieldname=fields_std,
        as_dict=True,
    )
    item_price_ao = frappe.db.get_value(
        doc_name,
        {**common, "price_list": "Venda AO"},
        fieldname=fields_std,
        as_dict=True,
    )
    item_price_mz = frappe.db.get_value(
        doc_name,
        {**common, "price_list": "Venda MZ"},
        fieldname=["price_list_rate", "item_name"],
        as_dict=True,
    )
    return item_price_pt_pvr, item_price_pt, item_price_ao, item_price_mz

def get_sheet_prices_from_line(line: list, sheet_name: str) -> tuple:
    """Índices das colunas PVR PT, PVP PT, PVP AO, PVP MZ conforme o layout da folha."""
    if sheet_name not in SHORT_SHEETS or sheet_name == "Gestão de Bibliotecas":
        i_pvr, i_pt, i_ao, i_mz = 11, 12, 14, 15
    else:
        i_pvr, i_pt, i_ao, i_mz = 8, 9, 11, 12
    return line[i_pvr], line[i_pt], line[i_ao], line[i_mz]

def apply_catalog_prices_to_item_prices(doc_name: str, pairs: list[tuple[object, object]]):
    """Grava os preços lidos da folha em Item Price."""
    for row, rate in pairs:
        frappe.db.set_value(doc_name, row.name, "price_list_rate", rate)
    return True

def validate_sheet_prices(price_pt_pvr, price_pt, price_ao, price_mz, *, allow_negative=False):
    """Valida os preços lidos da folha antes de gravar em Item Price.
    Devolve (ok: bool, error_message: str | None). Se ok é False, error_message
    descreve o primeiro campo inválido.
    """
    labels = (
        (price_pt_pvr, "PVR PT (planilha)"),
        (price_pt, "PVP PT (planilha)"),
        (price_ao, "PVP AO (planilha)"),
        (price_mz, "PVP MZ (planilha)"),
    )
    for raw, label in labels:
        if raw is None or (isinstance(raw, str) and not str(raw).strip()):
            return False, f"{label}: valor vazio."
        try:
            n = float(raw)
        except (TypeError, ValueError):
            return False, f"{label}: valor não numérico ({raw!r})."
        if not math.isfinite(n):
            return False, f"{label}: valor inválido (não finito)."
        if not allow_negative and n < 0:
            return False, f"{label}: não pode ser negativo ({n})."
    return True, None

def convert_list_to_model(values: list[list[str]]) -> list[ProdutModel]:
    if not values or len(values) < 3:
        return []

    raw_headers = values[1]
    headers = [h if h.strip() else "Extra" for h in raw_headers]

    models = []
    for row in values[2:]:
        # Preenche com string vazia se faltar valor
        row += [""] * (len(headers) - len(row))
        data = dict(zip(headers, row))

        model = ProdutModel(
            Sub_Familia=data.get("Sub-Familia", ""),
            Produto=data.get("Produto", ""),
            Ref=data.get("Ref.", ""),
            URL=data.get("URL", ""),
            Imagem=data.get("Imagem", ""),
            Pct_PVR=data.get("% PVR", ""),
            Qt=data.get("Qt", ""),
            PVR_PT=data.get("PVR PT", ""),
            PVP_PT=data.get("PVP PT", ""),
            Extra=data.get("Extra", ""),
            PVP_AO=data.get("PVP AO", ""),
            PVP_MZ=data.get("PVP MZ", "")
        )
         
        models.append(model)

    return models

def generate_pdf(ref: str, values: list[list[str]], show_pvr: bool, country: str, doc: FPDF = None, compress: bool = True) -> str | FPDF:
    import pandas as pd
    # Caminhos 
    root_dir = os.path.join(frappe.get_app_path('erpnext', 'selling', 'doctype', 'catalogo'))
    font_path_bold = os.path.join(root_dir, 'utils', 'LiberationSans-Bold.ttf') 
    font_path_djv = os.path.join(root_dir, 'utils', 'DejaVuSans.ttf')   
    # font_path_regular = os.path.join(root_dir, 'utils', 'LiberationSans-Regular.ttf') 
    image_background_path = os.path.join(root_dir, ref, f'{ref}.track_background.png')
    header_image_path = os.path.join(root_dir, ref, f'{ref}.track_desc.png')
    # Criação do PDF
    print('Gerando PDF comprimido => ', compress)
    pdf = doc if doc else FPDF()
    pdf.compress = compress
    pdf.set_page_background(image_background_path)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(top=35, left=10, right=10)
    pdf.add_page() 
    page_width = pdf.w 
    pdf.image(header_image_path, x=10, y=30, w=page_width - 20)  
  
    pdf.add_font('LiberationSans', 'B', font_path_bold)
    pdf.add_font('DejaVuSans', '', font_path_djv)
    # pdf.add_font('DejaVu', '', font_path_dejavu, uni=True)

    # pdf.set_y(-15) 
    # pdf.set_font("DejaVu", size=8) 
    # pdf.cell(0, 10, f"Page {pdf.page_no()}/{{nb}}", align="C")

    pdf.set_font("DejaVuSans", size=12)
    
    produts = convert_list_to_model(values) 

    pdf.ln(40) 
    draw_table(pdf, ref, produts, show_pvr, country)

    file_name = f"catalogo_{ref}_{country.lower()}_{'pvr' if show_pvr else 'pvp'}.pdf"
    # Salvar na pasta pública de arquivos do site
    public_files_path = frappe.utils.get_site_path("public", "files", file_name)

    if doc is None:
        # productsToExcel: list[ProdutModelToExcel] = []
        # for produt in produts:
        #     if produt.Ref.startswith("*") or produt.Ref.startswith("#") or not produt.Produto:
        #         produts.remove(produt)

        #     produt.Imagem = clean_image_formula(produt.Imagem)

        #     produt.PVP_PT = re.sub(r'\s+', '', produt.PVP_PT.replace("€", "").replace(',', '.'))
        #     produt.PVR_PT = re.sub(r'\s+', '', produt.PVR_PT.replace("€", "").replace(',', '.'))
        #     produt.PVP_AO = re.sub(r'\s+', '', produt.PVP_AO.replace("Kz", "").replace(',', '.'))
        #     produt.PVP_MZ = re.sub(r'\s+', '', produt.PVP_MZ.replace("MT", "").replace(',', '.'))

        #     unidade_por_sub_familia = {
        #         "Software": "License",
        #         "Hardware": "Unit",
        #         "Serviços": "Service"
        #     }
        #     Unit_Measure = unidade_por_sub_familia.get(produt.Sub_Familia, "Unit")

        #     productsToExcel.append(ProdutModelToExcel(
        #         Sub_Familia=produt.Sub_Familia,
        #         Produto=produt.Produto,
        #         Ref=produt.Ref,
        #         URL=produt.URL,
        #         Imagem=produt.Imagem,
        #         Pct_PVR=produt.Pct_PVR,
        #         Qt=produt.Qt,
        #         PVR_PT=produt.PVR_PT,
        #         PVP_PT=produt.PVP_PT,
        #         Extra=produt.Extra,
        #         PVP_AO=produt.PVP_AO,
        #         PVP_MZ=produt.PVP_MZ,
        #         Unit_Measure=Unit_Measure))

        # df = pd.DataFrame([vars(produto) for produto in productsToExcel])
        # excel_file_name = public_files_path.replace(".pdf", ".xlsx")
        # df.to_excel(excel_file_name, index=False)
  
        print('documento gerado em: ', public_files_path)
        pdf.output(public_files_path)
        # Retorna apenas o nome do arquivo, pois a URL pública é /files/<file_name>
        return file_name
    else:
        return pdf

def get_header_color(ref: str) -> tuple[int, int, int]:
    cores = {
        'access': (119, 31, 73),
        'time': (206, 59, 55),
        'q': (29, 151, 212),
        'fleet': (105, 107, 161),
        'pos': (147, 193, 61),
        'library': (128, 128, 190),
        'factory': (103, 149, 207)
    }
    return cores.get(ref, (0, 0, 0))

def estimate_multicell_height(pdf: FPDF, text: str, width: float, line_height: float = 5) -> float:
    string_width = pdf.get_string_width(text.strip(), True)
    lines = max(1, math.ceil(string_width / width))
    return (lines + 1) * line_height

def draw_table(pdf: FPDF, ref: str, produts: list[ProdutModel], show_pvr: bool, country: str):
    col_widths = [20, 80 if show_pvr else 100, 25]
    col_widths += [25] if show_pvr else []
    col_widths += [25 if show_pvr else 35, 15]

    headers = ["", "Nome", "Referência"]
    if show_pvr:
        headers += ["Uni./ PVR", "Uni./ PVP", "Ver+"]
    else:
        headers += ["Uni./ PVP", "Ver+"]

    def draw_header():
        pdf.set_fill_color(*color)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("LiberationSans", 'B', size=11)
        pdf.set_draw_color(255, 255, 255)
        pdf.set_line_width(0.6) 
        for i, header in enumerate(headers):  
            pdf.cell(col_widths[i], 10, header, border="LB", align=Align.L, fill=True) 
        pdf.set_line_width(0.2) 
        pdf.ln()

    color = get_header_color(ref)
    draw_header()

    pdf.set_font("DejaVuSans", size=10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_draw_color(128, 128, 128)

    for produto in produts:
        # Títulos e Subtítulos
        if produto.Ref.startswith("*") or produto.Ref.startswith("#"):
            fill_color = (47, 47, 47) if produto.Ref.startswith("*") else (128, 128, 128)
            pdf.set_fill_color(*fill_color)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("LiberationSans", style="B", size=11)
            pdf.cell(sum(col_widths), 10, produto.Produto, border=0, fill=True)
            pdf.ln()
            pdf.set_font("DejaVuSans", size=10)
            pdf.set_text_color(0, 0, 0)
            continue

        image_path = clean_image_formula(produto.Imagem)
        temp_y = pdf.get_y()
        temp_x = pdf.get_x()

        # Estimar altura da célula "Nome"
        height_nome = estimate_multicell_height(pdf, produto.Produto, col_widths[1])
        image_height = 20 if image_path.startswith("http") else 10
        line_height = max(height_nome, image_height)

        # Verifica quebra de página
        if pdf.get_y() + line_height > pdf.page_break_trigger:
            pdf.add_page()
            # draw_header()  # Descomente se quiser cabeçalho em cada página
            temp_y = pdf.get_y()
            temp_x = pdf.get_x()

        # Coluna 0: imagem
        if image_path.startswith("http"):
            pdf.image(image_path, x=temp_x, y=temp_y, w=col_widths[0], h=line_height)
        else:
            pdf.set_xy(temp_x, temp_y)
            pdf.cell(col_widths[0], line_height, '', border=0)

        # Coluna 1: Nome (alinhamento horizontal à esquerda, vertical ao topo)
        pdf.set_xy(temp_x + col_widths[0], temp_y)
        pdf.multi_cell(col_widths[1], 5, produto.Produto, border=0, align='L', fill=False)
        # Remove todas as bordas exceto a de baixo
        pdf.line(temp_x + col_widths[0], temp_y + line_height, temp_x + col_widths[0] + col_widths[1], temp_y + line_height)

        # Coluna 2: Referência (alinhamento à esquerda, topo)
        x_pos = temp_x + col_widths[0] + col_widths[1]
        pdf.set_xy(x_pos, temp_y)
        pdf.multi_cell(col_widths[2], 5, produto.Ref, border=0, align='L', fill=False)
        # linha inferior
        pdf.line(x_pos, temp_y + line_height, x_pos + col_widths[2], temp_y + line_height)
        x_pos += col_widths[2]

        # PVR (se aplicável)
        if show_pvr:
            pdf.set_xy(x_pos, temp_y)
            pdf.multi_cell(col_widths[3], 5, produto.Pct_PVR, border=0, align='L', fill=False)
            pdf.line(x_pos, temp_y + line_height, x_pos + col_widths[3], temp_y + line_height)
            x_pos += col_widths[3]

        # PVP conforme país (alinhamento à esquerda, topo)
        pvp = produto.PVP_PT
        if country == 'AO':
            pvp = produto.PVP_AO
        elif country == 'MZ':
            pvp = produto.PVP_MZ

        pdf.set_xy(x_pos, temp_y)
        pdf.multi_cell(col_widths[-2], 5, pvp, border=0, align='L', fill=False)
        pdf.line(x_pos, temp_y + line_height, x_pos + col_widths[-2], temp_y + line_height)
        x_pos += col_widths[-2]

        # Ver+ (alinhamento à esquerda, topo)
        pdf.set_xy(x_pos, temp_y)
        if(produto.URL and produto.URL.strip()):
            text_Color = pdf.text_color
            pdf.set_text_color(*color)
            pdf.multi_cell(col_widths[-1], 5, 'i', border=0, align=Align.C, fill=False, link=produto.URL)
            pdf.set_text_color(text_Color)
        else:
            pdf.multi_cell(col_widths[-1], 5, ' ', border=0, align=Align.C, fill=False)
        pdf.line(x_pos, temp_y + line_height, x_pos + col_widths[-1], temp_y + line_height)

        # Avança linha
        pdf.set_y(temp_y + line_height)

def clean_image_formula(formula: str) -> str: 
    result = formula.replace('=image("', '')
    result = result.replace('"; 1)', '')
    result = result.replace('\n', '')
    result = result.strip()
    
    return result

@frappe.whitelist()
def synchronize_item_prices_with_spreadsheet_by_sheet_name(sheet_name: str):
    """
    Sincroniza os preços dos itens com a planilha do Google Sheets.
    Args:
        sheet_name: Nome da planilha do Google Sheets.
    Returns:
        dict: Dicionário com o resultado da sincronização:
            - success: bool: True se a sincronização foi bem-sucedida, False caso contrário.
            - message: str: Mensagem de sucesso ou erro.
            - updated_count: int: Número de artigos cujos preços foram gravados (só em sucesso).
    Raises:
        Exception: Se ocorrer um erro ao sincronizar os preços dos itens.
    """
    doc_name = "Item Price"
    spreadsheet = get_catalog_spreadsheet()
    sheet, col_g = get_catalog_worksheet_and_ref_column(spreadsheet, sheet_name)

    PRICE_LISTS = ("Standard Selling", "Venda PT", "Venda AO", "Venda MZ")
    _in = ", ".join(["%s"] * len(PRICE_LISTS))
    try:
        rows = frappe.db.sql(
            f"""
            SELECT item_code
            FROM `tabItem Price`
            WHERE selling = 1
              AND price_list IN ({_in})
            GROUP BY item_code
            HAVING COUNT(DISTINCT price_list) = 4
            """,
            PRICE_LISTS,
            as_dict=True,
        )
        mapped_items_codes = [r["item_code"] for r in rows]

        print(f'Rows ➡️ {len(mapped_items_codes)}')
        updated_count = 0
        for item_code in mapped_items_codes:
            row_number = find_row_number_for_ref(col_g, item_code)

            if row_number is None:
                continue

            item_price_pt_pvr, item_price_pt, item_price_ao, item_price_mz = get_catalog_item_prices_for_item(item_code)
            line = sheet.row_values(row_number, value_render_option="UNFORMATTED_VALUE")
            price_pt_pvr, price_pt, price_ao, price_mz = get_sheet_prices_from_line(line, sheet_name)

            ok, err = validate_sheet_prices(price_pt_pvr, price_pt, price_ao, price_mz)
            if not ok:
                return {"success": False, "message": f"{item_code}: {err}"}

            apply_catalog_prices_to_item_prices(
                doc_name,
                [
                    (item_price_pt_pvr, price_pt_pvr),
                    (item_price_pt, price_pt),
                    (item_price_ao, price_ao),
                    (item_price_mz, price_mz),
                ],
            )
            updated_count += 1

        return {
            "success": True,
            "updated_count": updated_count,
            "message": f"Preços atualizados para {updated_count} artigo(s).",
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Ocorreu um erro ao sincronizar preços do catálogo: {str(e)}"
        }