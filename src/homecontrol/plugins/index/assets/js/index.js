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
				device.ir_handle_capture();
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
						// Enable form inputs, selects and buttons.
						$("input, select, button", this.$el).not(".event-related").
							removeClass("disabled").prop("disabled", false);
						
						// Set status label.
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
				switch_on.addClass("btn-primary").addClass("disabled").prop("disabled", true);
				switch_off.removeClass("btn-primary");
				this.rf_send_tristate(this.get_tristate("ffff"), function(success)
				{
					switch_on.removeClass("disabled").prop("disabled", false);
				});
			}, this));
			
			switch_off.click($.proxy(function()
			{
				switch_off.addClass("btn-primary").addClass("disabled").prop("disabled", true);
				switch_on.removeClass("btn-primary");
				this.rf_send_tristate(this.get_tristate("fff0"), function()
				{
					switch_off.removeClass("disabled").prop("disabled", false);
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
			return this.handle_capture(HC.TYPE_RF,
				$(".radio .capture", this.$el));
		},
		
		ir_handle_capture: function()
		{
			return this.handle_capture(HC.TYPE_IR, 
				$(".infrared .capture", this.$el));
		},
		
		handle_capture: function(type, capture)
		{
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
				//// THIS IS ONLY FOR DEBUG
				//
				//var event = null;
				//
				//if(type == HC.TYPE_RF)
				//{
				//	event = Object.create(HC.RFEvent);
				//
				//	event.timings = [1200, 500, 1200, 600, 1100, 236, 1234, 1231, 593, 134];
				//	event.receive_time = 123456789;
				//	event.pulse_length = 443;
				//	event.len_timings = event.timings.length;
				//}
				//else
				//{
				//	event = Object.create(HC.IREvent);
				//	
				//	event.timings = [1200, 500, 1200, 600, 1100, 236, 1234, 1231, 593, 134];
				//	event.receive_time = 987654321;
				//	event.decoding = "DEBUG";
				//	event.len_timings = event.timings.length;
				//	event.hex = 0x99999;
				//}
				//
				//event.append_to(capture);
				//return;
				//
				//// THIS IS ONLY FOR DEBUG				

				var $btn = $(".btn-start", capture);
				if($.trim($btn.html()) == "Start")
				{
					this.start_capture();
					
					$btn.html("Stop");
					$btn.addClass("btn-primary");
					
					this.last_event = null;
					
					this.capture_handler = setInterval($.proxy(function()
					{
						var start_time = 0;
						
						if(this.last_events == undefined)
							this.last_events = {}
						
						if(this.last_events[type] !== undefined)
							start_time = this.last_events[type].receive_time;
						
						this.get_events(type, start_time, $.proxy(function(events)
						{		
							for(var i = 0; i < events.length; i ++)
							{
								var event = null;
								
								if(type == HC.TYPE_RF) event = HC.RFEvent.load(events[i]);
								else event = HC.IREvent.load(events[i]);

								this.last_events[type] = event
								event.append_to(capture);
							}
							
						}, this));
						
					}, this), 250);
				}
				else
				{
					this.stop_capture();
					
					$btn.html("Start");
					$btn.removeClass("btn-primary");
					
					clearInterval(this.capture_handler);
				}
				
			}, this));
						
			$(".btn-clear", capture).click($.proxy(function()
			{
				$(".events", capture).html("");
				$(".event-related", capture).addClass("disabled").prop("disabled", true);
				
			}, this));		

			$(".btn-send", capture).click($.proxy(function()
			{
				$(".btn-send", capture).addClass("btn-primary");

				var events = new Array();
				$(".events .selected", capture).each(function(key, value)
				{
					var json = $(".event-body", value).html();
					events.push(HC.Event.load(json));
				});

				this.send_events(type, events, function() 
					{ $(".btn-send", capture).removeClass("btn-primary"); });
				
			}, this));
			
			$(".btn-save", capture).click($.proxy(function()
			{
				$dialog = $(".dialog-save-signal");
				$(".control-group", $dialog).removeClass("error");
				
				$dialog.dialog(
				{
					title: $dialog.data("title"),
					modal: true,
					resizable: false,
					width: $dialog.outerWidth(true) + "px"
				});

				$(".btn-cancel", $dialog).click(function(){ $dialog.dialog("close"); });
				$(".btn-save", $dialog).click($.proxy(function()
				{
					$input_name = $(".signal-name", this);
					$input_desc = $(".signal-description", this);
					
					if(!$input_name.val())
					{
						$input_name.parent().addClass("error");
						return;
					}
					
					var events = new Array();
					$(".events .selected", capture).each(function(key, value)
					{
						var json = $(".event-body", value).html();
						events.push(HC.Event.load(json));
					});
					
					var request = $.ajax({
						url: "signals/save",
						type: "POST",
						dataType: "json",
						data: $.toJSON({
								  name: $input_name.val(),
								  description: $input_desc.val(),
								  events: events
							  })
						});
					
					request.fail($.proxy(function(response)
					{
						HC.error("<strong>Error while saving signal</strong>: " + 
							     response.statusText + " (Error " + response.status + ")");
						return;
					}), this);
					
					request.done($.proxy(function(events)
					{
						// Success message .......
						$dialog.dialog("close");
						
					}), this);
					
				}, $dialog));

			}, this));
		}
	});
	
	$(document).ready(function()
	{
		var index = Object.create(HC.Index);
		index.init();
	});
	
})(jQuery);