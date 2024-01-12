# Copyright (c) 2023, Viral Patel and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document

class Room(Document):
	def on_update(self):
		data = frappe.db.exists("Web Page" , self.name)

		web_template_values = {'image':'/files/Your Office Makes Your Staff More Productive, 8 Ways How.webp','document_type':'Room','document_name':self.name}
		web_template_values = json.dumps(web_template_values)

		if not data:
			doc = frappe.new_doc("Web Page")
			doc.title = self.name
			doc.published = 1
			doc.module = 'rental'
			doc.content_type = 'Page Builder'
			doc.append('page_blocks',{
				"web_template":"Show Booking Availability",
				"web_template_values":web_template_values,
				"add_background_image": 0,
				"add_border_at_bottom": 0,
				"add_border_at_top": 0,
				"add_bottom_padding":0,
				"add_container":0,
				"add_shade":0,
				"add_top_padding":0,
				
			})
			doc.save(ignore_permissions = 1)

