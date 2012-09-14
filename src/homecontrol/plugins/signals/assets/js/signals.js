(function($)
{
	HC.Signals =
	{
		$signals: null,
		loader_signals: null,
		
		$scheduler: null,
		loader_scheduler: null,
		
		init: function()
		{
			this.$signals = $("div#signals");
			this.loader_signals = this.$signals.HC("Loader");
			
			this.$scheduler = $("div#scheduler");
			this.loader_scheduler = this.$scheduler.HC("Loader");
			
			$("a[href=#signals]").on('shown', $.proxy(this.load_signals, this));
			$("a[href=#scheduler]").on('shown', $.proxy(this.load_scheduler, this));
			
			this.load_signals();
			
			return this;			
		},
		
		load_signals: function(e)
		{
			$("table", this.$signals).hide();
			this.loader_signals.show();
			

			this.loader_signals.hide();
			$("table", this.$signals).fadeIn();
		},
		
		load_scheduler: function(e)
		{
			$("table", this.$scheduler).hide();
			this.loader_scheduler.show();
			

			this.loader_scheduler.hide();
			$("table", this.$scheduler).fadeIn();			
		}
	};
	
	$(document).ready(function()
	{
		var signals = Object.create(HC.Signals);
		signals.init();
	});
})(jQuery);