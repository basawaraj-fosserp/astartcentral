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
			const today = moment().format('YYYY-MM-DD');
			// Block past dates
			if (startDate.format('YYYY-MM-DD') < today) {
				frappe.show_alert({ message: __('Booking on past dates is not allowed.'), indicator: 'red' });
				return;
			}
			// Block past time slots on today
			if (startDate.format('YYYY-MM-DD') === today && startDate.isBefore(moment())) {
				frappe.show_alert({ message: __('Booking for past times is not allowed.'), indicator: 'red' });
				return;
			}
			if (view.name === "month" && endDate - startDate === 86400000) return;
			var event = frappe.model.get_new_doc("Equipment Booking");
			event["from_datetime"] = frappe.datetime.convert_to_system_tz(startDate.format());
			event["to_datetime"]   = frappe.datetime.convert_to_system_tz(endDate.format());
			frappe.set_route("Form", "Equipment Booking", event.name);
		},
		dayClick: function(date, jsEvent, view) {
			const today = moment().format('YYYY-MM-DD');
			if (date.format('YYYY-MM-DD') < today) {
				frappe.show_alert({ message: __('Booking on past dates is not allowed.'), indicator: 'red' });
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