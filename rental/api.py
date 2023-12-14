import frappe
from frappe import _
from erpnext.stock.stock_ledger import  get_previous_sle , NegativeStockError
from frappe.utils import flt

def create_warehouse(self , method):
    if self.get("__islocal"):
        doc = frappe.new_doc("Warehouse")
        doc.warehouse_name = self.name
        doc.save()



def set_actual_qty(self):
    from erpnext.stock.stock_ledger import is_negative_stock_allowed

    for d in self.get("items"):
        allow_negative_stock = is_negative_stock_allowed(item_code=d.item_code)
        previous_sle = get_previous_sle(
            {
                "item_code": d.item_code,
                "warehouse": d.s_warehouse or d.t_warehouse,
                "posting_date": self.posting_date,
                "posting_time": self.posting_time,
            }
        )

        # get actual stock at source warehouse
        d.actual_qty = previous_sle.get("qty_after_transaction") or 0

        # validate qty during submit
        if (
            d.docstatus == 1
            and d.s_warehouse
            and not allow_negative_stock
            and flt(d.actual_qty, d.precision("actual_qty"))
            < flt(d.transfer_qty, d.precision("actual_qty"))
        ):
            frappe.throw(
                _(
                    "Insufficient Credit Balance"
                )
                + "<br><br>"
                + _("Available Balance is {0}, you need {1}").format(
                    frappe.bold(flt(d.actual_qty, d.precision("actual_qty"))), frappe.bold(d.transfer_qty)
                ),
                NegativeStockError,
                title=_("Insufficient Balance"),
            )


@frappe.whitelist()
def check_roles():
    if "System Manager" in frappe.get_roles():
        return True
    return False

@frappe.whitelist()
def get_current_credit():
    customer = frappe.db.sql(f""" Select dl.link_name
                                From `tabDynamic Link` as dl
                                left join `tabContact` as co  ON co.name = dl.parent
                                Where dl.parenttype ='Contact' and co.user = '{frappe.session.user}' and
                                dl.link_doctype = 'Customer' """,as_dict = 1)

    if not len(customer):
        return  { "value" : 0 , "fieldtype":"Float"}

    warehouse = "{0} - {1}".format(customer[0].link_name , frappe.db.get_value("Company","Kingstech Pvt Ltd","abbr"))
    data = frappe.db.sql(f""" Select qty_after_transaction From `tabStock Ledger Entry`
                            where is_cancelled = 0 and warehouse = "{warehouse}" and item_code ="Credit Points" 
                            Order By creation Desc """,as_dict = 1)
    if data:
        return { "value" : data[0].qty_after_transaction , "fieldtype":"Float"}
        
    return  { "value" : 0 , "fieldtype":"Float"}