(function($)
{
	$.extend(HC.Signal,
	{
		init: function()
		{
			var token = document.location.href.match(/signal_id=([^&]+)/);
			if(token.length == 0)
				return this;
			
			this.load_by_id(token[1], $.proxy(this.set_handlers, this));			
			
			return this;			
		},
		
		set_handlers: function()
		{
			var $confirm = $(".templates .dialog-delete-signal-confirm");
			var $input_name = $(".signal-name");
			var $input_vendor = $(".signal-vendor");
			var $input_desc = $(".signal-description");
			var $input_device = $(".signal-device");
			
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
				this.vendor = $input_vendor.val();
				this.description = $input_desc.val();
				this.save();
				
				return false;
				
			}, this));
			
			$(".btn-send").click($.proxy(function()
            {
			    $(".btn-send").prop("disabled", true).addClass("disabled");
                var dev_name = $input_device.val();
                this.send(dev_name, function(){ 
                    $(".btn-send").prop("disabled", false).removeClass("disabled"); });                
                return false;
                
            }, this));			
			
			$(".btn-delete").click($.proxy(function()
			{
				$(".signal-name", $confirm).html(this.name);
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
		},
		
        update_signal_table: function($table, signals, loader)
        {
            $table.hide();
            if(loader != undefined) loader.show();
            
            var $tbody = $("tbody", $table);
            $("tr:not(.template)", $tbody).remove();
            $.each(signals, function(i, signal)
            {
                var $row = $("tr.template", $table).clone();
                $row.removeClass("template").appendTo($tbody);
                
                var data = $.extend(true, {}, signal, {
                    "events": $(document.createElement("div")), 
                });
                
                signal.event_types.sort();
                for(var i in signal.event_types)
                {
                    var type = signal.event_types[i];
                    var num = 0;
                    for(var j in signal.events)
                    {
                        if(type != signal.events[j].type)
                            continue;
                        
                        num ++;
                    }
                    
                    var $el = $(document.createElement("span"));
                    $el.html(num + "x " + type);
                    $el.addClass("label");
                    
                    switch(type)
                    {
                        case "ir": $el.addClass("label-important"); break;
                        case "rf": $el.addClass("label-warning"); break;                          
                    }
                    
                    $el.appendTo(data.events);
                }
                data.events = data.events.html();
                
                for(var name in data)
                    $row.html($row.html().replace("#" + name, data[name]));
                
                // Add signal id for further editing.
                $row.data("id", signal.id);
                $row.click(function(){location.href = "/signal/view?signal_id=" + signal.id;});
                
            });
            
            if(loader != undefined) loader.hide();
            $table.fadeIn();             
        }		
	});
})(jQuery);