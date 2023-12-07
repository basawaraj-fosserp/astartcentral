


function on_date_or_timezone_select() {
    let date_picker = document.getElementById('appointment-date');
    let timezone = document.getElementById('appointment-timezone');
    if (date_picker.value === '') {
        clear_time_slots();
        hide_next_button();
        frappe.throw(__('Please select a date'));
    }
    window.selected_date = date_picker.value;
    window.selected_timezone = timezone.value;
    update_time_slots(date_picker.value, timezone.value);
    let lead_text = document.getElementById('lead-text');
    lead_text.innerHTML = "Select Time"
}