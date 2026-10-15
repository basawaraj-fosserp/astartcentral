import frappe
from frappe.utils import flt, getdate

# Customers that were double-credited by the October 1st, 2026 run of
# rental.api.monthly_credit_allocation (before the fix that removed the
# redundant "allocate" Stock Reconciliation). Each of these received their
# correct monthly credit via a Stock Reconciliation, then the SAME amount
# again via the Stock Entry created by Credit Allocation.on_submit().
# Values below are the exact excess amount each customer must have deducted,
# identified by matching back-to-back SLEs for "Credit Points" where a Stock
# Reconciliation's resulting balance equals the very next Stock Entry's
# actual_qty, on 2026-10-01.
DUPLICATED_ALLOCATIONS = {
	"Test Customer": 6,
	"Face.AI": 4,
	"AStart Central": 200,
	"Venture Creation & Market Access": 100,
	"ImpactFat": 4,
	"Cartifuse": 4,
	"Advanced Ophthalmic Innovations Pte. Ltd.": 12,
	"Kah Yan": 8,
	"EBVision Biotechnology Pte Ltd": 4,
	"Kinara Vision Technologies Pte Ltd": 4,
	"SMX Circular Economy Platform Pte Ltd": 48,
	"BioCheetah": 12,
	"Trisafe Biotech": 4,
	"Singapore biodesign": 100,
	"ImmunoQs": 4,
	"Sequential skin": 28,
	"Revivo Biosystems": 32,
	"Prefer": 56,
	"Piezo Smart": 4,
	"Carecam": 8,
	"Argonaute Lifesciences Private Limited": 4,
	"HealBac Pte. Ltd.": 4,
	"Innocellular": 12,
	"A*StartCentral Staff Booking": 99999,
}


def execute():
	"""One-off: deduct the excess credit that
	rental.api.monthly_credit_allocation double-allocated on 2026-10-01,
	before the fix removing the redundant Stock Reconciliation step.

	Deducts the duplicated amount from each customer's CURRENT balance
	(not reset to their monthly credit), since balances have moved from
	legitimate usage since the duplicate was created.
	"""
	today = getdate()
	corrected, skipped, failed = 0, 0, 0

	for customer, duplicated_amount in DUPLICATED_ALLOCATIONS.items():
		duplicated_amount = flt(duplicated_amount)

		warehouse = frappe.db.get_value("Warehouse", {"customer": customer}, "name")
		if not warehouse:
			frappe.log_error(
				title="Credit allocation correction: warehouse not found",
				message=f"Customer {customer} has no warehouse; skipped.",
			)
			skipped += 1
			continue

		company = frappe.db.get_value("Warehouse", warehouse, "company")
		current_qty = flt(frappe.db.get_value(
			"Bin", {"item_code": "Credit Points", "warehouse": warehouse}, "actual_qty"
		))
		raw_corrected_qty = current_qty - duplicated_amount

		if raw_corrected_qty < 0:
			# Customer already spent into the duplicated portion (real usage
			# overlapped with the duplicate credit). Floor at 0 instead of
			# going negative — the part of the duplicate they already used
			# is not recovered automatically and needs a manual decision.
			frappe.log_error(
				title="Credit allocation correction: floored at 0",
				message=(
					f"Customer {customer}: current balance {current_qty} minus duplicated "
					f"amount {duplicated_amount} would be {raw_corrected_qty}. Floored to 0 "
					f"instead — customer already used part of the duplicated credit. "
					f"Needs manual review if further recovery is wanted."
				),
			)

		corrected_qty = max(0.0, raw_corrected_qty)

		try:
			reco_doc = frappe.new_doc("Stock Reconciliation")
			reco_doc.company = company
			reco_doc.purpose = "Stock Reconciliation"
			reco_doc.posting_date = today
			reco_doc.append("items", {
				"item_code": "Credit Points",
				"warehouse": warehouse,
				"qty": corrected_qty,
			})
			reco_doc.save(ignore_permissions=True)
			reco_doc.submit()
			corrected += 1
			frappe.logger().info(
				f"Corrected {customer}: {current_qty} -> {corrected_qty} "
				f"(removed duplicated {duplicated_amount}) via {reco_doc.name}"
			)
		except Exception:
			failed += 1
			frappe.log_error(
				title="October duplicate credit correction patch failed",
				message=frappe.get_traceback(),
			)

	frappe.db.commit()
	print(
		f"Patch complete: {corrected} customers corrected, {skipped} skipped (no warehouse), "
		f"{failed} failed. Check Error Log for any customers floored at 0 (needs manual review)."
	)
