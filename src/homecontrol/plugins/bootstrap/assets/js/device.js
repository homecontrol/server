(function($)
{
	HC.Device = 
	{
	    name: null,
	    /* TODO: Get device attributes from config.
	    host: null,
	    port_cmds: null,
	    port_events: null,
	    features: null,*/	    
	    
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
	
			request.fail($.proxy(function(response)
			{
			    HC.request_error("Could not get status information from device " + this.name, response);
				
				if(callback != undefined)
					callback(null);
				
			}, this));
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
	
			request.fail($.proxy(function(response)
			{
			    HC.request_error("Could not send rf tristate from device " + this.name, response);
				
				if(callback != undefined)
					callback(false);
				
			}, this));
		},
		
		start_capture: function()
		{
			var request = $.ajax({
				url: "device/" + this.name + "/start_capture",
				type: "GET",
				dataType: "json"
			});
			
			request.fail($.proxy(function(response){
			    HC.request_error("Could not start capturing for device " + this.name, response);
			}, this));			
		},
		
		stop_capture: function()
		{
			var request = $.ajax({
				url: "device/" + this.name + "/stop_capture",
				type: "GET",
				dataType: "json"
			});
			
			request.fail($.proxy(function(response){
			    HC.request_error("Could not start capturing for device " + this.name, response); 
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
	
			request.fail($.proxy(function(response){
			    HC.request_error("Could not fetch " + type + " events from device " + this.name, response);
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
			$(events).each(function(key,event)
		        { event_data.push(HC.to_json(event)) });
			
			var request = $.ajax({
				url: "/device/" + this.name + "/" + type + "_send_json",
				type: "POST",
				dataType: "json",
				data: event_data.join("\n") + "\n" 
			});
			
			request.done(function() { if(callback != undefined) callback(true); });
			
			request.fail($.proxy(function(response)
			{
			    HC.request_error("Could not send json from device " + this.name, response);
			    
				if(callback != undefined)
					callback(false, response);
				
			}, this));			
		}
	};	
	
})( jQuery );