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

	options: {
		select: function(startDate, endDate, jsEvent, view) {
			// Single day click in month view — let dayClick handle it, ignore here
			if (view.name === "month" && endDate - startDate === 86400000) return;

			const site_tz = (frappe.boot.time_zone && frappe.boot.time_zone.system) || 'Asia/Singapore';
			const now = moment.tz(site_tz);
			// Convert FullCalendar's local-time date to site timezone for comparison
			const start_sg = moment(frappe.datetime.convert_to_system_tz(moment(startDate).locale("en")));
			const today = now.format('YYYY-MM-DD');
			const startStr = start_sg.format('YYYY-MM-DD');
			// Block past dates
			if (startStr < today) {
				frappe.show_alert({ message: __('Booking on past dates is not allowed.'), indicator: 'red' });
				return;
			}
			// Block past time slots on today
			if (startStr === today && start_sg.isBefore(now)) {
				frappe.show_alert({ message: __('Booking for past times is not allowed.'), indicator: 'red' });
				return;
			}
			var event = frappe.model.get_new_doc("Equipment Booking");
			event["from_datetime"] = start_sg.format("YYYY-MM-DD HH:mm:ss");
			event["to_datetime"]   = frappe.datetime.convert_to_system_tz(moment(endDate).locale("en")).format("YYYY-MM-DD HH:mm:ss");
			frappe.set_route("Form", "Equipment Booking", event.name);
		},
		dayClick: function(date, jsEvent, view) {
			const site_tz = (frappe.boot.time_zone && frappe.boot.time_zone.system) || 'Asia/Singapore';
			const now = moment.tz(site_tz);
			// Convert FullCalendar's local-time date to site timezone for comparison
			const date_sg = moment(frappe.datetime.convert_to_system_tz(moment(date).locale("en")));
			const today = now.format('YYYY-MM-DD');
			const dateStr = date_sg.format('YYYY-MM-DD');
			if (dateStr < today) {
				frappe.show_alert({ message: __('Booking on past dates is not allowed.'), indicator: 'red' });
				return false;
			}
			// In day/week view, block clicks on past time slots
			if (view.name !== "month" && dateStr === today && date_sg.isBefore(now)) {
				frappe.show_alert({ message: __('Booking for past times is not allowed.'), indicator: 'red' });
				return false;
			}
			if (view.name === "month") {
				const $cal = $(jsEvent.target).closest(".fc");
				const $date_cell = $("td[data-date=" + date.format("YYYY-MM-DD") + "]");
				if ($date_cell.hasClass("date-clicked")) {
					$cal.fullCalendar("changeView", "agendaDay");
					$cal.fullCalendar("gotoDate", date);
					$cal.find(".date-clicked").removeClass("date-clicked");
					$cal.find(".fc-month-button").removeClass("active");
					$cal.find(".fc-agendaDay-button").addClass("active");
				}
				$cal.find(".date-clicked").removeClass("date-clicked");
				$date_cell.addClass("date-clicked");
			}
			return false;
		}
	}
}