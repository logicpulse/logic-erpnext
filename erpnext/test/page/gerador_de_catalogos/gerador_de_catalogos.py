import frappe
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os 
from fpdf import FPDF, Align
from dataclasses import dataclass
from typing import Optional

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
def catalog_access(spreadsheet_id: str, sheet_name: str, cell_range: str):
    # Caminho absoluto para o arquivo de credenciais
    creds_path = os.path.join(
        frappe.get_app_path('erpnext', 'test', 'page', 'gerador_de_catalogos', 'app_client_secret.json')
    )

    scope = [ 'https://www.googleapis.com/auth/spreadsheets', 'https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    values = sheet.get(cell_range)
    
    generate_pdf(values, False)

    return values

def generate_pdf(values: list[list[str]], show_pvr: bool):
    # Caminhos 
    root_dir = os.path.join(frappe.get_app_path('erpnext', 'test', 'page', 'gerador_de_catalogos'))
    font_path = os.path.join(root_dir, 'DejaVuSans.ttf') 
    image_background_path = os.path.join(root_dir, 'access', 'access.track_background.png')
    header_image_path = os.path.join(root_dir, 'access', 'access.track_desc.png')
    # Criação do PDF
    pdf = FPDF()
    pdf.set_page_background(image_background_path)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(top=35, left=10, right=10)
    pdf.add_page() 
    page_width = pdf.w
    page_height = pdf.h
    # pdf.image(image_background_path, x=0, y=0, w=page_width, h=page_height) 
    pdf.image(header_image_path, x=10, y=30, w=page_width - 20)  
  
    pdf.add_font('DejaVu', '', font_path, uni=True)

    # pdf.set_y(-15) 
    # pdf.set_font("DejaVu", size=8) 
    # pdf.cell(0, 10, f"Page {pdf.page_no()}/{{nb}}", align="C")

    pdf.set_font("DejaVu", size=12)
    
    produts = convert_list_to_model(values)

    # for p in produts:
    #     print(p)

    pdf.ln(40)
    draw_table(pdf, produts, show_pvr) 

    pdf_output_path = os.path.join(frappe.get_app_path('erpnext', 'test', 'page', 'gerador_de_catalogos', 'gerador_de_catalogos.pdf')) 
    pdf.output(pdf_output_path) 

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

def draw_table(pdf: FPDF, produts: list[ProdutModel], show_pvr: bool):
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
    pdf.set_fill_color(119, 31, 73)  # Cor de fundo do cabeçalho
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
        pdf.set_fill_color(128, 128, 128) 
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("DejaVu", size=10) 
        
        # Coluna 0: imagem (aqui só mostra o texto, para inserir imagem use pdf.image)
        pdf.cell(col_widths[0], row_height, produto.Imagem, border=False, align=Align.L, fill=False)
        # Coluna 1: nome
        # pdf.multi_cell(col_widths[1], row_height, produto.Produto, border=0, align=Align.L, fill=False, print_sh=True)
        pdf.cell(col_widths[1], row_height, produto.Produto, border='B', align=Align.L, fill=False)
        # Coluna 2: referência
        pdf.cell(col_widths[2], row_height, produto.Ref, border='B', align=Align.L, fill=False)
        idx = 3
        if show_pvr:
            pdf.cell(col_widths[idx], row_height, produto.PVR_PT, border='B', align=Align.L, fill=False)
            idx += 1
        pdf.cell(col_widths[idx], row_height, produto.PVP_PT, border='B', align=Align.L, fill=False)
        idx += 1
        pdf.cell(col_widths[idx], row_height, 'i', border='B', align=Align.C, fill=False, link=produto.URL)
        # pdf.set_alpha(0.5)
        pdf.ln()
