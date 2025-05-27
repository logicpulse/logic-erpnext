import frappe
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

@frappe.whitelist()
def catalog_access(spreadsheet_id, sheet_name, cell_range):
    # Caminho absoluto para o arquivo de credenciais
    creds_path = os.path.join(
        frappe.get_app_path('erpnext', 'test', 'page', 'gerador_de_catalogos', 'app_client_secret.json')
    )

    scope = [ 'https://www.googleapis.com/auth/spreadsheets', 'https://spreadsheets.google.com/feeds']
    creds = ServiceAccountCredentials.from_json_keyfile_name(creds_path, scope)
    client = gspread.authorize(creds)

    sheet = client.open_by_key(spreadsheet_id).worksheet(sheet_name)
    values = sheet.get(cell_range)
    return values