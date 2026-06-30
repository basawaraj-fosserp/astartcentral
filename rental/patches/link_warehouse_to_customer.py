import frappe


def execute():
	# 1. Add custom 'customer' Link field to Warehouse doctype if not already present
	if not frappe.db.exists("Custom Field", {"dt": "Warehouse", "fieldname": "customer"}):
		frappe.get_doc({
			"doctype": "Custom Field",
			"dt": "Warehouse",
			"fieldname": "customer",
			"label": "Customer",
			"fieldtype": "Link",
			"options": "Customer",
			"insert_after": "warehouse_name",
			"in_list_view": 0,
		}).insert(ignore_permissions=True)
		frappe.db.commit()

	# 2. Link existing warehouses to customers by matching warehouse name pattern.
	#    Two patterns exist in this codebase:
	#      a) "{Customer Name} - {Company Abbr}"  (credit_request / credit_allocation)
	#      b) "{Customer Name} - KPL"             (api.create_warehouse hardcoded abbr)
	warehouses = frappe.db.get_all("Warehouse", fields=["name", "company", "customer"])

	# Build a set of all valid suffixes across all companies
	all_abbrs = frappe.db.get_all("Company", fields=["abbr"])
	suffixes = {" - " + c.abbr for c in all_abbrs}
	suffixes.add(" - KPL")  # hardcoded legacy abbr

	for wh in warehouses:
		if wh.customer:
			continue  # already linked

		matched_customer = None
		for suffix in suffixes:
			if wh.name.endswith(suffix):
				candidate = wh.name[: -len(suffix)]
				if frappe.db.exists("Customer", candidate):
					matched_customer = candidate
					break

		if matched_customer:
			frappe.db.set_value("Warehouse", wh.name, "customer", matched_customer, update_modified=False)

	frappe.db.commit()
	print("Patch complete: Warehouse customer field added and existing warehouses linked.")
