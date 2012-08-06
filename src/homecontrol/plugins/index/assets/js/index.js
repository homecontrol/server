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
				device.rf_handle_tristate();
				device.rf_handle_capture();
			});
			
			return this;
		}	
	};

	$.extend(HC.Device,
	{	
		events: new Array(),
		
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
			$("input, select, button", this.$el).not(".persistent").each(function()
			{
				$(this).
					removeClass("disabled").
					removeAttr("disabled");
			});
		},
		
		rf_handle_tristate: function()
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
		
		rf_handle_capture: function()
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
			$(".btn-start", capture).click($.proxy(function()
			{
				var $el = $(".btn-start", capture);
				
				if($.trim($el.html()) == "Start")
				{
					this.start_capture();
					
					$el.html("Stop");
					$el.addClass("btn-primary");
					
					this.last_event = null;
					
					this.rf_capture_int = setInterval($.proxy(function()
					{
						var start_time = 0;
						if(this.last_event != null)
							start_time = this.last_event.receive_time;
						
						this.rf_get_events(start_time, $.proxy(function(events)
						{
							for(var i = 0; i < events.length; i ++)
							{
								var event = HC.RFEvent.load(events[i]);

								this.events.push(event);
								this.last_event = event;
								
								event.append_to($(".radio .capture", this.$el));
							}
							
						}, this));
						
					}, this), 1000);
				}
				else
				{
					this.stop_capture();
					
					$el.html("Start");
					$el.removeClass("btn-primary");
					
					clearInterval(this.rf_capture_int);
				}
				
			}, this));
						
			$(".btn-clear", capture).click($.proxy(function()
			{
				$(".events", capture).html("");
				
			}, this));		

			// Prepare sending dialog and bind it to the send button!
			$dialog = $(".dialog-send", this.$el);
			$dialog.dialog(
			{
				title: $dialog.data("title"),
				modal: true,
				width: eval($dialog.outerWidth(true) + 10),
				resizable: false,
				autoOpen: false
			});			

			$(".btn-send", capture).click($.proxy(function()
			{
				$dialog.dialog("open");

				// TODO: Determine field values.
				$(".delay", $dialog).attr("value", "1250");
				$(".pulse_length", $dialog).attr("value", "443");

				$(".btn-close").click(function()
				{
					$dialog.dialog("close");
				});

				$(".btn-send").click(function()
				{
					// TODO
				});				

			}, this));
		}
	});
	
	$(document).ready(function()
	{
		var index = Object.create(HC.Index);
		index.init();
	});
	
})(jQuery);