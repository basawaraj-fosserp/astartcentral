frappe.listview_settings['Credit Request'] = {
	colwidths: {"subject": 6},
	filters: [["status", "=", "Pending"]],

	get_indicator: function(doc) {
		if (doc.status === 'Pending') {
			return [__(doc.status),  'red', `status,=,Open`];
		} else if (doc.status === 'Allocated') {
			return [__(doc.status), "green", "status,=," + doc.status];
	}
}}
