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
		
		next_run_updater: {},
		
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
			    document.location.href = '/job/create';
	        });
						
			if(document.location.hash == "#jobs") $('a[href="#jobs"]').tab('show');
			// By default, load the signal pane
			else $('a[href="#signals"]').tab('show');
    		
			return this;
		},
		
		load_signals: function(e)
		{
		    document.location.hash = "#signals";
		    this.$signals.find("table").hide();
			this.loader_signals.show();
			
			var request = $.ajax({
				url: "/scheduler/load_signals?order_by=name", 
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
	            
			    HC.Signal.update_signal_table(this.$signals.find("table"), this.signals, this.loader_signals);			
				
			}, this));
	
			request.fail($.proxy(function(response)
			{
			    this.loader_signals.hide();
				HC.request_error("Could not load signals", response);
				
			}, this));
		},
		
		load_jobs: function(e)
		{
		    document.location.hash = "#jobs";
		    this.$jobs.find("table").hide();
			this.loader_jobs.show();
			
            var request = $.ajax({ url: "/scheduler/load_jobs?order_by=name", type: "GET", dataType: "json" });			
			
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
                    
                    // Load date/time of next run
                    this.get_next_run(job, $row);

                    // Handlers for (un)scheduling the job
                    $(".icon-play", $row).click($.proxy(function(){ this.schedule_job(job, $row); return false; }, this));
                    $(".icon-pause", $row).click($.proxy(function(){ this.unschedule_job(job, $row); return false; }, this));
                    
                    // Handler to run job
                    $(".btn-run", $row).click(function(){
                        $(".btn-run", $row).prop("disabled", true).addClass("disabled");
                        job.send(function(){ 
                            $(".btn-run", $row).prop("disabled", false).removeClass("disabled"); });
                        return false;
                    });
                    
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
		},
		
		get_next_run: function(job, $row)
		{
		    var request = $.ajax({ url: "/scheduler/get_next_run?job_id=" + job.id, type: "GET", dataType: "json" });
            request.done($.proxy(function(next_run)
            {
                if(next_run == null)
                {
                    $(".next-run", $row).html("");
                    if(job.cron == null) $(".icon-play, .icon-pause", $row).addClass("disabled");
                    else 
                    {
                        $(".icon-play", $row).removeClass("disabled");
                        $(".icon-pause", $row).addClass("disabled");
                    }
                }
                else
                {
                    var next_run_date = new Date(next_run);
                    var now = new Date();
                    var ms = Math.abs(next_run_date - now) + 500;
                    
                    $(".icon-play", $row).addClass("disabled");
                    $(".icon-pause", $row).removeClass("disabled");
                    $(".next-run", $row).html(next_run_date.toLocaleString());
                    
                    if(this.next_run_updater[job.id] != undefined) clearTimeout(this.next_run_updater[job.id]);
                    this.next_run_updater[job.id] = setTimeout($.proxy(function(){ this.get_next_run(job, $row) }, this), ms);
                }
                
            }, this));
            
            request.fail($.proxy(function() { $(".icon-play, .icon-pause", $row).addClass("disabled"); }, this));
		},
		
		schedule_job: function(job, $row)
		{
		    if($(".icon-play", $row).hasClass("disabled")) return;
		    var request = $.ajax({ url: "/scheduler/schedule_job?job_id=" + job.id, type: "GET", dataType: "json" });
		    request.done($.proxy(function() { this.get_next_run(job, $row); }, this)); 
		    request.fail(function(response){ HC.request_error("Could not schedule job \"" + job.name + "\"", response); });
		},
		
		unschedule_job: function(job, $row)
		{
		    if($(".icon-pause", $row).hasClass("disabled")) return;
            var request = $.ajax({ url: "/scheduler/unschedule_job?job_id=" + job.id, type: "GET", dataType: "json" });
            request.done($.proxy(function() { this.get_next_run(job, $row); }, this)); 
            request.fail(function(response){ HC.request_error("Could not unschedule job \"" + job.name + "\"", response); });
		}
	};
	
	$(document).ready(function()
	{
		var scheduler = Object.create(HC.Scheduler);
		scheduler.init();
	});
})(jQuery);