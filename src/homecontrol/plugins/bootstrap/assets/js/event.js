(function($)
{
	HC.Event = 
	{
	    id: null,
		type: null,
		timings: new Array(),
		receive_time: null,

		load: function(data)
		{
			if(typeof(data) == "string")
				data = $.evalJSON(data);

			if(typeof(data) != typeof({}))
				return Object.create(HC.Event);
			
			if(data.type == HC.TYPE_IR)
				return HC.IREvent.load(data);

			if(data.type == HC.TYPE_RF)
				return HC.RFEvent.load(data);
		}
	};

	HC.IREvent = $.extend({}, HC.Event,
	{	
		type: HC.TYPE_IR,
		decoding: null,
		hex: 0x0,
		length: 0,

		load: function(data)
		{
			var event = Object.create(HC.IREvent);

			event.id = data.id
			event.type = HC.TYPE_IR;
			event.decoding = data.decoding;
			event.hex = data.hex;
			event.length = data.length;
			event.timings = data.timings;
			event.receive_time = data.receive_time;
			
			return event;
		}
	});

	HC.RFEvent = $.extend({}, HC.Event,
	{	
		type: HC.TYPE_RF,
		error: null,
		pulse_length: 0,
		len_timings: 0,

		load: function(data)
		{
			var event = Object.create(HC.RFEvent);

			if(data.error !== undefined)
				event.error = data.error;

			event.id = data.id
			event.type = HC.TYPE_RF;
			event.timings = data.timings;
			event.receive_time = data.receive_time;
			event.pulse_length = data.pulse_length;
			event.len_timings = data.len_timings;
			
			return event;
		}
	});	

})( jQuery );