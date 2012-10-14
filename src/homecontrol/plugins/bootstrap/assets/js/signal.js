(function($)
{
	HC.Signal =
	{
		id: null,
		dev_name: null,
		name: null,
		vendor: null,
		description: null,
		events: new Array(),
		event_types: new Array(),
		
		load: function(data)
		{
			this.id = data["id"];
			this.dev_name = data["dev_name"];
			this.name = data["name"];
			this.vendor = data["vendor"];
			this.description = data["description"];
			this.event_types = data["event_types"];
			
			$(data["events"]).each($.proxy(function(key, event){
			    this.events.push(HC.Event.load(event));
	        }, this));

			return this;
		},
		
		load_by_id: function(id, callback)
		{
			var request  = $.ajax({
				url: "/signal/sql_load?signal_id=" + id,
				type: "GET",
				dataType: "json"
			});
			
			request.fail($.proxy(function(response){
			    HC.request_error("Could not load signal \"" + this.id + "\"", response);
				
				if(callback != undefined)
					callback(null, response);
				
			}, this));
			
			request.done($.proxy(function(data)
			{
				this.load(data);
				
				if(callback != undefined)
					callback(data);
				
			}, this));	
		},
		
		json: function()
		{
			// Kind of workaround to support inherit properties!
			var o = Object.create(this);
			for(p in this){ o[p] = this[p]; }

			return $.toJSON(o).replace(/(:|,)/g, "$1 ");
		},
		
		delete: function(callback)
		{
			var request = $.ajax({
				url: "/signal/" + this.id + "/sql_delete",
				type: "GET",
				dataType: "json"
			});
			
			request.fail(function(response){
			    HC.request_error("Error while deleting signal", response);
				
				if(callback != undefined)
					callback(false, response);
			});
			
			request.done($.proxy(function()
			{
				HC.success("Signal \"<strong>" + this.name + "</strong>\" deleted.", function()
				{
					if(document.referrer != "") document.location.href = document.referrer;
					else document.location.href = "/";
					return false;
				});
				
				if(callback != undefined)
					callback(true, null);
				
			}, this));
		},
		
		save: function(callback)
		{
			var request = $.ajax({
				url: "/scheduler/save_signal",
				type: "POST",
				dataType: "json",
				data: $.toJSON({ // TODO: Do we need explicit JSON conversion?
					id: this.id,
					dev_name: this.dev_name,
					name: this.name,
					vendor: this.vendor, 
					description: this.description,
					events: this.events
				})
			});
			
			request.fail(function(response){
			    HC.request_error("Error while saving signal", response);
				
				if(callback != undefined)
					callback(false, response);				
			});
			
			request.done($.proxy(function()
			{ 
				HC.success("Signal \"" + this.name + "\" successfully saved.");
				
				if(callback != undefined)
					callback(true, null);				
			}, this));
		},
		
		send: function(dev_name, callback)
		{
		    var device = Object.create(HC.Device);
            device.init(dev_name);
            
            // Separate events by their type.
            var events = {}
            $(this.events).each(function(key, event)
            {
                if(events[event.type] == undefined)
                    events[event.type] = new Array();
                
                events[event.type].push(event);
            });
            
            var rsend = function(events, callback)
            {
                var done = true;
                for(var type in events)
                {
                    done = false;
                    device.send_events(type, events[type], function(success)
                    {                  
                        // Success, next iteration.
                        if(success)
                        {
                            HC.success("Successfully send " + events[type].length + " " + 
                                       "events from type \"" + type + "\"."); 
                            
                            delete events[type];
                            rsend(events, rsend);
                        }
                        
                        // Error, skip next iterations.
                        else
                        {
                            if(callback != undefined)
                                callback(false);
                        }
                    });
                    
                    break; // Only process the first event type within this iteration.
                }
                
                if(done)
                {
                    if(callback != undefined)
                        callback(true);
                }
            };
            
            rsend(events, callback);
		}
	}
})( jQuery );
	