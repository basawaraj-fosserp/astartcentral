import frappe


def get_warehouse_for_customer(customer, company):
	"""Return the warehouse linked to a customer via the custom 'customer' field."""
	warehouse = frappe.db.get_value("Warehouse", {"customer": customer, "company": company}, "name")
	if not warehouse:
		frappe.throw(
			f"No warehouse found for customer <b>{customer}</b>. "
			"Please ensure a Credit Request has been submitted to create the warehouse."
		)
	return warehouse
