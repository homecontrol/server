(function($)
{
	HC.EventCommon =
	{
		toggle: function($event)
		{
			$header = $(".event-toggle", $event);
			
			if($header.hasClass("icon-plus"))
			{
				$header.removeClass("icon-plus").addClass("icon-minus");
				$(".event-body", $event).slideDown("slow");
			}
			else
			{
				$header.removeClass("icon-minus").addClass("icon-plus");
				$(".event-body", $event).slideUp("slow");						
			}
		},

		select: function(target, $event)
		{			
			if($event.hasClass("selected"))
			{
				$event.removeClass("selected");
				$(".icon-white", $event).removeClass("icon-white");

				$(".btn-send.event-related, .btn-save.event-related", target).
					addClass("disabled").prop("disabled", true);				
			}
			else
			{
				$event.addClass("selected");
				$(".icon-plus", $event).addClass("icon-white");
				$(".icon-minus", $event).addClass("icon-white");
				
				$(".btn-send.event-related, .btn-save.event-related", target).
					removeClass("disabled").prop("disabled", false);				
			}
		},

		append_to: function(target)
		{
			var $event = $(".templates .event").
				clone().hide().appendTo($(".events", target));
			
			$(".event-details", $event).html(this.get_details());
			$(".event-body", $event).html(HC.to_json(this));
	
			$event.slideDown("slow");
			
			$(".event-toggle", $event).click($.proxy(function()
			{
				this.toggle($event);
				
			}, this));
			$(".event-details", $event).click($.proxy(function()
			{
				this.select(target, $event);
				
			}, this));
			
			$(".btn-clear.event-related", target).removeClass("disabled").prop("disabled", false);			
		}
	}
	
	$.extend(HC.IREvent, HC.EventCommon, 
	{	
		get_details: function()
		{
			var date = new Date(Math.round(1000 * this.receive_time));
			
			return date.toLocaleTimeString() + ", " +  
				this.timings.length + " timings, " +
				"hex " + this.hex + " (" + this.decoding + ")";
		}
	});

	$.extend(HC.RFEvent, HC.EventCommon,
	{
		get_details: function()
		{
			var date = new Date(Math.round(1000 * this.receive_time));
			
			return date.toLocaleTimeString() + ", " +  
				this.timings.length + " timings, " +
				"pulse length " + this.pulse_length + " Mhz";
		}
	});	

})( jQuery );