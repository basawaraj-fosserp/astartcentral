import frappe

def check(customer=None):
    from rental.rental.utils import get_warehouse_for_customer
    if not customer:
        customer = "Vitreogel Innovations Pte Ltd"
    company = frappe.db.get_value("Customer", customer, "default_company") or frappe.defaults.get_defaults().company
    wh = get_warehouse_for_customer(customer, None)
    print("customer:", repr(customer))
    print("warehouse:", repr(wh))
    print("wh[:-5]:", repr(wh[:-5]) if wh else None)
    print("matches customer name exactly:", wh[:-5] == customer if wh else None)

def check_all_room_bookings():
    rooms = frappe.db.sql("""select name, customer from `tabRoom Booking` where docstatus=1 limit 5""", as_dict=1)
    for r in rooms:
        from rental.rental.utils import get_warehouse_for_customer
        wh = get_warehouse_for_customer(r.customer, None)
        print(r.name, "customer=", repr(r.customer), "warehouse=", repr(wh), "wh[:-5]=", repr(wh[:-5]) if wh else None, "match=", (wh[:-5]==r.customer if wh else None))
