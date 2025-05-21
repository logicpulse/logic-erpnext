# filepath: /workspace/development/frappe-bench/apps/erpnext/erpnext/gerador_de_catalogo/desktop.py
import frappe

def get_data():
    return [
        {
            "module_name": "gerador_de_catalogo",
            "color": "blue",
            "icon": "octicon octicon-file-directory",
            "type": "module",
            "label": "Gerador de Catalogo"
        }
    ]