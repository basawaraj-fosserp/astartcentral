import frappe

@frappe.whitelist()
def get_room_data(room):
    condition = ''
    if room:
        condition = f"where name = '{room}'"
    data = frappe.db.sql(f""" 
                        Select name, description, IF(enable_booking, 'booking open', 'booking close') as bookable
                        From `tabRoom`
                        {condition}
                         """, as_dict =True)

    for i , row in enumerate(data):
        row.update({'idx':i+1})
        page = frappe.db.exists('Web Page' ,{'title':row.name})
        rout = frappe.db.get_value("Web Page", page , 'route')
        row.update({'link':rout})

    return data
            

@frappe.whitelist()
def delete_row(room):
    frappe.db.delete("Room" , room.strip())
    return True

@frappe.whitelist()
def get_room_data_for_excel():
    meta = frappe.get_meta('Room')
    label = []
    field_name = []
    for row in meta.fields:
        label.append(row.label)
        field_name.append(row.fieldname)

    fields = ', '.join(field_name)
    data = frappe.db.sql(f""" 
                        Select {fields}
                        From `tabRoom`
                         """, as_dict =True)
    excel_data = []
    excel_data.append(label)
    for row in data:
        temp =[]
        for i in field_name:
            temp.append(row.get(i))
        excel_data.append(temp)
    return excel_data