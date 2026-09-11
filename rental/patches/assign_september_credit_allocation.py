import frappe
from frappe.utils import flt, getdate


def execute():
	"""One-off: allocate this month's credit points for customers who don't
	already have a submitted Credit Allocation for the current month/year
	(the scheduled rental.api.monthly_credit_allocation job was failing with
	EmptyStockReconciliationItemsError before that function was fixed)."""
	today = getdate()

	customers = frappe.db.get_all("Customer", pluck="name")
	allocated, skipped, failed = 0, 0, 0

	for customer in customers:
		warehouse = frappe.db.get_value("Warehouse", {"customer": customer}, "name")
		if not warehouse:
			continue

		already_allocated = frappe.db.exists(
			"Credit Allocation",
			{
				"customer": customer,
				"docstatus": 1,
				"posting_date": ["between", [today.replace(day=1), today]],
			},
		)
		if already_allocated:
			skipped += 1
			continue

		customer_doc = frappe.get_doc("Customer", customer)
		new_credit_score = flt(customer_doc.custom_credit_assigned_monthly)
		company = frappe.db.get_value("Warehouse", warehouse, "company")

		current_qty = flt(frappe.db.get_value(
			"Bin", {"item_code": "Credit Points", "warehouse": warehouse}, "actual_qty"
		))

		try:
			if current_qty != 0:
				clear_doc = frappe.new_doc("Stock Reconciliation")
				clear_doc.company = company
				clear_doc.purpose = "Stock Reconciliation"
				clear_doc.append("items", {
					"item_code": "Credit Points",
					"warehouse": warehouse,
					"qty": 0,
				})
				clear_doc.save(ignore_permissions=True)
				clear_doc.submit()

			if new_credit_score != 0:
				sr_doc = frappe.new_doc("Stock Reconciliation")
				sr_doc.company = company
				sr_doc.purpose = "Stock Reconciliation"
				sr_doc.append("items", {
					"item_code": "Credit Points",
					"warehouse": warehouse,
					"qty": new_credit_score,
				})
				sr_doc.save(ignore_permissions=True)
				sr_doc.submit()

			doc = frappe.new_doc("Credit Allocation")
			doc.customer = customer
			doc.company = company
			doc.credit_score = new_credit_score
			doc.save(ignore_permissions=True)
			doc.submit()
			allocated += 1
		except Exception:
			failed += 1
			frappe.log_error(
				title="September credit allocation patch failed",
				message=frappe.get_traceback(),
			)

	frappe.db.commit()
	print(f"Patch complete: {allocated} customers allocated, {skipped} already had this month's allocation, {failed} failed.")
