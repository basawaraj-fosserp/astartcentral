frappe.listview_settings['Room Booking'] = {
	colwidths: {"subject": 6},

	onload: function(listview) {
		// Keep only List and Calendar in the view switcher dropdown
		const allowed_views = ["List", "Calendar"];
		frappe.after_ajax(() => {
			listview.page.menu_btn_group.find(".custom-menu li[data-view]").each(function() {
				if (!allowed_views.includes($(this).attr("data-view"))) {
					$(this).hide();
				}
			});
		});
	},

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
