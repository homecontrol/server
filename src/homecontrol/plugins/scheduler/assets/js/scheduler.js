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
			this.loader_signals.show();
			
			var request = $.ajax({
				url: "scheduler/load_signals?order_by=name", 
				type: "GET",
				dataType: "json"
			});
	
			request.done($.proxy(function(signals)
			{
			    HC.Signal.update_signal_table($("table", this.$signals), signals, this.loader_signals, true);			
				
			}, this));
	
			request.fail($.proxy(function(response)
			{
			    this.loader_signals.hide();
				HC.request_error("Could not load signals", response);
				
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
                        var value = job[key];
                        if(value == null) value = "";
                        $row.html($row.html().replace("#" + key, value));
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