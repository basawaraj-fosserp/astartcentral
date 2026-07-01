function room_booking_time_within_hours(momentDate) {
	return room_booking_time_within_hours._check(momentDate);
}

room_booking_time_within_hours._admin_hours = null;
room_booking_time_within_hours._fetch_admin_hours = function() {
	if (room_booking_time_within_hours._admin_hours) {
		return Promise.resolve(room_booking_time_within_hours._admin_hours);
	}
	return frappe.db.get_doc("Admin Setting").then(doc => {
		room_booking_time_within_hours._admin_hours = {
			from: doc.booking_hours_from,
			to: doc.booking_hours_to
		};
		return room_booking_time_within_hours._admin_hours;
	});
};
room_booking_time_within_hours._to_minutes = function(str) {
	// e.g. "02:30 PM" -> minutes since midnight
	const [time, meridian] = str.split(" ");
	let [h, m] = time.split(":").map(Number);
	if (meridian === "PM" && h !== 12) h += 12;
	if (meridian === "AM" && h === 12) h = 0;
	return h * 60 + m;
};
room_booking_time_within_hours._check = function(momentDate) {
	const hours = room_booking_time_within_hours._admin_hours;
	if (!hours || !hours.from || !hours.to) return true;
	const minutes = momentDate.hours() * 60 + momentDate.minutes();
	return minutes >= room_booking_time_within_hours._to_minutes(hours.from)
		&& minutes <= room_booking_time_within_hours._to_minutes(hours.to);
};
room_booking_time_within_hours._fetch_admin_hours();

frappe.views.calendar["Room Booking"] = {
    field_map: {
		start: "from_datetime",
		end: "end_datetime",
		id: "name",
		title: "title",
		color:"color"
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

	options: {
		select: function(startDate, endDate, jsEvent, view) {
			// Single day click in month view — let dayClick handle it, ignore here
			if (view.name === "month" && endDate - startDate === 86400000) return;

			const today = moment().format('YYYY-MM-DD');
			const startStr = startDate.format('YYYY-MM-DD');
			// Block past dates
			if (startStr < today) {
				frappe.show_alert({ message: __('Booking on past dates is not allowed.'), indicator: 'red' });
				return;
			}
			// Block past time slots on today
			if (startStr === today && startDate.isBefore(moment())) {
				frappe.show_alert({ message: __('Booking for past times is not allowed.'), indicator: 'red' });
				return;
			}
			// Block slots outside Admin Setting's configured booking hours window
			room_booking_time_within_hours._fetch_admin_hours().then((hours) => {
				if (view.name !== "month" &&
					(!room_booking_time_within_hours(startDate) || !room_booking_time_within_hours(endDate))) {
					frappe.show_alert({
						message: __('Booking is only allowed from {0} to {1}.', [hours.from, hours.to]),
						indicator: 'red'
					});
					return;
				}
				var event = frappe.model.get_new_doc("Room Booking");
				event["from_datetime"] = startDate.format("YYYY-MM-DD HH:mm:ss");
				event["end_datetime"]  = endDate.format("YYYY-MM-DD HH:mm:ss");
				frappe.set_route("Form", "Room Booking", event.name);
			});
		},
		dayClick: function(date, jsEvent, view) {
			const today = moment().format('YYYY-MM-DD');
			const dateStr = date.format('YYYY-MM-DD');
			if (dateStr < today) {
				frappe.show_alert({ message: __('Booking on past dates is not allowed.'), indicator: 'red' });
				return false;
			}
			// In day/week view, a click on a past time slot should also be blocked
			if (view.name !== "month" && dateStr === today && date.isBefore(moment())) {
				frappe.show_alert({ message: __('Booking for past times is not allowed.'), indicator: 'red' });
				return false;
			}
			// Default month-view drill-down behaviour — use DOM directly (no Frappe `this`)
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