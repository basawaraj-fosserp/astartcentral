import frappe


def execute():
	"""Correct existing Warehouses whose warehouse_name/name doesn't match
	their linked Customer's current name (see rental.api.rename_customer_warehouse,
	which now keeps them in sync going forward on every Customer rename)."""
	warehouses = frappe.db.get_all(
		"Warehouse",
		filters={"customer": ("is", "set")},
		fields=["name", "warehouse_name", "customer", "company"],
	)

	updated, skipped = 0, 0
	for wh in warehouses:
		if not wh.customer or wh.warehouse_name == wh.customer:
			skipped += 1
			continue

		new_name = wh.customer
		if wh.company:
			suffix = " - " + frappe.get_cached_value("Company", wh.company, "abbr")
			new_name = wh.customer + suffix

		if wh.name != new_name:
			frappe.rename_doc("Warehouse", wh.name, new_name, force=True)

		frappe.db.set_value("Warehouse", new_name, "warehouse_name", wh.customer, update_modified=False)
		updated += 1

	frappe.db.commit()
	print(f"Patch complete: {updated} warehouses renamed to match their customer, {skipped} already in sync.")
