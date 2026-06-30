// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

if (!document.getElementById('eqb-picker-styles')) {
	const style = document.createElement('style');
	style.id = 'eqb-picker-styles';
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

const EQB_ALL_TIMES = [
	"12:00 AM","12:30 AM","01:00 AM","01:30 AM","02:00 AM","02:30 AM",
	"03:00 AM","03:30 AM","04:00 AM","04:30 AM","05:00 AM","05:30 AM",
	"06:00 AM","06:30 AM","07:00 AM","07:30 AM","08:00 AM","08:30 AM",
	"09:00 AM","09:30 AM","10:00 AM","10:30 AM","11:00 AM","11:30 AM",
	"12:00 PM","12:30 PM","01:00 PM","01:30 PM","02:00 PM","02:30 PM",
	"03:00 PM","03:30 PM","04:00 PM","04:30 PM","05:00 PM","05:30 PM",
	"06:00 PM","06:30 PM","07:00 PM","07:30 PM","08:00 PM","08:30 PM",
	"09:00 PM","09:30 PM","10:00 PM","10:30 PM","11:00 PM","11:30 PM"
];

function eqb_time_to_minutes(t) {
	const match = t.match(/^(\d{2}):(\d{2}) (AM|PM)$/);
	if (!match) return -1;
	let h = parseInt(match[1]);
	const m = parseInt(match[2]);
	const period = match[3];
	if (period === "AM" && h === 12) h = 0;
	if (period === "PM" && h !== 12) h += 12;
	return h * 60 + m;
}

function eqb_get_disabled_slots(booked_slots) {
	const disabled = new Set();
	booked_slots.forEach(function(b) {
		const b_from = eqb_time_to_minutes(b.from_time);
		const b_to   = eqb_time_to_minutes(b.to_time);
		EQB_ALL_TIMES.forEach(function(t) {
			const tm = eqb_time_to_minutes(t);
			if (tm >= b_from && tm < b_to) {
				disabled.add(t);
			}
		});
	});
	return disabled;
}

function eqb_is_range_blocked(from_min, to_min, booked_slots) {
	return booked_slots.some(function(b) {
		const b_from = eqb_time_to_minutes(b.from_time);
		const b_to   = eqb_time_to_minutes(b.to_time);
		return b_from < to_min && b_to > from_min;
	});
}

function eqb_build_time_grid_html(visible_slots, disabled_set, from_sel, to_sel) {
	const from_min = from_sel ? eqb_time_to_minutes(from_sel) : -1;
	const to_min   = to_sel   ? eqb_time_to_minutes(to_sel)   : -1;

	let html = '<div class="time-slot-grid">';
	visible_slots.forEach(function(t) {
		const tm = eqb_time_to_minutes(t);
		const is_disabled = disabled_set.has(t);
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
		status_text = `From: <strong>${from_sel}</strong> &mdash; now click an end time`;
	} else {
		status_text = 'Click a slot to set the start time.';
	}
	html += `<div class="ts-status">${status_text}</div>`;
	return html;
}

function open_eqb_time_picker_dialog(frm) {
	if (!frm.doc.equipment || !frm.doc.from_date) {
		frappe.msgprint(__('Please select an Equipment and From Date before choosing a time.'));
		return;
	}

	let picker_from = frm.doc.from_time || null;
	let picker_to   = frm.doc.to_time   || null;

	frappe.call({
		method: 'rental.rental.doctype.equipment_booking.equipment_booking.get_booked_slots',
		args: {
			equipment:    frm.doc.equipment,
			date:         frm.doc.from_date,
			serial_no:    frm.doc.serial_no || null,
			exclude_name: frm.doc.name || null
		},
		callback: function(r) {
			if (!r.message) return;

			const booked = r.message || [];

			frappe.call({
				method: 'rental.rental.doctype.equipment_booking.equipment_booking.get_current_server_time',
				args: { from_date: frm.doc.from_date },
				callback: function(sr) {
					const { is_today, current_minutes } = sr.message || {};

					// All 48 slots visible (full 24h, no admin window filter)
					const visible_slots = EQB_ALL_TIMES.slice();
					const disabled_set  = eqb_get_disabled_slots(booked);

					// Disable past slots when date is today
					if (is_today) {
						visible_slots.forEach(function(t) {
							if (eqb_time_to_minutes(t) < current_minutes) {
								disabled_set.add(t);
							}
						});
						if (picker_from && eqb_time_to_minutes(picker_from) < current_minutes) {
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
								options: eqb_build_time_grid_html(visible_slots, disabled_set, picker_from, picker_to)
							}
						],
						primary_action_label: __('Confirm'),
						primary_action: function() {
							if (!picker_from || !picker_to) {
								frappe.msgprint(__('Please select both a start time and an end time.'));
								return;
							}
							frm.set_value('from_time', picker_from);
							frm.set_value('to_time',   picker_to);
							frm.set_value('selected_time_display', `${picker_from} → ${picker_to}`);
							d.hide();
						}
					});

					d.show();

					// Single delegated handler on stable modal-body
					const $dialog_body = d.$wrapper.find('.modal-body');
					$dialog_body.on('click', '.time-slot-btn:not([disabled])', function() {
						const clicked_time = $(this).data('time');
						const clicked_min  = eqb_time_to_minutes(clicked_time);

						if (picker_from === null) {
							picker_from = clicked_time;
							picker_to   = null;
						} else if (picker_to === null) {
							const from_min = eqb_time_to_minutes(picker_from);
							if (clicked_min <= from_min) {
								picker_from = clicked_time;
								picker_to   = null;
							} else if (eqb_is_range_blocked(from_min, clicked_min, booked)) {
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
							eqb_build_time_grid_html(visible_slots, disabled_set, picker_from, picker_to)
						);
					});
				}
			});
		}
	});
}

function eqb_is_weekend(date_str) {
	if (!date_str) return false;
	const d = new Date(date_str);
	const day = d.getDay(); // 0=Sun, 6=Sat
	return day === 0 || day === 6;
}

frappe.ui.form.on('Equipment Booking', {
	setup: function(frm) {
		frm.set_query("equipment", function() {
			return {
				query: "rental.rental.doctype.equipment_booking.equipment_booking.get_equipment",
				filters: { customer: frm.doc.customer }
			};
		});
	},

	refresh: function(frm) {
		// Disable Saturday (6) and Sunday (0) in both date pickers
		['from_date', 'to_date'].forEach(function(fieldname) {
			const field = frm.get_field(fieldname);
			if (field && field.datepicker) {
				field.datepicker.set('disable', [
					function(date) { return date.getDay() === 0 || date.getDay() === 6; }
				]);
			}
		});

		frappe.call({
			method: "rental.rental.doctype.room_booking.room_booking.check_log_in_user",
			args: { user: frappe.session.user },
			callback: function(r) {
				if (r.message) {
					frm.set_df_property('customer', 'hidden', 1);
					if (frm.is_new() && !frm.doc.customer) {
						frm.set_value('customer', r.message);
					}
				} else {
					frm.set_df_property('customer', 'hidden', 0);
				}
			}
		});

		if (frm.doc.docstatus === 0) {
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

		// Keep selected_time_display in sync on load
		if (frm.doc.from_time && frm.doc.to_time && frm.doc.docstatus === 0) {
			frm.set_value('selected_time_display', `${frm.doc.from_time} → ${frm.doc.to_time}`);
		}

		frm.set_df_property('time_picker_btn', 'hidden', frm.doc.docstatus === 0 ? 0 : 1);
	},

	after_save: function(frm) {
		frm.set_df_property('time_picker_btn', 'hidden', frm.doc.docstatus === 0 ? 0 : 1);
	},

	onload_post_render: function(frm) {
		frm.set_df_property('time_picker_btn', 'hidden', frm.doc.docstatus === 0 ? 0 : 1);
	},

	// Button field event — fires when the "Select Time" button is clicked
	time_picker_btn: function(frm) {
		open_eqb_time_picker_dialog(frm);
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
				frm.set_value("to_date", "");
				return;
			}
		}
		if (eqb_is_weekend(frm.doc.from_date)) {
			frappe.show_alert({ message: __('Bookings are only allowed on weekdays (Monday – Friday). Please select a valid From Date.'), indicator: 'red' });
			frm.set_value("from_date", "");
			frm.set_value("to_date", "");
			return;
		}
		frm.set_value("to_date", frm.doc.from_date);
		frm.set_value("from_time", "");
		frm.set_value("to_time", "");
		frm.set_value("selected_time_display", "");
	},

	equipment: function(frm) {
		frm.set_value("from_time", "");
		frm.set_value("to_time", "");
		frm.set_value("selected_time_display", "");
		if (frm.doc.equipment) {
			frappe.db.get_value("Equipment", frm.doc.equipment, "custom_a_asset_serial_no", function(r) {
				frm.set_value("serial_no", r && r.custom_a_asset_serial_no ? r.custom_a_asset_serial_no : "");
			});
		} else {
			frm.set_value("serial_no", "");
		}
	},

	customer: function(frm) {
		frm.set_value("equipment", "");
		frm.set_value("serial_no", "");
		frm.set_value("from_time", "");
		frm.set_value("to_time", "");
		frm.set_value("selected_time_display", "");
	}
});
