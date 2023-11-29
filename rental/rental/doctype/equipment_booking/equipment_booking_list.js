frappe.listview_settings['Equipment Booking'] = {
	colwidths: {"subject": 6},
	
	get_indicator: function(doc) {
		if (doc.status === 'Active') {
			return [__(doc.status), 'green' || 'green', `status,=,Active`];
		} else if (doc.status === 'Inactive') {
			return [__(doc.status), "orenge", "status,=," + doc.status];
		} else {
			return [__(doc.status), "red", "status,=," + doc.status];
		}
	}
}
