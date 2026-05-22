# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
import frappe

class MaintenanceContract(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from erpnext.selling.doctype.visit.visit import Visit
		from frappe.types import DF

		article: DF.Link
		article_description: DF.Data | None
		billing_frequency: DF.Data | None
		client: DF.Link
		company: DF.Link
		contract_name: DF.Data
		contract_signed: DF.Check
		email_contacto: DF.Data | None
		end_date: DF.Date
		notes: DF.TextEditor | None
		number_of_licenses: DF.Int
		start_date: DF.Date
		status: DF.Literal["Ativo", "Inativo"]
		travel_included: DF.Check
		version: DF.Data | None
		visits: DF.Table[Visit]
	# end: auto-generated types

	@frappe.whitelist()
	def get_email_contacto(self):
		email = frappe.db.get_value("Address", { 'link_doctype': 'Customer', 'link_name': self.client }, "email_id")
		# print("Email Contacto: ", email)
		self.email_contacto = email

	pass
