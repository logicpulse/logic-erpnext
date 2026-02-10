<p>Olá {{ doc.tenant or doc.customer_name }},</p>

<p>
O contrato de manutenção <strong>{{ doc.contract_name }}</strong> teve início em
<strong>{{ frappe.format_date(doc.start_date) }}</strong>.
</p>

<p>
Período:
{{ frappe.format_date(doc.start_date) }}
a
{{ frappe.format_date(doc.end_date) }}<br>
Produto/Serviço: {{ doc.product }}
</p>

<p>
Qualquer dúvida, estamos à disposição.
</p>

<p>
Cumprimentos,<br>
<strong>{{ frappe.defaults.get_user_default("Company") }}</strong>
</p>
