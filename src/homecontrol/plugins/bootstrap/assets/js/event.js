(function($)
{
	HC.Event = 
	{
		type: null,
		timings: new Array(),
		receive_time: null,
		json_data: null,

		load: function(data)
		{
			if(typeof(data) != typeof({}))
			{
				// TODO: Create event object from data e.g. expect
				// json string and parse it!
				return null;
			}
			
			if(data.type == HC.TYPE_IR)
				return HC.IREvent.load(data);

			if(data.type == HC.TYPE_RF)
				return HC.RFEvent.load(data);
		}
	};

	HC.IREvent = $.extend({}, HC.Event, HC.IREvent,
	{	
		type: HC.TYPE_IR,
		decoding: null,
		hex: 0x0,
		length: 0,

		load: function(data)
		{
			var event = Object.create(HC.IREvent);

			event.decoding = data.decoding;
			event.hex = data.hex;
			event.length = data.length;
			event.timings = data.timings;
			event.receive_time = data.receive_time;

			if(JSON !== undefined)
				event.json_data = JSON.stringify(data);
			
			return event;
		}
	});

	HC.RFEvent = $.extend({}, HC.Event, HC.RFEvent,
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

			event.timings = data.timings;
			event.receive_time = data.receive_time;
			event.pulse_length = data.pulse_length;
			event.len_timings = data.len_timings;
			
			if(JSON !== undefined)
				event.json_data = JSON.stringify(data);
			
			return event;
		}
	});	

})( jQuery );