console.log("viral")

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
        
                this.page.add_inner_button(__("Create Workspace"))
            }
        })
	}
}