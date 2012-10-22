(function($)
{
	$.extend(HC.Job,
	{
		init: function()
		{
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
			// TODO: Signals? Positions?
						
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
				this.save();
				
				return false;
				
			}, this));
			
			$(".btn-run").click($.proxy(function()
            {
			    $(".btn-run").prop("disabled", true).addClass("disabled");
			    
			    this.send();

                this.send(dev_name, function(){ 
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
		}		
	});
	
	$(document).ready(function()
	{
		window.job = Object.create(HC.Job);
		window.job.init();
	});
})(jQuery);