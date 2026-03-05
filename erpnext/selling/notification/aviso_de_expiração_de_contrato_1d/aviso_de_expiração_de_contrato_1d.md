<div style="font-family: Arial, Helvetica, sans-serif; font-size: 14px; color: #333; line-height: 1.6;">

    <p>Prezado(a) <strong>{{ doc.client }}</strong>,</p>

    <p>
        Esperamos que esteja bem.
    </p>

    <p>
        Informamos que o contrato de manutenção 
        <strong>{{ doc.contract_name }}</strong> 
        encontra-se <strong>prest es a expirar</strong>.
    </p>

    <table style="border-collapse: collapse; margin-top: 15px;">
        <tr>
            <td style="padding: 6px 0;"><strong>Data de Início:</strong></td>
            <td style="padding: 6px 15px;">{{ frappe.format_date(doc.start_date) }}</td>
        </tr>
        <tr>
            <td style="padding: 6px 0;"><strong>Data de Término:</strong></td>
            <td style="padding: 6px 15px; color: #c0392b; font-weight: 600;">
                {{ frappe.format_date(doc.end_date) }}
            </td>
        </tr>
        <tr>
            <td style="padding: 6px 0;"><strong>Produto / Serviço:</strong></td>
            <td style="padding: 6px 15px;">
                {{ doc.article_description }}
            </td>
        </tr>
    </table>

    <p style="margin-top: 20px;">
        Para garantir a continuidade dos serviços e evitar qualquer interrupção,
        recomendamos que a renovação seja efetuada antes da data de término.
    </p>

    <p>
        Caso já tenha iniciado o processo de renovação, pedimos que desconsidere esta mensagem.
    </p>

    <p style="margin-top: 25px;">
        Permanecemos à disposição para qualquer esclarecimento adicional.
    </p>

    <p style="margin-top: 25px;">
        Atenciosamente,<br>
        <strong>{{ doc.company }}</strong>
    </p>

</div>