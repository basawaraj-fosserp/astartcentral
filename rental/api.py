import frappe
from frappe import _
from erpnext.stock.stock_ledger import  get_previous_sle , NegativeStockError
from frappe.utils import flt, getdate, now  
from frappe.model.mapper import get_mapped_doc
from datetime import datetime, timedelta, time
from erpnext.accounts.doctype.subscription.subscription import get_subscription_updates

def validate_customer(self, method):
    create_subscription_plan(self)
    update_subscription_plan_cost(self)



def create_suto_sub(self, method):
    create_warehouse(self)
    if not self.custom_subscription:
        sub_doc = create_subscription(source_name = self.name)
        sub_doc.save()
        get_subscription_updates(sub_doc.name)
        self.custom_subscription = sub_doc.name
        self.custom_membership = sub_doc.name
        frappe.db.set_value("Customer", self.name, {
            "custom_subscription": sub_doc.name,
            "custom_membership": sub_doc.name,
        })
    data = frappe.db.get_list("Credit Allocation" , filters ={'customer':self.name , "docstatus":1})
    if self.custom_credit_assigned_monthly and not len(data):
        doc_ = frappe.new_doc("Credit Allocation")
        doc_.ignore_linked_doctypes= ('Customer')
        doc_.customer = self.name
        doc_.company = frappe.db.get_value("Warehouse", {"customer": self.name}, "company")
        doc_.posting_date = getdate()
        doc_.credit_score = self.custom_credit_assigned_monthly
        doc_.save(ignore_permissions = True)
        doc_.submit()


def create_warehouse(self):
    existing = frappe.db.get_value("Warehouse", {"customer": self.name}, "name")
    if not existing:
        company = frappe.db.get_single_value("Global Defaults", "default_company")
        doc = frappe.new_doc("Warehouse")
        doc.warehouse_name = self.name
        doc.company = company
        doc.customer = self.name
        doc.save(ignore_permissions=True)
        
def on_update(self , method):
    data = frappe.db.get_list("Credit Allocation" , filters ={'customer':self.name , "docstatus":1})
    if self.custom_credit_assigned_monthly and not len(data):
        doc_ = frappe.new_doc("Credit Allocation")
        doc_.customer = self.name
        doc_.ignore_linked_doctypes= ['Customer']
        doc_.company = frappe.db.get_value("Warehouse", {"customer": self.name}, "company")
        doc_.posting_date = getdate()
        doc_.credit_score = self.custom_credit_assigned_monthly
        doc_.save(ignore_permissions = True)
        doc_.submit()

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
    if "System Manager" in frappe.get_roles() or "Astart Admin" in frappe.get_roles():
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

    customer_name = customer[0].link_name
    warehouse = frappe.db.get_value("Warehouse", {"customer": customer_name}, "name")
    if not warehouse:
        return {"value": 0, "fieldtype": "Float"}

    data = frappe.db.sql(f""" Select qty_after_transaction From `tabStock Ledger Entry`
                            where is_cancelled = 0 and warehouse = "{warehouse}" and item_code ="Credit Points"
                            Order By creation Desc """, as_dict=1)
    if data:
        return {"value": data[0].qty_after_transaction, "fieldtype": "Float"}

    return {"value": 0, "fieldtype": "Float"}

@frappe.whitelist()
def create_subscription(source_name , target_doc = None):
    doclist = get_mapped_doc(
        "Customer",
        source_name,
        {
            "Customer": {
                "doctype": "Subscription",
                "field_map": {
                    "doctype":"party_type",
                    "name":"party",
                    "custom_agreement_start_date":"start_date",
                    "custom_agreement_end_date":"end_date"
                },
                },
        },
        target_doc,
    )
    doclist.update({'generate_invoice_at_period_start':1, "generate_new_invoices_past_due_date":1})
    
    doclist.append('plans',{
        "plan" : frappe.db.get_value('Customer', source_name, 'custom_subscription_plan'),
        'qty':1
    })

    return doclist


def check_subscription_period():
    customer = []
    doc_list = frappe.get_list("Subscription" , pluck = "name")
    for row in doc_list:
        doc = frappe.get_doc("Subscription" , row)
        if getdate(doc.end_date) < getdate():
            customer.append(doc.customer)
    if customer:
        for row in customer:
            users = frappe.db.sql(f""" Select user
                                    From `tabContact` as c
                                    left join `tabDynamic Link` as dl On dl.parent = c.name
                                    Where dl.link_doctype = "Customer" and dl.name = '{row}' """,as_dict = 1)
            user = users[0].user
            frappe.db.set_value("User" , user , "enable" , 0)
        


# on submit of subscription allocate a credit point
# def allocation_of_credit_bases_payment(self ,method):
#     paid_amount = self.paid_amount
#     data = []
#     for row in self.references:
#         if row.reference_doctype == "Sales Invoice" and self.payment_type == "Receive":
#             data = frappe.db.sql(f""" Select spd.plan , spd.qty
#                                     From `tabSubscription Invoice` as si
#                                     left join `tabSubscription` as su On su.name = si.parent
#                                     left join `tabSubscription Plan Detail` as spd on spd.parent = su.name
#                                     Where document_type = "Sales Invoice" and invoice = '{row.reference_name}'
#                                     """,as_dict = 1)

#             for d in data:
#                 doc = frappe.get_doc('Subscription Plan', d.plan)
#                 credit_score = frappe.db.get_value("Customer", self.party, 'custom_credit_assigned_monthly')
#                 credit_allocation(self.party, self.company, credit_score , self.name , row.total_amount)
                



# def credit_allocation(customer, company, credit_score, payment_reference , paid_amount):
    
#cron monthly credit allocation
def monthly_credit_allocation():
    cu_list = frappe.db.get_list("Customer", pluck="name")
    for row in cu_list:
        warehouse = frappe.db.get_value("Warehouse", {"customer": row}, "name")
        if not warehouse:
            continue

        sle_list = frappe.db.get_list('Stock Ledger Entry', {'warehouse': warehouse})
        if not len(sle_list):
            continue

        sr_doc = frappe.new_doc("Stock Reconciliation")
        sr_doc.company = frappe.db.get_value("Warehouse", warehouse, "company")
        sr_doc.purpose = "Stock Reconciliation"
        sr_doc.append('items', {
            'item_code': "Credit Points",
            "warehouse": warehouse,
            'qty': 0,
        })
        try:
            sr_doc.save(ignore_permissions=True)
            sr_doc.submit()
            customer = frappe.get_doc("Customer", row)
            doc = frappe.new_doc("Credit Allocation")
            doc.customer = row
            doc.company = sr_doc.company
            doc.credit_score = customer.custom_credit_assigned_monthly
            doc.save(ignore_permissions=True)
            doc.submit()
        except Exception:
            frappe.log_error("Customer {0} not found any warehouse for credit point".format(row))

        

def create_user_permission(self , method):
    if self.user and len(self.links) > 0:
        if not frappe.db.exists("User Permission", {'user':self.user, 'allow':'Customer', 'for_value':self.links[0].link_name}):
            doc = frappe.new_doc("User Permission")
            doc.user = self.user
            doc.allow = "Customer"
            doc.for_value = self.links[0].link_name
            doc.apply_to_all_doctypes = 1
            doc.save(ignore_permissions = True)

@frappe.whitelist()
def invite_user(contact):
    contact = frappe.get_doc("Contact", contact)

    if not contact.email_id:
        frappe.throw(_("Please set Email Address"))

    if contact.has_permission("write"):
        user = frappe.get_doc(
            {
                "doctype": "User",
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "email": contact.email_id,
                "user_type": "Website User",
                "send_welcome_email": 1,
            }
        )
        user.insert(ignore_permissions=True)
        user.add_roles('Customer Rental Booking' , 'Astart Customer')
        return user.name

def update_subscription_plan_cost(self):
    if self.is_new() or not self.custom_subscription_plan:
        return

    if not self.has_value_changed("custom_membership_costmonthly"):
        return

    frappe.db.set_value("Subscription Plan", self.custom_subscription_plan, "cost", self.custom_membership_costmonthly)


def backfill_subscription_plan_costs():
    """One-off: sync every customer's existing Subscription Plan cost to
    their current custom_membership_costmonthly value. Run once via:
    bench --site <site> execute rental.api.backfill_subscription_plan_costs
    """
    customers = frappe.db.get_all(
        "Customer",
        filters={"custom_subscription_plan": ("is", "set")},
        fields=["name", "custom_subscription_plan", "custom_membership_costmonthly"],
    )

    updated, skipped = 0, 0
    for row in customers:
        current_cost = frappe.db.get_value("Subscription Plan", row.custom_subscription_plan, "cost")
        if current_cost == row.custom_membership_costmonthly:
            skipped += 1
            continue

        frappe.db.set_value(
            "Subscription Plan",
            row.custom_subscription_plan,
            "cost",
            row.custom_membership_costmonthly,
        )
        updated += 1

    frappe.db.commit()
    print(f"Subscription Plan cost backfill done: {updated} updated, {skipped} already in sync.")


def create_subscription_plan(self):
    if not self.custom_subscription_plan:
        doc = frappe.new_doc('Subscription Plan')
        doc.currency = "SGD"
        doc.plan_name = self.customer_name + ' - '+ str(self.custom_membership_costmonthly)
        doc.item = "Credit Points"
        doc.cost = self.custom_membership_costmonthly
        doc.price_determination = 'Fixed Rate'
        doc.billing_interval = 'Month'
        doc.billing_interval_count = 1
        doc.flags.ignore_permissions = 1
        doc.save()
        self.custom_subscription_plan = doc.name


def on_trash_customer(self, method):
    warehouse = frappe.db.get_value("Warehouse", {"customer": self.name}, "name")
    if warehouse:
        try:
            frappe.db.delete('Warehouse', warehouse)
        except Exception:
            frappe.throw(f"Customer <b>{self.name}</b> is linked to transactions. Please contact the Administrator.")


@frappe.whitelist()
def get_all_equipment():
    return frappe.db.get_list("Equipment", {"status" : "Active"}, pluck="name")

@frappe.whitelist()
def get_all_room():
    return frappe.db.get_list("Room", pluck="name")