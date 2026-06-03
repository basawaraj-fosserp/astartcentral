// Copyright (c) 2023, Viral Patel and contributors
// For license information, please see license.txt

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

function eqb_apply_time_filter(frm, today_server, current_minutes) {
	const from_date = frm.doc.from_date;
	if (from_date && from_date === today_server) {
		const filtered = EQB_ALL_TIMES.filter(t => {
			const match = t.match(/^(\d{2}):(\d{2}) (AM|PM)$/);
			if (!match) return false;
			let h = parseInt(match[1]);
			const m = parseInt(match[2]);
			const period = match[3];
			if (period === "AM" && h === 12) h = 0;
			if (period === "PM" && h !== 12) h += 12;
			return (h * 60 + m) >= current_minutes;
		});
		frm.set_df_property("from_time", "options", "\n" + filtered.join("\n"));
		if (frm.doc.from_time && !filtered.includes(frm.doc.from_time)) {
			frm.set_value("from_time", "");
		}
	} else {
		frm.set_df_property("from_time", "options", "\n" + EQB_ALL_TIMES.join("\n"));
	}
}

function eqb_filter_from_time_options(frm) {
	frappe.call({
		method: "rental.rental.doctype.room_booking.room_booking.get_current_time",
		callback: function(r) {
			if (r.message) {
				const { today, hours, minutes } = r.message;
				eqb_apply_time_filter(frm, today, hours * 60 + minutes);
			}
		}
	});
}

frappe.ui.form.on('Equipment Booking', {
	setup:function(frm){
		frm.set_query("equipment", "equipment", function() {
			return {
				query: "rental.rental.doctype.equipment_booking.equipment_booking.get_equipment",
				filters: {
					customer: frm.doc.customer
				}
			};
		});
	},
	refresh:function(frm){
		eqb_filter_from_time_options(frm);
		frappe.call({
			method:"rental.rental.doctype.room_booking.room_booking.check_log_in_user",
			args:{
				user:frappe.session.user
			},
			callback:function(r){
				if (r.message) {
					// non-admin: hide and auto-fill customer only on new doc
					frm.set_df_property('customer', 'hidden', 1);
					if (frm.is_new() && !frm.doc.customer) {
						frm.set_value('customer', r.message);
					}
				} else {
					// admin: customer field visible and editable
					frm.set_df_property('customer', 'hidden', 0);
				}
			}
		})
		frm.call({
			method:"set_from_end_time",
			args:{
				self:frm.doc
			},
			callback:function() {

			}
		})
		
	},
	from_date:function(frm){
		frm.set_value("to_date" , frm.doc.from_date);
		eqb_filter_from_time_options(frm);
	},
	from_time:function(frm){
		if(!frm.doc.to_time){
		frm.set_value('to_time' , frm.doc.from_time)
		}
	},
	customer:function(frm){
		frm.clear_table("equipment");
		frm.refresh_field("equipment");
	}
});