import frappe
from erpnext.stock.stock_ledger import  get_previous_sle

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
                    "Row {0}: Quantity not available for {4} in warehouse {1} at posting time of the entry ({2} {3})"
                ).format(
                    d.idx,
                    frappe.bold(d.s_warehouse),
                    formatdate(self.posting_date),
                    format_time(self.posting_time),
                    frappe.bold(d.item_code),
                )
                + "<br><br>"
                + _("Available quantity is {0}, you need {1}").format(
                    frappe.bold(flt(d.actual_qty, d.precision("actual_qty"))), frappe.bold(d.transfer_qty)
                ),
                NegativeStockError,
                title=_("Insufficient Stock"),
            )