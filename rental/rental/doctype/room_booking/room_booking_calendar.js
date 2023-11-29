frappe.views.calendar["Room Booking"] = {
    field_map: {
		"start": "from_datetime",
		"end": "end_datetime",
		"id": "name",
		"title": "title",

	},
    filters: [
        {
			"label": __("Room Type"),
			"fieldname": "select_room_type",
            "fieldtype": "Link",
			"options": "Room"
        }
    ],
    get_events_method: "rental.rental.doctype.room_booking.room_booking.get_booking_data",
    get_css_class: function(data) {
		console.log(data)
		if(data.status == "Active"){
			return 'success'
		}
		if(data.status == "Inactive"){
			return 'warning'
		}
	}
}