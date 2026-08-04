import frappe


def execute():
	"""Disable automatic invoice generation on every existing Subscription
	raised against a Customer, matching the flags now set to 0 for new
	subscriptions in rental.api.create_subscription."""
	subscriptions = frappe.db.get_all(
		"Subscription",
		filters={"party_type": "Customer"},
		fields=["name", "generate_invoice_at_period_start", "generate_new_invoices_past_due_date"],
	)

	updated, skipped = 0, 0
	for row in subscriptions:
		if not row.generate_invoice_at_period_start and not row.generate_new_invoices_past_due_date:
			skipped += 1
			continue

		frappe.db.set_value("Subscription", row.name, {
			"generate_invoice_at_period_start": 0,
			"generate_new_invoices_past_due_date": 0,
		})
		updated += 1

	frappe.db.commit()
	print(f"Patch complete: {updated} subscriptions had auto-invoicing disabled, {skipped} already off.")
