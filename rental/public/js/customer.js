frappe.ui.form.on('Customer', {
    refresh:function(frm){
        frm.add_custom_button(__('Create Subscription'), function () {
            frappe.model.open_mapped_doc({
                method: "rental.api.create_subscription",
                frm: frm
            })
        },__('Create'));
        frm.remove_custom_button(__("Pricing Rule") , __("Create"))
    },
    custom_agreement_start_date:function(frm){
        if(frm.doc.custom_agreement_start_date){
            var end_date = frappe.datetime.add_days(frm.doc.custom_agreement_start_date, 364);
            cur_frm.set_value("custom_agreement_end_date", end_date);
        }
    },
    custom_select_all_equipments:function(frm){
        frappe.call({
            method : "rental.api.get_all_equipment",
            args:{

            },
            callback:(r)=>{
                frm.doc.custom_agreement_on_equipment = []
                $.each(r.message, function(i, d) {
                    var row = frm.add_child('custom_agreement_on_equipment');
                    row.equipment = d
                });
                frm.refresh_field('custom_agreement_on_equipment');
            }
        })
    }
})