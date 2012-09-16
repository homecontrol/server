(function($)
{
	HC.Signal = 
	{
		id: null,
		name: null,
		description: null,
		events: new Array(),

		load: function(data)
		{
			if(typeof(data) == "string")
				data = $.evalJSON(data);

			if(typeof(data) != typeof({}))
				return Object.create(HC.Signal);
			
			var signal = Object.create(HC.Signal);
			
			signal.id = data.id;
			signal.name = data.name;
			signal.description = data.description;
			
			$.each(data.events, function(i, event_data)
			{ signal.events.push(HC.Event.loader(event_data)) });
			
			return signal;
		},

		json: function()
		{
			// Kind of workaround to support inherit properties!
			var o = Object.create(this);
			for(p in this){ o[p] = this[p]; }

			return $.toJSON(o).replace(/(:|,)/g, "$1 ");
		}
	};
})( jQuery );