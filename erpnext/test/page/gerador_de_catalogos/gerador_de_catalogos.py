import frappe
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os 
import webbrowser 
from fpdf import FPDF, Align
from dataclasses import dataclass 
from datetime import datetime

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

@frappe.whitelist()
def get_catalog(ref: str, spreadsheet_id: str, sheet_name: str, cell_range: str, country: str, price_type: str):
    try:
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
        file_name = generate_pdf(ref, values, show_pvr, country)

        # Abrir o PDF no navegador
        webbrowser.open_new_tab(frappe.utils.get_url() + '/files/' + file_name) 
        return file_name
    except Exception as err:
        frappe.log_error(frappe.get_traceback(), "Catalog Access Error")
        frappe.throw(f"Erro ao acessar o catálogo: {str(err)}")

@frappe.whitelist()
def get_cover(country: str, price_type: str):
    try:
        # Caminho para a imagem de capa
        root_dir = os.path.join(frappe.get_app_path('erpnext', 'test', 'page', 'gerador_de_catalogos'))
        cover_image_path = os.path.join(root_dir, 'utils', 'catalog_cover.jpg')

        if not os.path.exists(cover_image_path):
            frappe.throw(f"Capa não encontrada!!!")

        font_path = os.path.join(root_dir, 'utils', 'DejaVuSans.ttf')  

        pdf_cover = FPDF()
        pdf_cover.set_page_background(cover_image_path)
        pdf_cover.add_page()
        pdf_cover.add_font('DejaVu', '', font_path, uni=True)
        
        year = datetime.now().year
        title = f'CATÁLOGO {country.upper()} V2.{year}' 
        caption = f'ref {country.upper()} - {price_type.upper()}01{year}'
        description = f'em vigor a partir Fevereiro de {year}'
  
        # Definindo a posição do título
        pdf_cover.set_font("DejaVu", size=30)
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
            frappe.get_app_path('erpnext', 'test', 'page', 'gerador_de_catalogos', 'utils', file_name)
        ) 
        pdf_cover.output(pdf_output_path)  
        webbrowser.open_new_tab(frappe.utils.get_url() + '/files/' + pdf_output_path) 
        return pdf_output_path 
    except Exception as err:
        frappe.log_error(frappe.get_traceback(), "Cover Access Error")
        frappe.throw(f"Erro ao acessar a capa: {str(err)}")

def get_values(spreadsheet_id, sheet_name, cell_range):
    creds_path = os.path.join(frappe.get_app_path('erpnext', 'test', 'page', 'gerador_de_catalogos', 'utils', 'app_client_secret.json'))

    scope = [ 'https://www.googleapis.com/auth/spreadsheets', 'https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    values = sheet.get(cell_range)
    return values

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

def generate_pdf(ref: str, values: list[list[str]], show_pvr: bool, country: str) -> str:
    # Caminhos 
    root_dir = os.path.join(frappe.get_app_path('erpnext', 'test', 'page', 'gerador_de_catalogos'))
    font_path = os.path.join(root_dir, 'utils', 'DejaVuSans.ttf') 
    image_background_path = os.path.join(root_dir, ref, f'{ref}.track_background.png')
    header_image_path = os.path.join(root_dir, ref, f'{ref}.track_desc.png')
    # Criação do PDF
    pdf = FPDF()
    pdf.set_page_background(image_background_path)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(top=35, left=10, right=10)
    pdf.add_page() 
    page_width = pdf.w 
    pdf.image(header_image_path, x=10, y=30, w=page_width - 20)  
  
    pdf.add_font('DejaVu', '', font_path, uni=True)

    # pdf.set_y(-15) 
    # pdf.set_font("DejaVu", size=8) 
    # pdf.cell(0, 10, f"Page {pdf.page_no()}/{{nb}}", align="C")

    pdf.set_font("DejaVu", size=12)
    
    produts = convert_list_to_model(values) 

    pdf.ln(40) 
    draw_table(pdf, ref, produts, show_pvr, country)

    file_name = f"catalogo_{ref}_{country.lower()}_{'pvr' if show_pvr else 'pvp'}.pdf" 
    pdf_output_path = os.path.join(
        frappe.get_app_path(
            'erpnext', 'test', 'page', 'gerador_de_catalogos', ref,
            file_name
        )
    )
     
    pdf.output(pdf_output_path)  
    return pdf_output_path 

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

def draw_table(pdf: FPDF, ref: str, produts: list[ProdutModel], show_pvr: bool, country: str):
    # Definições de larguras das colunas
    col_widths = [20, 80 if show_pvr else 100, 25]
    col_widths += [25] if show_pvr else []
    col_widths += [25 if show_pvr else 35, 15]

    # Cabeçalho
    headers = ["", "Nome", "Referência"]
    if show_pvr:
        headers += ["Uni./ PVR", "Uni./ PVP", "Ver+"]
    else:
        headers += ["Uni./ PVP", "Ver+"]

    # Estilos
    color = get_header_color(ref)
    pdf.set_fill_color(*color)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", size=12)
    pdf.set_draw_color(255, 255, 255)
    pdf.set_line_width(0.1)

    # Desenha cabeçalho
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align=Align.L, fill=True)
    pdf.ln()

    # Reset estilos para linhas normais
    pdf.set_font("DejaVu", size=11)
    pdf.set_text_color(0, 0, 0)

    regular_line = 10
    midle_line = 15
    large_line = 20

    for produto in produts:
        # Ajuste de altura da linha conforme regras do C#
        if produto.Imagem.startswith("http"):
            if "transparent.png" in produto.Imagem and len(produto.Produto) > 0:
                if len(produto.Produto) <= 70:
                    row_height = regular_line
                elif len(produto.Produto) <= 140:
                    row_height = midle_line
                else:
                    row_height = large_line
            else:
                row_height = large_line
        elif produto.Ref.startswith("*") or produto.Ref.startswith("#"):
            row_height = 12
        else:
            row_height = regular_line

        # Títulos
        if produto.Ref.startswith("*"):
            pdf.set_fill_color(47, 47, 47)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("DejaVu", size=12)
            texto = produto.Produto
            col_span = sum(col_widths)
            pdf.cell(col_span, row_height, texto, border=1, align=Align.L, fill=True)
            pdf.ln()
            pdf.set_font("DejaVu", size=11)
            pdf.set_text_color(0, 0, 0)
            continue

        # Subtítulos
        if produto.Ref.startswith("#"):
            pdf.set_fill_color(128, 128, 128)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("DejaVu", size=12)
            texto = produto.Produto
            col_span = sum(col_widths)
            pdf.cell(col_span, row_height, texto, border=1, align=Align.L, fill=True)
            pdf.ln()
            pdf.set_font("DejaVu", size=11)
            pdf.set_text_color(0, 0, 0)
            continue

        # Linha normal
        pdf.set_draw_color(128, 128, 128)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("DejaVu", size=10)

        # Salva a posição inicial da linha
        x_start = pdf.get_x()
        y_start = pdf.get_y()

        # Coluna 0: Imagem (apenas texto)
        pdf.multi_cell(col_widths[0], row_height, produto.Imagem, border=0, align=Align.L)
        x_nome = x_start + col_widths[0]
        pdf.set_xy(x_nome, y_start)

        # Coluna 1: Nome (pode quebrar em várias linhas)
        nome_lines = pdf.multi_cell(col_widths[1], 7, produto.Produto, border=0, align=Align.L, split_only=True)
        nome_height = 7 * len(nome_lines)
        max_height = max(nome_height, row_height)

        pdf.set_xy(x_nome + col_widths[1], y_start)

        # Coluna 2: Referência
        pdf.multi_cell(col_widths[2], max_height, produto.Ref, border=0, align=Align.L)
        x_next = x_nome + col_widths[1] + col_widths[2]
        pdf.set_xy(x_next, y_start)

        idx = 3

        # Coluna PVR (se aplicável)
        if show_pvr:
            pdf.multi_cell(col_widths[idx], max_height, produto.Pct_PVR, border=0, align=Align.L)
            x_next += col_widths[idx]
            pdf.set_xy(x_next, y_start)
            idx += 1

        # Coluna preço por país
        if country == 'AO':
            preco = produto.PVP_AO
        elif country == 'MZ':
            preco = produto.PVP_MZ
        else:
            preco = produto.PVP_PT
        pdf.multi_cell(col_widths[idx], max_height, preco, border=0, align=Align.L)
        x_next += col_widths[idx]
        pdf.set_xy(x_next, y_start)

        # Coluna link
        pdf.multi_cell(col_widths[idx+1], max_height, 'i', border=0, align=Align.C, link=produto.URL)
        # Move para a próxima linha
        pdf.set_xy(x_start, y_start + max_height)

""" def draw_table(pdf: FPDF, ref: str, produts: list[ProdutModel], show_pvr: bool, country: str):
    # Definições de larguras das colunas
    col_widths = [20, 80 if show_pvr else 100, 25]
    col_widths += [25] if show_pvr else []
    col_widths += [25 if show_pvr else 35, 15]


    # Cabeçalho
    headers = ["", "Nome", "Referência"]
    if show_pvr:
        headers += ["Uni./ PVR", "Uni./ PVP", "Ver+"]
    else:
        headers += ["Uni./ PVP", "Ver+"]

    # Estilos
    color = get_header_color(ref)
    pdf.set_fill_color(*color) 
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("DejaVu", size=12)
    pdf.set_draw_color(255, 255, 255)
    pdf.set_line_width(0.1)

    # Desenha cabeçalho
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1, align=Align.L, fill=True)
    pdf.ln()

    # Reset estilos para linhas normais
    pdf.set_font("DejaVu", size=11)
    pdf.set_text_color(0, 0, 0)

    regular_line = 10
    midle_line = 15
    large_line = 20

    for produto in produts:
        # Ajuste de altura da linha conforme regras do C#
        if produto.Imagem.startswith("http"):
            if "transparent.png" in produto.Imagem and len(produto.Produto) > 0:
                if len(produto.Produto) <= 70:
                    row_height = regular_line
                elif len(produto.Produto) <= 140:
                    row_height = midle_line
                else:
                    row_height = large_line
            else:
                row_height = large_line
        elif produto.Ref.startswith("*") or produto.Ref.startswith("#"):
            row_height = 12
        else:
            row_height = regular_line

        # Títulos 
        if produto.Ref.startswith("*"):
            pdf.set_fill_color(47, 47, 47)  # Cor diferente para título
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("DejaVu", size=12)
            texto = produto.Produto
            col_span = sum(col_widths)
            pdf.cell(col_span, row_height, texto, border=1, align=Align.L, fill=True)
            pdf.ln()
            # Reset estilos
            pdf.set_font("DejaVu", size=11)
            pdf.set_text_color(0, 0, 0)
            continue

        # Subtítulos
        if produto.Ref.startswith("#"):
            pdf.set_fill_color(128, 128, 128)  # Cor diferente para subtítulo
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("DejaVu", size=12)
            texto = produto.Produto
            col_span = sum(col_widths)
            pdf.cell(col_span, row_height, texto, border=1, align=Align.L, fill=True)
            pdf.ln()
            # Reset estilos
            pdf.set_font("DejaVu", size=11)
            pdf.set_text_color(0, 0, 0)
            continue

        # Linha normal
        # pdf.set_fill_color(128, 128, 128) 
        pdf.set_draw_color(128, 128, 128) 
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("DejaVu", size=10) 
        
        # Coluna 0: imagem (aqui só mostra o texto, para inserir imagem use pdf.image)
        pdf.cell(col_widths[0], row_height, produto.Imagem, border=False, align=Align.L, fill=False)
        # Coluna 1: nome 
        pdf.cell(col_widths[1], row_height, produto.Produto, border='B', align=Align.L, fill=False)
        # Coluna 2: referência
        pdf.cell(col_widths[2], row_height, produto.Ref, border='B', align=Align.L, fill=False)
        idx = 3

        if show_pvr:
            pdf.cell(col_widths[idx], row_height, produto.Pct_PVR, border='B', align=Align.L, fill=False)
            idx += 1

        if country == 'AO':
            pdf.cell(col_widths[idx], row_height, produto.PVP_AO, border='B', align=Align.L, fill=False)
        elif country == 'MZ':
            pdf.cell(col_widths[idx], row_height, produto.PVP_MZ, border='B', align=Align.L, fill=False)
        else:
            pdf.cell(col_widths[idx], row_height, produto.PVP_PT, border='B', align=Align.L, fill=False)

        idx += 1
        pdf.cell(col_widths[idx], row_height, 'i', border='B', align=Align.C, fill=False, link=produto.URL)
        pdf.ln()  """