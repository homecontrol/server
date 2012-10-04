(function($)
{
	HC.Signal =
	{
		id: null,
		device_id: null,
		name: null,
		vendor: null,
		description: null,
		events: new Array(),
		event_types: new Array(),
		
		load: function(data)
		{
			this.id = data["id"];
			this.device_id = data["device_id"];
			this.name = data["name"];
			this.vendor = data["vendor"];
			this.description = data["description"];
			this.events = data["events"];
			this.event_types = data["event_types"];
			return this;
		},
		
		load_by_id: function(id, callback)
		{
			var request  = $.ajax({
				url: "/signal/sql_load?signal_id=" + id,
				type: "GET",
				dataType: "json"
			});
			
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could not load signal \"" + this.id + "\"</strong>: " +
					response.statusText + " (Error " + response.status + ")");
				
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
			
			request.fail(function(response)
			{
				HC.error("<strong>Error while deleting signal \"" + this.name + "\"</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
				
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
					device_id: this.device_id,
					name: this.name,
					vendor: this.vendor, 
					description: this.description,
					events: this.events
				})
			});
			
			request.fail(function(response)
			{
				HC.error("<strong>Error while saving signal</strong>: " + 
					response.statusText + " (Error " + response.status + ")");
				
				if(callback != undefined)
					callback(false, response);				
			});
			
			request.done($.proxy(function()
			{ 
				HC.success("Signal \"" + this.name + "\" successfully saved.");
				
				if(callback != undefined)
					callback(true, null);				
			}, this));
		}
	}
})( jQuery );
	