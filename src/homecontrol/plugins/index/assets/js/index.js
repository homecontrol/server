(function($)
{
	HC.Index =
	{
		init: function()
		{
			this.init_devices();
			return this;
		},
		
		init_devices: function()
		{
			$("li.device").click(function()
			{
				var dev_id = $("a", this).attr("href").replace("#", "");
				var dev_name = $("a", this).html();
				
				var device = Object.create(HC.Device);
				device.init(dev_name);
				device.show(dev_id);
				device.handle_rf_tristate();
				device.handle_rf_capture();
			});
			
			return this;
		}	
	};

	$.extend(HC.Device,
	{	
		show: function(dev_id)
		{
			this.id = dev_id;
			this.$el= $("div#" + this.id);
			
			// Hide other devices
			$("li.device").removeClass("active");
			$("div.device .info").hide();
			$("div.device").hide();
			
			// Show current device
			$("li." + this.id).addClass("active");
			this.$el.show(0, $.proxy(this.update_status, this));			
			
			return this;
		},
		
		update_status: function()
		{
			this.loader = $(".info", this.$el).HC("Loader");
			this.loader.show();
			
			this.get_status($.proxy(function(info)
			{
				if(info == null)
				{
					// Something was going wrong e.g. re-try after some minutes?
				}
				else
				{
					for(var key in info)
					{						
						if(info[key] != undefined && info[key] != "")
							$("." + key, this.$el).html(info[key]);
					}
					
					// Enable controls if device is online.
					if(info["status"] == "online")
					{
						this.enable_controls();
						$(".status", this.$el).
							removeClass("label-important").
							addClass("label-success");
					}
					
					$(".info", this.$el).fadeIn("slow");					
				}
				
				this.loader.hide();
				
			}, this));
			
			return this;
		},
		
		enable_controls: function()
		{
			// Enable form inputs, selects and buttons
			$("input, select, button", this.$el).each(function()
			{
				$(this).
					removeClass("disabled").
					removeAttr("disabled");
			});
		},
		
		handle_rf_tristate: function()
		{
			// Set handlers.
			var tristate = $(".radio .tristate", this.$el);
			var form_actions = $(".form-actions", tristate);
			var switch_on = $("button[value='1']", form_actions);
			var switch_off = $("button[value='0']", form_actions);
						
			// Toggle primary button
			switch_on.click($.proxy(function()
			{
				switch_on.addClass("btn-primary").addClass("disabled").attr("disabled", "");
				switch_off.removeClass("btn-primary");
				this.rf_send_tristate(this.get_tristate("ffff"), function(success)
				{
					switch_on.removeClass("disabled").removeAttr("disabled", "");
				});
			}, this));
			
			switch_off.click($.proxy(function()
			{
				switch_off.addClass("btn-primary").addClass("disabled").attr("disabled", "");
				switch_on.removeClass("btn-primary");
				this.rf_send_tristate(this.get_tristate("fff0"), function()
				{
					switch_off.removeClass("disabled").removeAttr("disabled", "");
				});				
			}, this));
		},
		
		get_tristate: function(suffix)
		{
			if(suffix == undefined)
				suffix = "";
			
			// Compose tristate
			var tristate = $(".radio .tristate", this.$el);
			var group = $(".group", tristate).val();
			var address = $(".address", tristate).val();
						
			tristate = ""
			for(var i = 1; i <= 4; i ++)
			{
				if(i == group) tristate += "0"
				else tristate += "f";
			}
			for(var i = 1; i <= 4; i ++)
			{
				if(i == address) tristate += "0"
				else tristate += "f";
			}
			
			return tristate + suffix;
		},
		
		handle_rf_capture: function()
		{
			var capture = $(".radio .capture", this.$el);
			
			// Make event box resizeable
			$(".resizable", capture).resizable(
			{
				handles: "s",
				resize: function(event, ui)
				{
					$(".events", ui.element).css("height", ui.size.height);
				}
			});
			
			// Set handlers.
			$(".start", capture).click($.proxy(function()
			{	
				this.add_radio_event(100, "");
				
				
			}, this));
			
			$(".copy", capture).click($.proxy(function()
			{
				
			}, this));
			
			$(".clear", capture).click($.proxy(function()
			{
				$(".events", capture).html("");
				
			}, this));			
		},
		
		add_radio_event: function(pulse_length, timings)
		{
			var capture = $(".radio .capture", this.$el);
			var event = $(".templates .event").
				clone().hide().appendTo($(".events", capture));
			
			$(".event-details", event).html("100 Timings, Pulse Length 433 Mhz");
			$(".event-body", event).html("13468, 364, 1352, 1284, 432, 396, 1348, 1296, 420, 408, 1336, 1268, 452, 400, 1348, 368, 1372, 372, 1344, 1248, 484, 384, 1364, 360, 1360, 372, 1364, 372, 1344, 372, 1360, 1268, 444, 404, 1340, 1256, 464, 416, 1332, 1244, 472, 392, 1356, 1248, 468, 384, 1384, 352, 1348");
	
			event.slideDown("slow");
			
			$(".event-toggle", event).click(function()
			{
				if($(this).hasClass("icon-plus"))
				{
					$(this).removeClass("icon-plus").addClass("icon-minus");
					$(".event-body", event).slideDown("slow");
				}
				else
				{
					$(this).removeClass("icon-minus").addClass("icon-plus");
					$(".event-body", event).slideUp("slow");						
				}
			});
		}
	});
	
	$(document).ready(function()
	{
		var index = Object.create(HC.Index);
		index.init();
	});
	
})(jQuery);