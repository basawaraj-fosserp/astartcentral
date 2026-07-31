import frappe


def execute():
	"""Correct existing Subscriptions whose plans table still references a
	stale Subscription Plan instead of the customer's current
	custom_subscription_plan (see rental.api.swap_subscription_plan)."""
	customers = frappe.db.get_all(
		"Customer",
		filters={"custom_subscription": ("is", "set"), "custom_subscription_plan": ("is", "set")},
		fields=["name", "custom_subscription", "custom_subscription_plan"],
	)

	updated, skipped = 0, 0
	for row in customers:
		if not frappe.db.exists("Subscription", row.custom_subscription):
			skipped += 1
			continue

		sub_doc = frappe.get_doc("Subscription", row.custom_subscription)
		plan_names = [d.plan for d in sub_doc.plans]

		if plan_names == [row.custom_subscription_plan]:
			skipped += 1
			continue

		qty = 1
		for d in sub_doc.plans:
			if d.plan != row.custom_subscription_plan:
				qty = d.qty or 1

		sub_doc.set("plans", [d for d in sub_doc.plans if d.plan == row.custom_subscription_plan])
		if not sub_doc.plans:
			sub_doc.append("plans", {"plan": row.custom_subscription_plan, "qty": qty})

		sub_doc.flags.ignore_permissions = True
		sub_doc.save()
		updated += 1

	frappe.db.commit()
	print(f"Patch complete: {updated} Subscriptions corrected, {skipped} already in sync.")
