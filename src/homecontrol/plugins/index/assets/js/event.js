(function($)
{
	HC.EventCommon =
	{
		toggle: function()
		{
			var $event = $(this).parent().parent();
			
			if($(this).hasClass("icon-plus"))
			{
				$(this).removeClass("icon-plus").addClass("icon-minus");
				$(".event-body", $event).slideDown("slow");
			}
			else
			{
				$(this).removeClass("icon-minus").addClass("icon-plus");
				$(".event-body", $event).slideUp("slow");						
			}
		},

		select: function()
		{
			var $event = $(this).parent().parent();
			
			if($event.hasClass("selected"))
			{
				$event.removeClass("selected");
				$(".icon-white", $event).removeClass("icon-white");
			}
			else
			{
				$event.addClass("selected");
				$(".icon-plus", $event).addClass("icon-white");
				$(".icon-minus", $event).addClass("icon-white");
			}
		},

		append_to: function(target)
		{
			var $event = $(".templates .event").
				clone().hide().appendTo($(".events", target));
			
			$(".event-details", $event).html(this.get_details());
			$(".event-body", $event).html(this.json());
	
			$event.slideDown("slow");
			
			$(".event-toggle", $event).click(this.toggle);
			$(".event-details", $event).click(this.select);
		}
	}
	
	$.extend(HC.IREvent, HC.EventCommon, 
	{	
		get_details: function()
		{
			var date = new Date(Math.round(1000 * this.receive_time));
			
			return date.toLocaleTimeString() + ", " +  
				this.timings.length + " timings, " +
				"hex " + this.hex + ", decoding " + this.decoding;
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