// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

if (!document.getElementById('ts-picker-styles')) {
	const style = document.createElement('style');
	style.id = 'ts-picker-styles';
	style.textContent = `
		.time-slot-grid {
			display: flex;
			flex-wrap: wrap;
			gap: 8px;
			padding: 12px 0;
			max-height: 360px;
			overflow-y: auto;
		}
		.time-slot-btn {
			width: calc(25% - 6px);
			padding: 8px 4px;
			border: 1px solid #d1d8dd;
			border-radius: 6px;
			background: #fff;
			cursor: pointer;
			font-size: 12px;
			text-align: center;
			transition: background 0.15s, border-color 0.15s;
			white-space: nowrap;
			box-sizing: border-box;
		}
		.time-slot-btn:hover:not([disabled]) {
			border-color: #5e64ff;
			background: #f0f1ff;
		}
		.time-slot-btn.ts-from {
			background: #5e64ff;
			color: #fff;
			border-color: #5e64ff;
			font-weight: 600;
		}
		.time-slot-btn.ts-to {
			background: #2490ef;
			color: #fff;
			border-color: #2490ef;
			font-weight: 600;
		}
		.time-slot-btn.ts-range {
			background: #d1e8ff;
			border-color: #a0c8f5;
		}
		.time-slot-btn.ts-disabled,
		.time-slot-btn[disabled] {
			background: #f4f5f6;
			color: #b8bfc9;
			border-color: #e4e6ea;
			cursor: not-allowed;
			text-decoration: line-through;
		}
		.ts-status {
			padding: 10px 0 4px;
			font-size: 13px;
			color: #333;
			min-height: 28px;
		}
	`;
	document.head.appendChild(style);
}

const ALL_TIMES = [
	"12:00 AM","12:30 AM","01:00 AM","01:30 AM","02:00 AM","02:30 AM",
	"03:00 AM","03:30 AM","04:00 AM","04:30 AM","05:00 AM","05:30 AM",
	"06:00 AM","06:30 AM","07:00 AM","07:30 AM","08:00 AM","08:30 AM",
	"09:00 AM","09:30 AM","10:00 AM","10:30 AM","11:00 AM","11:30 AM",
	"12:00 PM","12:30 PM","01:00 PM","01:30 PM","02:00 PM","02:30 PM",
	"03:00 PM","03:30 PM","04:00 PM","04:30 PM","05:00 PM","05:30 PM",
	"06:00 PM","06:30 PM","07:00 PM","07:30 PM","08:00 PM","08:30 PM",
	"09:00 PM","09:30 PM","10:00 PM","10:30 PM","11:00 PM","11:30 PM"
];


function time_to_minutes(t) {
	const match = t.match(/^(\d{2}):(\d{2}) (AM|PM)$/);
	if (!match) return -1;
	let h = parseInt(match[1]);
	const m = parseInt(match[2]);
	const period = match[3];
	if (period === "AM" && h === 12) h = 0;
	if (period === "PM" && h !== 12) h += 12;
	return h * 60 + m;
}

function get_disabled_slots(booked_slots) {
	const disabled = new Set();
	booked_slots.forEach(function(b) {
		const b_from = time_to_minutes(b.from_time);
		const b_to   = time_to_minutes(b.end_time);
		ALL_TIMES.forEach(function(t) {
			const tm = time_to_minutes(t);
			if (tm >= b_from && tm < b_to) {
				disabled.add(t);
			}
		});
	});
	return disabled;
}

function is_range_blocked(from_min, to_min, booked_slots) {
	return booked_slots.some(function(b) {
		const b_from = time_to_minutes(b.from_time);
		const b_to   = time_to_minutes(b.end_time);
		return b_from < to_min && b_to > from_min;
	});
}

function build_time_grid_html(visible_slots, disabled_set, from_sel, to_sel, max_booking_hours) {
	const from_min = from_sel ? time_to_minutes(from_sel) : -1;
	const to_min   = to_sel   ? time_to_minutes(to_sel)   : -1;
	const max_end_min = (from_min !== -1 && max_booking_hours) ? from_min + (max_booking_hours * 60) : -1;

	let html = '<div class="time-slot-grid">';
	visible_slots.forEach(function(t) {
		const tm = time_to_minutes(t);
		// After from is selected, disable slots beyond max booking hours
		const beyond_max = from_sel && !to_sel && max_end_min !== -1 && tm > max_end_min;
		const is_disabled = disabled_set.has(t) || beyond_max;
		let cls = 'time-slot-btn';
		if (is_disabled) {
			cls += ' ts-disabled';
		} else if (t === from_sel) {
			cls += ' ts-from';
		} else if (t === to_sel) {
			cls += ' ts-to';
		} else if (from_min !== -1 && to_min !== -1 && tm > from_min && tm < to_min) {
			cls += ' ts-range';
		}
		html += `<button class="${cls}" data-time="${t}" ${is_disabled ? 'disabled' : ''}>${t}</button>`;
	});
	html += '</div>';

	let status_text = '';
	if (from_sel && to_sel) {
		status_text = `Selected: <strong>${from_sel}</strong> &rarr; <strong>${to_sel}</strong>`;
	} else if (from_sel) {
		let max_note = '';
		if (max_booking_hours) {
			max_note = ` &nbsp;<span style="color:#e24c4c;font-size:11px;">(max ${max_booking_hours} hr${max_booking_hours !== 1 ? 's' : ''})</span>`;
		}
		status_text = `From: <strong>${from_sel}</strong> &mdash; now click an end time${max_note}`;
	} else {
		let max_note = max_booking_hours ? ` &nbsp;<span style="color:#e24c4c;font-size:11px;">Max booking: ${max_booking_hours} hr${max_booking_hours !== 1 ? 's' : ''}</span>` : '';
		status_text = `Click a slot to set the start time.${max_note}`;
	}
	html += `<div class="ts-status">${status_text}</div>`;
	return html;
}

function open_time_picker_dialog(frm) {
	if (!frm.doc.select_room_type || !frm.doc.from_date) {
		frappe.msgprint(__('Please select a Room and From Date before choosing a time.'));
		return;
	}

	// Local to this dialog open — not shared across opens
	let picker_from = frm.doc.from_time || null;
	let picker_to   = frm.doc.end_time  || null;

	frappe.call({
		method: 'rental.rental.doctype.room_booking.room_booking.get_time_picker_data',
		args: { room: frm.doc.select_room_type, date: frm.doc.from_date },
		callback: function(r) {
			if (!r.message) return;

			const { admin_from, admin_to, booked_slots, is_today, current_minutes, max_booking_hours } = r.message;
			const booked = booked_slots || [];

			let visible_slots;
			if (admin_from && admin_to) {
				const af_min = time_to_minutes(admin_from);
				const at_min = time_to_minutes(admin_to);
				visible_slots = ALL_TIMES.filter(t => {
					const tm = time_to_minutes(t);
					return tm >= af_min && tm <= at_min;
				});
			} else {
				visible_slots = ALL_TIMES.slice();
			}

			const disabled_set = get_disabled_slots(booked);

			// Disable past times when booking date is today (server decides is_today)
			if (is_today) {
				visible_slots.forEach(function(t) {
					if (time_to_minutes(t) < current_minutes) {
						disabled_set.add(t);
					}
				});
				// Clear picker selections if they are now in the past
				if (picker_from && time_to_minutes(picker_from) < current_minutes) {
					picker_from = null;
					picker_to   = null;
				}
			}

			const d = new frappe.ui.Dialog({
				title: __('Select Booking Time'),
				fields: [
					{
						fieldtype: 'HTML',
						fieldname: 'time_grid_html',
						options: build_time_grid_html(visible_slots, disabled_set, picker_from, picker_to, max_booking_hours)
					}
				],
				primary_action_label: __('Confirm'),
				primary_action: function() {
					if (!picker_from || !picker_to) {
						frappe.msgprint(__('Please select both a start time and an end time.'));
						return;
					}
					frm.set_value('from_time', picker_from);
					frm.set_value('end_time',  picker_to);
					frm.set_value('selected_time_display', `${picker_from} → ${picker_to}`);
					d.hide();
				}
			});

			d.show();

			// Single delegated handler on stable modal-body — never needs rebinding.
			const $dialog_body = d.$wrapper.find('.modal-body');
			$dialog_body.on('click', '.time-slot-btn:not([disabled])', function() {
				const clicked_time = $(this).data('time');
				const clicked_min  = time_to_minutes(clicked_time);

				if (picker_from === null) {
					picker_from = clicked_time;
					picker_to   = null;
				} else if (picker_to === null) {
					const from_min = time_to_minutes(picker_from);
					if (clicked_min <= from_min) {
						picker_from = clicked_time;
						picker_to   = null;
					} else if (is_range_blocked(from_min, clicked_min, booked)) {
						frappe.show_alert({
							message: __('Your selected range overlaps a booked slot. Please choose a different range.'),
							indicator: 'red'
						});
						picker_from = null;
						picker_to   = null;
					} else {
						picker_to = clicked_time;
					}
				} else {
					picker_from = clicked_time;
					picker_to   = null;
				}

				d.fields_dict['time_grid_html'].$wrapper.html(
					build_time_grid_html(visible_slots, disabled_set, picker_from, picker_to, max_booking_hours)
				);
			});
		}
	});
}

function apply_time_filter(frm, today_server, current_minutes) {
	const from_date = frm.doc.from_date;
	if (from_date && from_date === today_server) {
		const filtered = ALL_TIMES.filter(t => time_to_minutes(t) >= current_minutes);
		frm.set_df_property("from_time", "options", "\n" + filtered.join("\n"));
		if (frm.doc.from_time && !filtered.includes(frm.doc.from_time)) {
			frm.set_value("from_time", "");
			frm.set_value("end_time", "");
			frm.set_value("selected_time_display", "");
		}
	} else {
		frm.set_df_property("from_time", "options", "\n" + ALL_TIMES.join("\n"));
	}
	filter_end_time_options(frm);
}

function filter_end_time_options(frm) {
	const from_time = frm.doc.from_time;
	if (from_time) {
		const from_minutes = time_to_minutes(from_time);
		const filtered = ALL_TIMES.filter(t => time_to_minutes(t) > from_minutes);
		frm.set_df_property("end_time", "options", "\n" + filtered.join("\n"));
		if (frm.doc.end_time && !filtered.includes(frm.doc.end_time)) {
			frm.set_value("end_time", "");
		}
	} else {
		frm.set_df_property("end_time", "options", "\n" + ALL_TIMES.join("\n"));
	}
}

function filter_from_time_options(frm) {
	frappe.call({
		method: "rental.rental.doctype.room_booking.room_booking.get_current_time",
		callback: function(r) {
			if (r.message) {
				const { today, hours, minutes } = r.message;
				apply_time_filter(frm, today, hours * 60 + minutes);
			}
		}
	});
}

function rb_is_weekend(date_str) {
	if (!date_str) return false;
	const d = new Date(date_str);
	const day = d.getDay(); // 0=Sun, 6=Sat
	return day === 0 || day === 6;
}

frappe.ui.form.on('Room Booking', {
	onload: function(frm) {
		// Auto-set customer based on logged-in user on new docs
		if (frm.is_new() && !frm.doc.customer) {
			frappe.call({
				method: "rental.rental.doctype.room_booking.room_booking.check_log_in_user",
				args: { user: frappe.session.user },
				callback: function(r) {
					if (r.message && !frm.doc.customer) {
						frm.set_value('customer', r.message);
					}
				}
			});
		}

		// When opened from calendar slot click, from_datetime / end_datetime are pre-set
		// as local "YYYY-MM-DD HH:mm:ss" strings. Parse them directly with moment.
		if (frm.is_new() && frm.doc.from_datetime) {
			const start = moment(frm.doc.from_datetime, "YYYY-MM-DD HH:mm:ss");
			const end   = frm.doc.end_datetime ? moment(frm.doc.end_datetime, "YYYY-MM-DD HH:mm:ss") : null;
			const fmt_time = (m) => m.format("hh:mm A");  // e.g. "12:00 AM", "01:30 PM"
			const from_time_val = fmt_time(start);
			const end_time_val  = end ? fmt_time(end) : null;

			// Use a flag so the from_date handler skips clearing time values
			frm._calendar_prefill = true;
			frm.set_value('from_date', start.format("YYYY-MM-DD"));
			if (end) frm.set_value('end_date', end.format("YYYY-MM-DD"));

			// filter_from_time_options makes a server call; set times after it resolves
			frappe.call({
				method: "rental.rental.doctype.room_booking.room_booking.get_current_time",
				callback: function(r) {
					frm._calendar_prefill = false;
					if (r.message) {
						const { today, hours, minutes } = r.message;
						apply_time_filter(frm, today, hours * 60 + minutes);
					}
					frm.set_value('from_time', from_time_val);
					if (end_time_val) {
						frm.set_value('end_time', end_time_val);
						frm.set_value('selected_time_display', `${from_time_val} → ${end_time_val}`);
					}
				}
			});
		}
	},

	setup: function(frm) {
		frm.set_query("select_room_type", function() {
			return {
				query: "rental.rental.doctype.room_booking.room_booking.get_rooms",
				filters: { customer: frm.doc.customer }
			};
		});
		frm.set_query("customer", () => {
			return { page_length: 100 };
		});
	},

	refresh: function(frm) {
		// Disable Saturday (6) and Sunday (0) in both date pickers
		['from_date', 'end_date'].forEach(function(fieldname) {
			const field = frm.get_field(fieldname);
			if (field && field.datepicker) {
				try {
					field.datepicker.update('onBeforeSelect', function(fd, d) {
						return d.getDay() !== 0 && d.getDay() !== 6;
					});
				} catch(e) {
					// datepicker not yet initialised — skip silently
				}
			}
		});

		if (frm.is_new()) filter_from_time_options(frm);

		frm.add_custom_button(__('Check Availablity'), function() {
			window.open(`${window.location.origin}/app/room-booking/view/calendar/default?select_room_type=${frm.doc.select_room_type}`);
		});

		frappe.call({
			method: "rental.rental.doctype.room_booking.room_booking.check_log_in_user",
			args: { user: frappe.session.user },
			callback: function(r) {
				if (frm.is_new() && !frm.doc.customer) {
					frm.set_value('customer', r.message);
				}
			}
		});

		if (frm.is_new()) {
			frm.call({
				method: "set_from_end_time",
				args: { self: frm.doc },
				callback: function(r) {
					if (r.message) {
						frm.set_value(r.message);
					}
				}
			});
		}

		frappe.call({
			method: "rental.api.check_roles",
			callback: function(r) {
				if (!r.message) {
					frm.set_df_property('customer', 'read_only', 1);
				}
			}
		});

		if (frm.is_new() && frm.doc.from_time && frm.doc.end_time) {
			frm.set_value('selected_time_display', `${frm.doc.from_time} → ${frm.doc.end_time}`);
		}

		frm.set_df_property('time_picker_btn', 'hidden', frm.doc.docstatus === 0 ? 0 : 1);
	},

	after_save: function(frm) {
		frm.set_df_property('time_picker_btn', 'hidden', frm.doc.docstatus === 0 ? 0 : 1);
	},

	onload_post_render: function(frm) {
		frm.set_df_property('time_picker_btn', 'hidden', frm.doc.docstatus === 0 ? 0 : 1);
	},

	time_picker_btn: function(frm) {
		open_time_picker_dialog(frm);
	},

	from_date: function(frm) {
		if (frm.doc.from_date) {
			const selected = new Date(frm.doc.from_date);
			const today = new Date();
			if (selected.getMonth() !== today.getMonth() || selected.getFullYear() !== today.getFullYear()) {
				const current_month = today.toLocaleString('default', { month: 'long', year: 'numeric' });
				frappe.show_alert({
					message: __('Oops! Your credits are available for {0} only. Please choose a date within the current month.', [current_month]),
					indicator: 'orange'
				}, 5);
				frm.set_value("from_date", "");
				frm.set_value("end_date", "");
				return;
			}
		}
		if (rb_is_weekend(frm.doc.from_date)) {
			frappe.show_alert({ message: __('Bookings are only allowed on weekdays (Monday – Friday). Please select a valid From Date.'), indicator: 'red' });
			frm.set_value("from_date", "");
			frm.set_value("end_date", "");
			return;
		}
		frm.set_value("end_date", frm.doc.from_date);
		// Skip clearing times when pre-filling from calendar slot click
		if (!frm._calendar_prefill) {
			frm.set_value("from_time", "");
			frm.set_value("end_time", "");
			frm.set_value("selected_time_display", "");
			filter_from_time_options(frm);
		}
	},

	customer: function(frm) {
		frm.set_value("select_room_type", "");
	}
});
