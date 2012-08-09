(function($)
{
	HC.Device = 
	{
		init: function(name)
		{
			this.name = name;
			return this;
		},
		
		get_status: function(callback)
		{
			var request = $.ajax({
				url: "device/" + this.name + "/get_info",
				type: "GET",
				dataType: "json"
			});
	
			request.done($.proxy(function(info)
			{
				if(callback != undefined)
					callback(info);
				
			}), this);
	
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could not get device status</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
				
				if(callback != undefined)
					callback(null);
				
			}), this);
		},
		
		rf_send_tristate: function(tristate, callback)
		{
			var request = $.ajax({
				url: "device/" + this.name + "/rf_send_tristate?tristate=" + tristate,
				type: "GET",
				dataType: "json"
			});
	
			request.done($.proxy(function(info)
			{
				if(callback != undefined)
					callback(true);
				
			}), this);
	
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could not send rf tristate</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
				
				if(callback != undefined)
					callback(false);
				
			}), this);
		},
		
		start_capture: function()
		{
			var request = $.ajax({
				url: "device/" + this.name + "/start_capture",
				type: "GET",
				dataType: "json"
			});
			
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could not start capturing for device " + this.name + "</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
			}), this);			
		},
		
		stop_capture: function()
		{
			var request = $.ajax({
				url: "device/" + this.name + "/stop_capture",
				type: "GET",
				dataType: "json"
			});
			
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could not start capturing for device " + this.name + "</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
			}), this);			
		},
		
		get_events: function(time, callback)
		{
			return this._get_events("", time, callback);
		},
		
		rf_get_events: function(time, callback)
		{
			return this._get_events("rf", time, callback);
		},
		
		ir_get_events: function(time, callback)
		{
			return this._get_events("ir", time, callback);
		},
		
		_get_events: function(type, time, callback)
		{
			var method = "get_events";
			if(type != "") method = type + "_" + method;
			
			var request = $.ajax({
				url: "device/" + this.name + "/" + method + "/" + time, 
				type: "GET",
				dataType: "json"
			});
	
			request.done($.proxy(function(events)
					{ if(callback != undefined) callback(events); }), this);
	
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could fetch " + type + " events from device " + this.name + "</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
			}), this);
		},

		rf_send_events: function(events, callback)
		{
			return this._send_events("rf", events, callback);
		},

		ir_send_events: function(events, callback)
		{
			return this._send_events("ir", events, callback);
		},

		_send_events: function(type, events, callback)
		{
			var event_data = []
			$(events).each(function(key,event){ event_data.push(event.json()); });
			
			var request = $.ajax({
				url: "device/" + this.name + "/" + type + "_send_json",
				type: "POST",
				dataType: "json",
				data: event_data.join("\n") + "\n" 
			});
			
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could not send json for device " + this.name + "</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
				if(callback != undefined)
					callback(response);
				
			}), this);
			
			request.done($.proxy(function(events)
				{ if(callback != undefined) callback(null); }), this);
		}
	};	
	
})( jQuery );