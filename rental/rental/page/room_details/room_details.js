frappe.pages['room-details'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Rooms',
		single_column: true
	});
	page.title_field = page.add_field({
		fieldname: 'title',
		label: __('Title'),
		fieldtype:'Link',
		options:'Room',
		onchange:function(){
			frappe.room_details.make(page);
		}
	});
	frappe.room_details.make(page);
}


frappe.room_details = {
	make:function(page){
		var me = frappe.room_details;
		me.page = page;
		me.body = $('<div></div>').appendTo(me.page.main);
		console.log(page.title_field.get_value())
		frappe.call({
			method: "rental.rental.page.room_details.room_details.get_room_data",
			args:{
				'room' : page.title_field.get_value()
			},
			callback:function(r){
				var data = {'data':r.message};
				$(frappe.render_template('room_details', data)).appendTo(me.body);
			}
		})
		me.page.add_inner_button(__('+ Add Room'), function () {
			frappe.new_doc("Room")
		}).addClass("btn-primary");
		me.page.add_inner_button(__('Export Excel'), function () {
			frappe.call({
				method:"rental.rental.page.room_details.room_details.get_room_data_for_excel",
				args:{
					
				},
				callback:function(r){
					data = r.message
					var wb = XLSX.utils.book_new();
					var ws = XLSX.utils.aoa_to_sheet(data);

					// Add the worksheet to the workbook
					XLSX.utils.book_append_sheet(wb, ws, "Sheet1");

					// Convert the workbook to a Blob
					var wbString = XLSX.write(wb, { bookType: 'xlsx', bookSST: false, type: 'binary' });

					// Convert the string to a Blob
					var blob = new Blob([s2ab(wbString)], { type: 'application/octet-stream' });
			 
					// Trigger the download
					saveAs(blob, "room_detail.xlsx");
				}
			})
		});
		
	}
}
function s2ab(s) {
	var buf = new ArrayBuffer(s.length);
	var view = new Uint8Array(buf);
	for (var i = 0; i != s.length; ++i) view[i] = s.charCodeAt(i) & 0xFF;
	return buf;
}
function saveAs(blob, fileName) {
	var link = document.createElement('a');
	link.href = window.URL.createObjectURL(blob);
	link.download = fileName;
	document.body.appendChild(link);
	link.click();
	document.body.removeChild(link);
}
function delete_row(){
	var element = document.querySelector('#room')
		element.addEventListener('click', function (event) {
			
			  var row = event.target.closest('tr');
			  var rowData = {
				id: row.dataset.id,
				name: row.cells[1].textContent // Adjust the index based on your table structure
			  };
	  
			  // Log or do something with the rowData
			  console.log('Clicked row data:', rowData.name);

			  frappe.confirm(
				'Are you sure to delete this Room?',
				function(){
					frappe.call({
						method:"rental.rental.page.room_details.room_details.delete_row",
						args:{
							room : rowData.name
						},
						callback:function(){
							frappe.ui.toolbar.clear_cache();
						}
					})
				},
			)
			
		  });		
}

