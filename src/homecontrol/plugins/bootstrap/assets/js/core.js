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
		info: function(msg)
		{
			return this.alert("info", msg);
		},
		
		error: function(msg)
		{
			return this.alert("error", msg);
		},
		
		success: function(msg)
		{
			return this.alert("success", msg);
		},
		
		alert: function(type, msg)
		{
			// TODO: Look for similar alerts and don't print the
			// same alert twice but set and increase a counter.
			
			$(".template-alert").clone().
				prependTo("body > div.container").
				removeClass("template-alert"). 
				addClass("alert fade in alert-" + type).
				append(msg).
				slideDown("fast");
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