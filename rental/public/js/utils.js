console.log("viral")

// Restrict view switcher to List and Calendar only for booking doctypes
const RENTAL_BOOKING_DOCTYPES = ["Room Booking", "Equipment Booking"];
const RENTAL_ALLOWED_VIEWS = ["List", "Calendar"];

frappe.after_ajax(() => {
	const _original_setup_views = frappe.views.ListViewSelect.prototype.setup_views;
	frappe.views.ListViewSelect.prototype.setup_views = function() {
		_original_setup_views.call(this);
		if (RENTAL_BOOKING_DOCTYPES.includes(this.doctype)) {
			$(this.parent).find("li[data-view]").each(function() {
				if (!RENTAL_ALLOWED_VIEWS.includes($(this).attr("data-view"))) {
					$(this).hide();
				}
			});
		}
	};
});

frappe.views.Workspace = class Workspace extends frappe.views.Workspace {
    setup_actions(page) {
		let pages = page.public ? this.public_pages : this.private_pages;
		let current_page = pages.filter((p) => p.title == page.name)[0];

		if (!this.is_read_only) {
			this.setup_customization_buttons(current_page);
			return;
		}

		this.clear_page_actions();
        frappe.call({
            method:"rental.api.check_roles",
            callback:function(r){
                var d = r.message
            }
        }).then((d) => {
            if (d.message){
                this.page.set_secondary_action(__("Edit"), async () => {
                    if (!this.editor || !this.editor.readOnly) return;
                    this.is_read_only = false;
                    this.toggle_hidden_workspaces(true);
                    await this.editor.readOnly.toggle();
                    this.editor.isReady.then(() => {
                        this.initialize_editorjs_undo();
                        this.setup_customization_buttons(current_page);
                        this.show_sidebar_actions();
                        this.make_blocks_sortable();
                    });
                });
                this.page.add_inner_button(__("Create Workspace"), () => {
                    this.initialize_new_page();
                });
            }
        })
	}
}