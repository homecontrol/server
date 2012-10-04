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
					
					var event_types = signal["event_types"]
					signal["num_events"] = signal["events"].length;
					signal["event_types"] = $(document.createElement("div"));					

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
					$row.click(function(){location.href = "/signal/view?signal_id=" + signal["id"];})
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
		}
	};
	
	$(document).ready(function()
	{
		var scheduler = Object.create(HC.Scheduler);
		scheduler.init();
	});
})(jQuery);