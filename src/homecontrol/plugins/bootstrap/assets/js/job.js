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
			
			$(data["signals"]).each($.proxy(function(key, data)
	        {
			    var signal = Object.create(HC.Signal);
			    this.signals.push(signal.load(data));
			    
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
				data: HC.to_json(this)
			});
			
			request.fail(function(response){
			    HC.request_error("Error while saving job", response);
				
				if(callback != undefined)
					callback(false, response);				
			});
			
			request.done($.proxy(function(data)
			{
			    this.load(data); 
			    
				HC.success("Job \"" + this.name + "\" successfully saved.");
				
				if(callback != undefined)
					callback(true, data);
				
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
	