(function($)
{
	HC.Scheduler =
	{
		$signals: null,
		signals: new Array(),
		loader_signals: null,
		
		$jobs : null,
		jobs: new Array(),
		loader_jobs: null,
		
		init: function()
		{
			this.$signals = $("#signals");
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
			
			// By default, load the signal pane
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
	            this.signals = new Array();
	            $(signals).each($.proxy(function(key, data)
	            {
	                var signal = Object.create(HC.Signal);
	                this.signals.push(signal.load(data));
	                
	            }, this));
	            
			    HC.Signal.update_signal_table(this.$signals, this.signals, this.loader_signals, true);			
				
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
                this.jobs = new Array();
                $.each(jobs, $.proxy(function(key, data)
                {
                    var job = Object.create(HC.Job);
                    this.jobs.push(job.load(data));
                    
                    var $row = $("table tr.template", this.$jobs).clone();
                    $row.removeClass("template").appendTo($tbody);
                    
                    for(var key in data)
                    {
                        var value = data[key];
                        if(value == null) value = "";
                        $("." + key, $row).html(value);
                    }
                    
                    // Add signal id for further editing.
                    $row.data("id", job.id);  
                    $row.click(function(){location.href = "/job/view?job_id=" + job.id;})
                    
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