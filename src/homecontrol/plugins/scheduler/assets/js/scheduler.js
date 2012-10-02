(function($)
{
	HC.Scheduler =
	{
		$signals: null,
		loader_signals: null,
		
		$scheduler: null,
		loader_scheduler: null,
		
		init: function()
		{
			this.$signals = $("div#signals");
			this.loader_signals = this.$signals.HC("Loader");
			
			this.$scheduler = $("div#scheduler");
			this.loader_scheduler = this.$scheduler.HC("Loader");
			
			$("a[href=#signals]").on('shown', $.proxy(this.load_signals, this));
			$("a[href=#scheduler]").on('shown', $.proxy(this.load_scheduler, this));
			
			this.load_signals();
			
			return this;			
		},
		
		load_signals: function(e)
		{
			$("table", this.$signals).hide();
			this.loader_signals.show();
			
			var request = $.ajax({
				url: "scheduler/load_signals?order_by=name", 
				type: "GET",
				dataType: "json"
			});
	
			request.done($.proxy(function(signals)
			{
				var $tbody = $("table tbody", this.$signals);
				$("tr:not(.template)", $tbody).remove();
				$.each(signals, $.proxy(function(i, signal)
				{
					var $row = $("table tr.template", this.$signals).clone();
					$row.removeClass("template").appendTo($tbody);
					
					signal["num_events"] = signal["events"].length;					
					signal["event_types"] = $(document.createElement("div"));					
					
					var event_types = new Array();
					for(var i in signal["events"])
					{
						var event = signal["events"][i];
						if($.inArray(event.type, event_types) < 0)
							event_types.push(event.type);
					}
					event_types.sort();					
					for(var i in event_types)
					{
						var $el = $(document.createElement("span"));
						$el.html(event_types[i]);
						$el.addClass("label");
						
						switch(event_types[i])
						{
							case "ir":
								$el.addClass("label-important");
							break;
							case "rf":
								$el.addClass("label-warning");
							break;							
						}
						
						$el.appendTo(signal["event_types"]);
					}
					
					signal["event_types"] = signal["event_types"].html();
					
					for(var key in signal)
					{
						$row.html($row.html().replace("#" + key, signal[key]));
					}
					
					// Add signal id for further editing.
					$row.data("id", signal["id"]);	
					this.set_signal_handlers($row, signal);
				}, this));
				
				this.loader_signals.hide();
				$("table", this.$signals).fadeIn();				
				
			}, this));
	
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could not load signals:: " +  
					response.statusText + " (Error " + response.status + ")");
				
				this.loader_signals.hide();
				$("table", this.$signals).fadeIn();				
				
			}, this));
		},
		
		load_scheduler: function(e)
		{
			$("table", this.$scheduler).hide();
			this.loader_scheduler.show();
			

			this.loader_scheduler.hide();
			$("table", this.$scheduler).fadeIn();			
		},
		
		set_signal_handlers: function($row, signal)
		{
			var $dialog = $(".templates .dialog-edit-signal").clone().appendTo($("td:first", $row));
			var $confirm = $(".templates .dialog-delete-signal-confirm").clone().appendTo($("td:first", $row));
			var $input_name = $(".signal-name", $dialog);
			var $input_vendor = $(".signal-vendor", $dialog);
			var $input_desc = $(".signal-description", $dialog);
			
			$dialog.dialog(
			{
				title: $dialog.data("title"),
				modal: true,
				resizable: false,
				width: $dialog.outerWidth(true) + "px",
				autoOpen: false
			});
			
			
			$confirm.dialog({
				title: $confirm.data("title"),
				modal: true,
				resizable: false,
				width: $confirm.outerWidth(true) + "px",
				autoOpen: false
			});
			
			$row.click(function()
			{
				$dialog.dialog("open");

				$input_name.val(signal.name);
				$input_vendor.val(signal.vendor);
				$input_desc.val(signal.description);				
			});
			
			$(".btn-cancel", $dialog).click(function()
			{
				$dialog.dialog("close");
				return false;
				
			});
			
			$(".btn-save", $dialog).click($.proxy(function()
			{
				var request = $.ajax({
					url: "scheduler/save_signal", // TODO: Change this into new signal wrapper URL.
					type: "POST",
					dataType: "json",
					data: $.toJSON({ // TODO: Do we need explicit JSON conversion?
						id: signal.id,
						device_id: signal.device_id,
						name: $input_name.val(),
						vendor: $input_vendor.val(),
						description: $input_desc.val(),
						events: signal.events
					})
				});
				
				request.fail(function(response)
				{
					HC.error("<strong>Error while saving signal</strong>: " + 
						     response.statusText + " (Error " + response.status + ")");
				});
				
				request.done($.proxy(function(events)
				{
					HC.success("Signal \"" + $input_name.val() + "\" successfully saved.");
					$dialog.dialog("close");
					this.load_signals();
					
				}, this));
				
				return false;
				
			}, this));
			
			$(".btn-delete", $dialog).click(function()
			{
				$(".signal-name", $confirm).html(signal.name);
				$confirm.dialog("open");
				return false;
			});

			$(".btn-ok", $confirm).click($.proxy(function()
			{
				var request = $.ajax({
					url: "signal/" + signal.id + "/sql_delete",
					type: "GET",
					dataType: "json"
				});
				
				request.fail(function(response)
				{
					HC.error("<strong>Error while deleting signal \"" + signal.name + "\"</strong>: " + 
						     response.statusText + " (Error " + response.status + ")");
				});
				
				request.done($.proxy(function(events)
				{
					HC.success("Signal \"<strong>" + signal.name + "</strong>\" successfully deleted.");
					$dialog.dialog("close");
					this.load_signals();
					
				}, this));
				
				$confirm.dialog("close");
				return false;
				
			}, this));
				
			$(".btn-cancel", $confirm).click(function()
			{				
				$confirm.dialog("close");
				return false;
			});
		}
	};
	
	$(document).ready(function()
	{
		var scheduler = Object.create(HC.Scheduler);
		scheduler.init();
	});
})(jQuery);