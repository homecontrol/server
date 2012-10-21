(function($)
{
	$.extend(HC.Signal,
	{
		init: function()
		{
			var token = document.location.href.match(/signal_id=([^&]+)/);
			if(token.length == 0)
				return this;
			
			this.load_by_id(token[1], $.proxy(this.set_handlers, this));			
			
			return this;			
		},
		
		set_handlers: function()
		{
			var $confirm = $(".templates .dialog-delete-signal-confirm");
			var $input_name = $(".signal-name");
			var $input_vendor = $(".signal-vendor");
			var $input_desc = $(".signal-description");
			var $input_device = $(".signal-device");
			
			$confirm.dialog({
				title: $confirm.data("title"),
				modal: true,
				resizable: false,
				width: $confirm.outerWidth(true) + "px",
				autoOpen: false
			});
			
			$(".btn-save").click($.proxy(function()
			{
				this.name = $input_name.val();
				this.vendor = $input_vendor.val();
				this.description = $input_desc.val();
				this.save();
				
				return false;
				
			}, this));
			
			$(".btn-send").click($.proxy(function()
            {
			    $(".btn-send").prop("disabled", true).addClass("disabled");
                var dev_name = $input_device.val();
                this.send(dev_name, function(){ 
                    $(".btn-send").prop("disabled", false).removeClass("disabled"); });                
                return false;
                
            }, this));			
			
			$(".btn-delete").click($.proxy(function()
			{
				$(".signal-name", $confirm).html(this.name);
				$confirm.dialog("open");
				return false;
				
			}, this));

			$(".btn-ok", $confirm).click($.proxy(function()
			{
				this.delete(function()
				{
					if(document.referrer != "") document.location.href = document.referrer;
					else document.location.href = "/";
					return false;
				});
				
				$confirm.dialog("close");
				return false;
				
			}, this));
				
			$(".btn-cancel", $confirm).click(function()
			{				
				$confirm.dialog("close");
				return false;
			});			
		}		
	});
	
	$(document).ready(function()
	{
		window.signal = Object.create(HC.Signal);
		window.signal.init();
	});
})(jQuery);