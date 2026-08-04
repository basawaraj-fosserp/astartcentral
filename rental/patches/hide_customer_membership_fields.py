import frappe


def execute():
	"""Hide the internal Membership and Subscription Plan fields on Customer -
	these are managed automatically by rental.api (create_suto_sub,
	create_subscription_plan, update_subscription_plan_cost, etc.) and should
	not be edited directly from the form."""
	for fieldname in ("custom_membership", "custom_subscription_plan"):
		frappe.make_property_setter(
			{
				"doctype": "Customer",
				"fieldname": fieldname,
				"property": "hidden",
				"value": "1",
				"property_type": "Check",
			}
		)

	frappe.db.commit()
	print("Patch complete: custom_membership and custom_subscription_plan hidden on Customer.")
