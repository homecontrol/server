(function($)
{
	HC.Scheduler =
	{
		$signals: null,
		loader_signals: null,
		
		$jobs : null,
		loader_jobs: null,
		
		init: function()
		{
			this.$signals = $("div#signals");
			this.loader_signals = this.$signals.HC("Loader");
			
			this.$jobs = $("div#jobs");
			this.loader_jobs = this.$jobs.HC("Loader");
			
			$("a[href=#signals]").on('shown', $.proxy(this.load_signals, this));
			$("a[href=#jobs]").on('shown', $.proxy(this.load_jobs, this));
			$("a[href=#create_job]").click(function (e)
	        {
			    e.preventDefault();
			    document.location.href = 'job/create';
	        });
    		
			this.load_signals();
			
			return this;			
		},
		
		load_signals: function(e)
		{
			$("table", this.$signals).hide();
			this.loader_signals.show();
			
			var request = $.ajax({
				url: "scheduler/load_signals?order_by=name", 
				type: "GET",
				dataType: "json"
			});
	
			request.done($.proxy(function(signals)
			{
				var $tbody = $("table tbody", this.$signals);
				$("tr:not(.template)", $tbody).remove();
				$.each(signals, $.proxy(function(i, signal)
				{
					var $row = $("table tr.template", this.$signals).clone();
					$row.removeClass("template").appendTo($tbody);
					
					var event_types = signal["event_types"]
					signal["num_events"] = signal["events"].length;
					signal["event_types"] = $(document.createElement("div"));					

					event_types.sort();
					for(var i in event_types)
					{
						var $el = $(document.createElement("span"));
						$el.html(event_types[i]);
						$el.addClass("label");
						
						switch(event_types[i])
						{
							case "ir":
								$el.addClass("label-important");
							break;
							case "rf":
								$el.addClass("label-warning");
							break;							
						}
						
						$el.appendTo(signal["event_types"]);
					}
					
					signal["event_types"] = signal["event_types"].html();
					
					for(var key in signal)
					{
						$row.html($row.html().replace("#" + key, signal[key]));
					}
					
					// Add signal id for further editing.
					$row.data("id", signal["id"]);	
					$row.click(function(){location.href = "/signal/view?signal_id=" + signal["id"];})
					
				}, this));
				
				this.loader_signals.hide();
				$("table", this.$signals).fadeIn();				
				
			}, this));
	
			request.fail($.proxy(function(response)
			{
				HC.request_error("Could not load signals", response);
				this.loader_signals.hide();
				$("table", this.$signals).fadeIn();				
				
			}, this));
		},
		
		load_jobs: function(e)
		{
			$("table", this.$jobs).hide();
			this.loader_jobs.show();
			
            var request = $.ajax({
                url: "scheduler/load_jobs?order_by=name", 
                type: "GET",
                dataType: "json"
            });			
			
            request.done($.proxy(function(jobs)
            {
                var $tbody = $("table tbody", this.$jobs);
                $("tr:not(.template)", $tbody).remove();
                $.each(jobs, $.proxy(function(i, job)
                {
                    var $row = $("table tr.template", this.$jobs).clone();
                    $row.removeClass("template").appendTo($tbody);
                    
                    for(var key in job)
                    {
                        $row.html($row.html().replace("#" + key, job[key]));
                    }
                    
                    // Add signal id for further editing.
                    $row.data("id", job["id"]);  
                    $row.click(function(){location.href = "/job/view?job_id=" + job["id"];})
                    
                }, this));
                
                this.loader_jobs.hide();
                $("table", this.$jobs).fadeIn();             
                
            }, this));
    
            request.fail($.proxy(function(response)
            {
                HC.request_error("Could not load jobs", response);
                this.loader_jobs.hide();
                $("table", this.$jobs).fadeIn();             
                
            }, this));			
		}
	};
	
	$(document).ready(function()
	{
		var scheduler = Object.create(HC.Scheduler);
		scheduler.init();
	});
})(jQuery);