frappe.ui.form.on('Quotation Item', {
    discount_percentage: function (frm, cdt, cdn) {
        frappe.msgprint("Campo alterado!");
        console.log('discount changed');
        // console.log('cdt:', cdt);
        // console.log('cdn:', cdn);
        // var item = frappe.get_doc(cdt, cdn);
        // item.amount = item.price_list_rate * (1 - item.discount_percentage / 100);
        // frm.refresh_field('items');
    }
});
