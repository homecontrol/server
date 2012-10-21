(function($)
{
	HC.Job =
	{
		id: null,
		name: null,
		description: null,
		cron: null,
		signals: new Array(),
		
		load: function(data)
		{
			this.id = data["id"];
			this.name = data["name"];
			this.description = data["description"];
			this.cron = data["cron"];
			
			$(data["signals"]).each($.proxy(function(key, signal){
			    this.signals.push(HC.Signal.load(signal));
	        }, this));

			return this;
		},
		
		load_by_id: function(id, callback)
		{
			var request  = $.ajax({
				url: "/job/sql_load?job_id=" + id,
				type: "GET",
				dataType: "json"
			});
			
			request.fail($.proxy(function(response){
			    HC.request_error("Could not load job \"" + this.id + "\"", response);
				
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
				url: "/job/" + this.id + "/sql_delete",
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
				HC.success("Job \"<strong>" + this.name + "</strong>\" deleted.", function()
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
				url: "/scheduler/save_job",
				type: "POST",
				dataType: "json",
				data: $.toJSON({ // TODO: Do we need explicit JSON conversion?
					id: this.id,
					name: this.name, 
					description: this.description,
					cron: this.cron,
					signals: this.signals
				})
			});
			
			request.fail(function(response){
			    HC.request_error("Error while saving job", response);
				
				if(callback != undefined)
					callback(false, response);				
			});
			
			request.done($.proxy(function()
			{ 
				HC.success("Job \"" + this.name + "\" successfully saved.");
				
				if(callback != undefined)
					callback(true, null);				
			}, this));
		},
		
		send: function(callback)
		{
		    var rsend = function(signals)
		    {
		        if(signals.length == 0)
		        {
		            if(callback != undefined)
		                callback(true);
		            
		            return;
		        }
		        
		        var signal = signals.pop();
		        
		        signal.send(signal.dev_name, function(success)
                {
		            if(success) 
		                rsend(signals);
		            
		            else
		            {
		                if(callback != undefined)
		                    callback(false);
		            }
                });
		    };
		    
		    rsend($.extend(true, [], this.signals).reverse());
		}
	}
})( jQuery );
	