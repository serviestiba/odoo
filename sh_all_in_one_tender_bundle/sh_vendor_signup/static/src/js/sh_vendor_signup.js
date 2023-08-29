odoo.define("sh_all_in_one_tender_bundle.custom_js", function (require) {			

    var publicWidget = require("web.public.widget");


    publicWidget.registry.js_cls_sh_customer_signup_custom_js = publicWidget.Widget.extend({
		selector: "#vendor_sign_up_form_section",
		events: {
	        'click .vendor_img .fa-link': '_onClickImage',
			'click .vendor_type .browse': '_onClickBrowseImage',
			'change .vendor_type input[type="file"]': '_onChangeFileInput',
			'click #addBtn': '_onClickAddContactRow',
			'click #contact_row .remove': '_onClickRemoveContactRow',
	    },
		
		/**
         * @override
         */
        start: function () {
			this.rowIdx = 0;
			$("form[action='/vendor_sign_up'] #category_section").multiselect();
			return this._super(...arguments);
		},

	    _onClickImage: function (ev) {
			$(".browse").click(); 
		},
		
	    _onClickBrowseImage: function (ev) {
			var file = $("input[name='vendor_image']");
	  		file.trigger("click");
		},
		
		_onChangeFileInput: function (ev) {
			  var fileName = ev.currentTarget.files[0].name;
			  $(".vendor_type #file").val(fileName);
				var reader = new window.FileReader();
			        
			        reader.onload = function (ev) {
			            $('.vendor_type #preview').attr('src', ev.target.result);
			        };
					reader.readAsDataURL(ev.currentTarget.files[0]);

		},
		_onClickAddContactRow: function (ev) {
			var rowCount = $(document).find("#contact_row row").length + 1;
	        this.rowIdx = this.rowIdx + 1;
	        var vendorName = "vendor_c_name_" + String(this.rowIdx);
	        var vendorEmail = "vendor_c_email_" + String(this.rowIdx);
	        var vendorPhone = "vendor_c_phone_" + String(this.rowIdx);
	        var productOptioons = '<option value="">Select Product</option>';
	        var productOptioons = $(document).find("#js_id_product_list").html();
	        var text =
				'<div class="row c_row '+
				String(this.rowIdx)+
				'">'+ '<div class="col-lg-4 col-sm-12">'+
				  '<div class="mb-3">'+
					'<label for="vendor_contact_name"><b>Name :</b></label>'+
					'<input type="text" class="form-control" ' +
					' name="'+
					vendorName+
					'" required="required"/>'+
					'</div>'+
				    '</div>'+
	'<div class="col-lg-4 col-sm-12">'+
				  '<div class="mb-3">'+
					'<label for="vendor_contact_email"><b>Email :</b></label>'+
					'<input type="email" class="form-control" name="'+
					vendorEmail+
					'" required="required"/>'+
					'</div>'+
				    '</div>'+
	'<div class="col-lg-4 col-sm-12">'+
				  '<div class="mb-3">'+
					'<label for="vendor_contact_phone"><b>Phone :</b></label>'+
					'<div class="" style="display: flex;align-items: center;">'+
					'<input type="text" class="form-control" name="'+
					vendorPhone+
					'"/>'+
					'<button style="margin-left: 14px;margin-right: 7px;font-size: 22px;padding: 0;color: red;" class="btn remove" type="button"><i class="fa fa-trash"/></button>'+
					'</div>'+
					'</div>'+
				    '</div>'
	        $("#contact_row").append(text);
		},
		_onClickRemoveContactRow: function (ev) {
			ev.currentTarget.closest('.c_row').remove();
		},
	});
});













