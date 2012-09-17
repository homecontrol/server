/**
 * The following inheritance pattern is based on an article found at 
 * http://alexsexton.com/blog/2010/02/using-inheritance-patterns-to-organize-large-jquery-applications/
 */

// Make sure Object.create is available in the browser (for our prototypal inheritance)
// Note this is not entirely equal to native Object.create, but compatible with our use-case
if (typeof Object.create !== 'function')
{
	Object.create = function(o)
	{
		// optionally move this outside the declaration and into a closure if you need more speed.
		function F()
		{ } 
		
		F.prototype = o;
		return new F();
	};
}

(function($)
{	
	HC = 
	{
		info: function(msg, delay)
		{
			if(delay == undefined) delay = 1000 * 5;
			return this.alert("info", msg, delay);
		},
		
		error: function(msg, delay)
		{
			if(delay == undefined) delay = 1000 * 25;
			
			// Don't show multiple the same message twice!
			$alerts = $("body > div.container .alert-error span");
			for(var i = 0; i < $alerts.length; i ++)
			{
				if($($alerts[i]).html() == msg)
					return;
			}
			
			return this.alert("error", msg, delay);
		},
		
		success: function(msg, delay)
		{
			if(delay == undefined) delay = 1000 * 5;
			return this.alert("success", msg, delay);
		},
		
		alert: function(type, msg, delay)
		{
			$alert = $(".template-alert").clone();
			$("span", $alert).append(msg);
			
			return $alert.prependTo("body > div.container").
				removeClass("template-alert"). 
				addClass("alert fade in alert-" + type).
				slideDown("fast").
				delay(delay).
				slideUp("fast");
		}
	};

	HC.TYPE_IR = "ir";
	HC.TYPE_RF = "rf";

	HC.Loader = function() 
	{
		return $(".template-loader").clone().
			removeClass("template-loader").
			addClass("loader").
			width(this.parent().width()).
			appendTo(this.parent());
	};
	
	/**
	 * Integrate HC namespace into jQuery, see http://docs.jquery.com/Plugins/Authoring
	 */
	$.fn.HC = function(method)
	{
		method = $.proxy(eval("HC." + method), this);
		return method.apply(this, Array.prototype.slice.call(arguments, 1));
	};

})( jQuery );