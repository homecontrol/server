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
	
			request.done(function(info)
			{
				if(callback != undefined)
					callback(info);
				
			});
	
			request.fail(function(response)
			{
				HC.error("<strong>Could not get device status</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
				
				if(callback != undefined)
					callback(null);
				
			});
		},
		
		rf_send_tristate: function(tristate, callback)
		{
			var request = $.ajax({
				url: "device/" + this.name + "/rf_send_tristate?tristate=" + tristate,
				type: "GET",
				dataType: "json"
			});
	
			request.done(function(info)
			{
				if(callback != undefined)
					callback(true);
				
			});
	
			request.fail(function(response)
			{
				HC.error("<strong>Could not send rf tristate</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
				
				if(callback != undefined)
					callback(false);
				
			});
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
			}, this));			
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
			}, this));			
		},
		
		get_events: function(time, callback)
		{
			return this._get_events("", time, callback);
		},
		
		rf_get_events: function(time, callback)
		{
			return this.get_events("rf", time, callback);
		},
		
		ir_get_events: function(time, callback)
		{
			return this.get_events("ir", time, callback);
		},
		
		get_events: function(type, time, callback)
		{
			var method = "get_events";
			if(type != "") method = type + "_" + method;
			
			var request = $.ajax({
				url: "device/" + this.name + "/" + method + "?timestamp=" + time, 
				type: "GET",
				dataType: "json"
			});
			
			request.done(function(events) { if(callback != undefined) callback(events); });
	
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could not fetch " + type + " events from device " + this.name + "</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
			}, this));
		},

		rf_send_events: function(events, callback)
		{
			return this.send_events("rf", events, callback);
		},

		ir_send_events: function(events, callback)
		{
			return this.send_events("ir", events, callback);
		},

		send_events: function(type, events, callback)
		{
			var event_data = []
			$(events).each(function(key,event){ event_data.push(event.json()); });
			
			var request = $.ajax({
				url: "device/" + this.name + "/" + type + "_send_json",
				type: "POST",
				dataType: "json",
				data: event_data.join("\n") + "\n" 
			});
			
			request.done(function(events) { if(callback != undefined) callback(events); });
			
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could not send json for device " + this.name + "</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
				if(callback != undefined)
					callback(response);
				
			}, this));			
		}
	};	
	
})( jQuery );