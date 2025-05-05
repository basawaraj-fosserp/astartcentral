frappe.views.calendar["Equipment Booking"] = {
    field_map: {
		start: "from_datetime",
		end: "to_datetime",
		id: "name",
		title : "title",
		allDay : "allDay",
		color :"color"

	},
    filters: [
        {
			"label": __("Select Equipment"),
			"fieldname": "select_equipment",
            "fieldtype": "Link",
			"options": "Equipment"
        }
    ],
    get_events_method: "rental.rental.doctype.equipment_booking.equipment_booking.get_booking_data",
    // get_css_class: function(data) {
	// 	console.log(data)
	// 	if(data.status == "Active"){
	// 		return 'success'
	// 	}
	// 	if(data.status == "Inactive"){
	// 		return 'warning'
	// 	}
	// }
}