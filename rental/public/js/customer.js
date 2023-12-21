frappe.ui.form.on('Customer', {
    refresh:function(frm){
        frm.add_custom_button(__('Create Subscription'), function () {
            frappe.model.open_mapped_doc({
                method: "rental.api.create_subscription",
                frm: frm
            })
        },__('Create'));
        frm.remove_custom_button(__("Pricing Rule") , __("Create"))
    }
})