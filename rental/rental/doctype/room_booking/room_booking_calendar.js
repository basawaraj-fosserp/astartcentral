function rb_ampm_to_minutes(time_str) {
	// Converts "09:00 AM" / "06:00 PM" to total minutes from midnight
	const match = time_str.match(/^(\d{1,2}):(\d{2})\s*(AM|PM)$/i);
	if (!match) return 0;
	let h = parseInt(match[1]);
	const m = parseInt(match[2]);
	const period = match[3].toUpperCase();
	if (period === 'AM' && h === 12) h = 0;
	if (period === 'PM' && h !== 12) h += 12;
	return h * 60 + m;
}

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
		viewRender: function() {
			// Fetch server time once and store offset + admin booking window
			if (frappe._rb_server_offset_ms !== undefined) return;
			frappe.call({
				method: 'rental.rental.doctype.room_booking.room_booking.get_current_time',
				callback: function(r) {
					if (r.message) {
						const { today, hours, minutes, admin_from, admin_to } = r.message;
						const server_now = moment(today + ' ' + String(hours).padStart(2,'0') + ':' + String(minutes).padStart(2,'0'), 'YYYY-MM-DD HH:mm');
						frappe._rb_server_offset_ms = server_now.valueOf() - moment().valueOf();
						frappe._rb_admin_from = admin_from || null;
						frappe._rb_admin_to   = admin_to   || null;
					}
				}
			});
		},

		select: function(startDate, endDate, jsEvent, view) {
			// Single day click in month view — let dayClick handle it, ignore here
			if (view.name === "month" && endDate - startDate === 86400000) return;

			const now = moment().add(frappe._rb_server_offset_ms || 0, 'ms');
			const today = now.format('YYYY-MM-DD');
			const startStr = startDate.format('YYYY-MM-DD');
			if (startStr < today) {
				frappe.show_alert({ message: __('Booking on past dates is not allowed.'), indicator: 'red' });
				return;
			}
			if (startStr === today && startDate.isBefore(now)) {
				frappe.show_alert({ message: __('Booking for past times is not allowed.'), indicator: 'red' });
				return;
			}
			// Enforce admin booking hours window
			if (frappe._rb_admin_from && frappe._rb_admin_to) {
				const slot_from_min = startDate.hours() * 60 + startDate.minutes();
				const slot_to_min   = endDate.hours() * 60 + endDate.minutes();
				const admin_from_min = rb_ampm_to_minutes(frappe._rb_admin_from);
				const admin_to_min   = rb_ampm_to_minutes(frappe._rb_admin_to);
				if (slot_from_min < admin_from_min || slot_to_min > admin_to_min) {
					frappe.show_alert({
						message: __('Bookings are only allowed between {0} and {1}.', [frappe._rb_admin_from, frappe._rb_admin_to]),
						indicator: 'red'
					});
					return;
				}
			}
			var event = frappe.model.get_new_doc("Room Booking");
			event["from_datetime"] = startDate.format("YYYY-MM-DD HH:mm:ss");
			event["end_datetime"]  = endDate.format("YYYY-MM-DD HH:mm:ss");
			frappe.set_route("Form", "Room Booking", event.name);
		},
		dayClick: function(date, jsEvent, view) {
			const now = moment().add(frappe._rb_server_offset_ms || 0, 'ms');
			const today = now.format('YYYY-MM-DD');
			const dateStr = date.format('YYYY-MM-DD');
			if (dateStr < today) {
				frappe.show_alert({ message: __('Booking on past dates is not allowed.'), indicator: 'red' });
				return false;
			}
			if (view.name !== "month" && dateStr === today && date.isBefore(now)) {
				frappe.show_alert({ message: __('Booking for past times is not allowed.'), indicator: 'red' });
				return false;
			}
			// Enforce admin booking hours window in day/week view
			if (view.name !== "month" && frappe._rb_admin_from && frappe._rb_admin_to) {
				const slot_min     = date.hours() * 60 + date.minutes();
				const admin_from_min = rb_ampm_to_minutes(frappe._rb_admin_from);
				const admin_to_min   = rb_ampm_to_minutes(frappe._rb_admin_to);
				if (slot_min < admin_from_min || slot_min >= admin_to_min) {
					frappe.show_alert({
						message: __('Bookings are only allowed between {0} and {1}.', [frappe._rb_admin_from, frappe._rb_admin_to]),
						indicator: 'red'
					});
					return false;
				}
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
