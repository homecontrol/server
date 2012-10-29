(function($)
{
	$.extend(HC.Job,
	{
        $signals: null,
        loader_signals: null,
        
		init: function()
		{
            this.$signals = $("#signals");
            this.loader_signals = this.$signals.HC("Loader");
            
			var token = document.location.href.match(/job_id=([^&]+)/);
			if(token == null)
			{
	            // Disable send and delete button when creating new jobs.
	            $(".btn-run").prop("disabled", true).addClass("disabled");
	            $(".btn-delete").prop("disabled", true).addClass("disabled");
	            
	            this.set_handlers();
			}
			else this.load_by_id(token[1], $.proxy(this.set_handlers, this));			
			
			return this;			
		},
		
		set_handlers: function()
		{
			var $confirm = $(".templates .dialog-delete-job-confirm");
			var $input_name = $(".job-name");
			var $input_desc = $(".job-description");
			var $input_cron = $(".job-cron");

			this.update_signal_table();
						
			$confirm.dialog({
				title: $confirm.data("title"),
				modal: true,
				resizable: false,
				width: $confirm.outerWidth(true) + "px",
				autoOpen: false
			});
			
			$(".btn-save").click($.proxy(function()
			{
				this.name = $input_name.val();				
				this.description = $input_desc.val();
				this.cron = $input_cron.val();
				
				var is_new = (this.id == null);
				this.save($.proxy(function(success)
		        {
				    if(!success || !is_new) return;
				    
				    // Redirect to new job page.
				    document.location.href = "/job/view?job_id=" + this.id;
				    
		        }, this));
				
				return false;
				
			}, this));
			
			$(".btn-run").click($.proxy(function()
            {
			    $(".btn-run").prop("disabled", true).addClass("disabled");
			    
			    this.send(function(){ 
                    $(".btn-run").prop("disabled", false).removeClass("disabled"); });
			    
                return false;
                
            }, this));
			
			$(".btn-delete").click($.proxy(function()
			{
				$(".job-name", $confirm).html(this.name);
				$confirm.dialog("open");
				return false;
				
			}, this));

			$(".btn-ok", $confirm).click($.proxy(function()
			{
				this.delete(function()
				{
					if(document.referrer != "") document.location.href = document.referrer;
					else document.location.href = "/";
					return false;
				});
				
				$confirm.dialog("close");
				return false;
				
			}, this));
				
			$(".btn-cancel", $confirm).click(function()
			{				
				$confirm.dialog("close");
				return false;
			});
			
			$(".btn-add-signal").click($.proxy(function()
	        {
			    var signal_id = $(".add-signal select").val(); 
	            var signal = Object.create(HC.Signal);
	            
	            signal.load_by_id(signal_id, $.proxy(function(success, response)
	            {
	                if(!success) return;
	                this.signals.push(signal);
	                this.update_signal_table();
	                
	            }, this));
			    
			    return false;
			        
	        }, this));
			
            $(".btn-add-delay ul.dropdown-menu a").click($.proxy(function(event)
            {
                // Create delay signal
                var signal = Object.create(HC.Signal);
                signal.delay = $(event.target).data("delay");
                this.signals.push(signal);
                this.update_signal_table();
                
                return false;
                
            }, this));			
		},
		
		update_signal_table: function(skip_hide)
		{
		    HC.Signal.update_signal_table(this.$signals, this.signals, this.loader_signals, skip_hide);
		    
		    $("tbody tr", this.$signals).draggable(
            {
                axis: "y",
                containment: "parent",
                helper: $.proxy(function(event)
                {
                    var $drag = $("<div><table></table></div>").
                        find("table").css("width", this.$signals.width() + "px").
                        append($(event.target).closest('tr').clone());
                    
                    $("td", $(event.target).closest('tr')).each(function(i, row){
                        $($("td", $drag).get(i)).width($(row).width()); 
                    });
                           
                    return $drag.end();
                    
                }, this)
            });
		    
		    var job = this;
		    $("tbody tr", this.$signals).droppable(
            {
                drop: function(event, ui)
                {
                    var from = ui.draggable.get(0).rowIndex - 3;
                    var to = this.rowIndex - 3;
                    
                    var foo = job.signals[from];
                    job.signals[from] = job.signals[to];
                    job.signals[to] = foo;
                    
                    job.update_signal_table(true);
	            }
	        });
		}
	});
	
	$(document).ready(function()
	{
		window.job = Object.create(HC.Job);
		window.job.init();
	});
})(jQuery);