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
				device.handle_radio_tristate();
				device.handle_radio_capture();
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
		
		handle_radio_tristate: function()
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
		
		handle_radio_capture: function()
		{
			var capture = $(".radio .capture", this.$el);
			
			// Make event box resizeable
			$(".events", capture).resizable({handles: "s"});
			
			// Set handlers.
			$(".start", capture).click($.proxy(function()
			{
				var event = $(".templates .event", capture).
					clone().hide().appendTo($(".events", capture));
				
				$(".index", event).html("1");
				$(".pulse_length", event).html("433 Mhz");
				$(".timings", event).html("100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100");

				event.slideDown("slow");
				
				$(".events", capture).resizable({handles: "s"});
				
			}, this));
			
			$(".copy", capture).click($.proxy(function()
			{
				
			}, this));
			
			$(".clear", capture).click($.proxy(function()
			{
				
			}, this));			
		}
	});
	
	$(document).ready(function()
	{
		var index = Object.create(HC.Index);
		index.init();
	});
	
})(jQuery);