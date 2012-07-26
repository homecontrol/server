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
			$(".template-alert").clone().
				prependTo("body > div.container").
				removeClass("template-alert"). 
				addClass("alert fade in alert-" + type).
				append(msg).
				slideDown("fast");
		}
	};
	
	HC.Loader = function() 
	{
		return $(".template-loader").clone().
			removeClass("template-loader").
			addClass("loader").
			width(this.parent().width()).
			appendTo(this.parent());
	};

	HC.Device = 
	{
		init: function(name)
		{
			this.name = name;
			return this;
		},
		
		get_status: function(callback)
		{
			var request = $.ajax({
				url: "device/" + this.name + "/get_info",
				type: "GET",
				dataType: "json"
			});
	
			request.done($.proxy(function(info)
			{
				if(callback != undefined)
					callback(info);
				
			}), this);
	
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could not get device status</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
				
				if(callback != undefined)
					callback(null);
				
			}), this);
		},
		
		rf_send_tristate: function(tristate, callback)
		{
			var request = $.ajax({
				url: "device/" + this.name + "/rf_send_tristate/" + tristate,
				type: "GET",
				dataType: "json"
			});
	
			request.done($.proxy(function(info)
			{
				if(callback != undefined)
					callback(true);
				
			}), this);
	
			request.fail($.proxy(function(response)
			{
				HC.error("<strong>Could not send rf tristate</strong>: " + 
					     response.statusText + " (Error " + response.status + ")");
				
				if(callback != undefined)
					callback(false);
				
			}), this);
		},
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