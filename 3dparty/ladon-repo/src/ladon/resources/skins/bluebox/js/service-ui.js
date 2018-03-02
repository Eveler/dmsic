var jsonwps_primitives = ["string","number","float","boolean"];

function buildFormPart(service,legend,params_info,path,params_order,presets,selections) {
	if (!params_order) {
		params_order = [];
		$.each(params_info, function(key, value) { params_order.push(key) });
	}
	if (legend) {
		$("#form-fieldset").append('<div class="ui-state-default arg-object level'+(path.length-1)+'">'+legend+'</div>');
	}
	for (var p in params_order) {
		pname = params_order[p];
		pinfo = params_info[pname];
		ptype = pinfo;
		if (typeof(ptype)=="object") {
			ptype = pinfo["type"];
		}
		if ($.inArray(ptype,jsonwps_primitives)>-1) {
			show = true;
			value = null;
			if (presets && typeof(presets[pname])!="undefined") {
				if (presets[pname]==null) {
					continue;
				}
				show = false;
				value = presets[pname];
				if (typeof(value)=="object") {
					show = presets[pname].show;
					value = presets[pname].value;
				}
			}
			$("#form-fieldset").append('<div class="level'+path.length+'" id="'+path.length+'-'+pname+'")></div>')
			if (!show) {
				$("#form-fieldset #"+path.length+'-'+pname).hide();
			}
			if (selections && typeof(selections[pname])=="string") {
				$("#form-fieldset #"+path.length+'-'+pname).append('<label for="'+pname+'">'+pname+'</label>');
				$("#form-fieldset #"+path.length+'-'+pname).append('<select name="'+path.join('.')+(path.length ? '.':'')+pname+'" id="'+pname+'" class="'+selections[pname]+' text ui-widget-content ui-corner-all" />');
			}
			else {
				if (ptype=="boolean") {
					$("#form-fieldset #"+path.length+'-'+pname).append('<input type="checkbox" name="'+path.join('.')+(path.length ? '.':'')+pname+'" id="'+pname+'" class="ui-widget-content ui-corner-all"/> '+pname);
				}
				else {
					$("#form-fieldset #"+path.length+'-'+pname).append('<label for="'+pname+'">'+pname+'</label>');
					$("#form-fieldset #"+path.length+'-'+pname).append('<input type="text" name="'+path.join('.')+(path.length ? '.':'')+pname+'" id="'+pname+'" class="text ui-widget-content ui-corner-all" />');
				}
			}
			if (value!=null) { 
				$("#form-fieldset #"+path.length+'-'+pname).find("input[name=\""+path.join('.')+(path.length ? '.':'')+pname+"\"]").val(value);
			}
		}
		else if ($.isArray(ptype)) {
			$("#form-fieldset").append('<div class="level'+path.length+'" id="'+path.length+'-'+pname+'")> LIST HERE </div>')
			$("#form-fieldset #"+path.length+'-'+pname).append('<label for="'+pname+'">'+pname+'</label>');
		}
		else {
			newpath = path.slice();
			newpath.push(pname);
			newpresets = null;
			if (presets && typeof(presets[pname])=="object") {
				newpresets = presets[pname];
			}
			newselections = null;
			if (selections && typeof(selections[pname])=="object") {
				newselections = selections[pname];
			}
			console.debug(newpresets);
			buildFormPart(service,pname,service.jsonrpc_desc.types[ptype],newpath,null,newpresets,newselections);
		}
	}
}

var rx_listitem = RegExp(/item-(\d+)/); 
function formDomInsert(service,pname,ptype,path,element,defval) {
	var presets = null;
	var selections = null;
	if ($.inArray(ptype,jsonwps_primitives)>-1) {
		show = true;
		value = null;
		if (presets && typeof(presets[pname])!="undefined") {
			if (presets[pname]==null) {
				return;
			}
			show = false;
			value = presets[pname];
			if (typeof(value)=="object") {
				show = presets[pname].show;
				value = presets[pname].value;
			}
		}
		var input_div = $('<div id="'+path.length+'-'+pname+'" class="param-line"></div>');
		$(element).append(input_div);
		if (!show) {
			input_div.hide();
		}
		if (selections && typeof(selections[pname])=="string") {
			input_div.append('<div class="label">'+pname+'</div>');
			input_div.append('<select role="param" name="'+path.join('.')+(path.length ? '.':'')+pname+'" class="'+selections[pname]+' text ui-widget-content ui-corner-all" />');
		}
		else {
			if (ptype=="boolean") {
				var chkbox = $('<input role="param" type="checkbox" name="'+path.join('.')+(path.length ? '.':'')+pname+'" class="ui-widget-content ui-corner-all"/>');
				if (defval!=null) {
					chkbox.attr('checked',defval?true:false);
				}
				input_div.append($('<div class="value"></div>').append(chkbox).append(pname));
			}
			else {
				input_div.append('<div class="label">'+pname+'</div>');
				var valinput = $('<input role="param" type="text" name="'+path.join('.')+(path.length ? '.':'')+pname+'" class="text ui-widget-content ui-corner-all" />');
				if (defval!=null) {
					valinput.val(defval);
				}
				input_div.append($('<div class="value"></div>').append(valinput));
			}
		}
		if (value!=null) {
			input_div.find("input[name=\""+path.join('.')+(path.length ? '.':'')+pname+"\"]").val(value);
		}
	}
	else if ($.isArray(ptype)) {
		var list_div = $('<div class="list" id="'+path.length+'-'+pname+'"></div>')
		$(element).append(list_div)
		list_div.append('<div class="label">'+pname+'</div>');
		var add_button = $('<button> + </button>');
		list_div.append(add_button);
		var newpath = path.slice();
		newpath.push(pname);
		var bullet_elem = $('<ul name="'+newpath.join('.')+'"></ul>');
		list_div.append(bullet_elem);
		add_button.click( function () {
			var item_idx = bullet_elem.find('li').length;
			var form_part = $('<li name="'+item_idx+'"></li>');
			bullet_elem.append(form_part);
			var pptype = ptype[0];
// 			if (ptype in service.jsonrpc_desc.types) {
// 				pptype = service.jsonrpc_desc.types[ptype];
// 			}
// 			console.debug(pptype);
			formDomInsert(service,"item-"+item_idx,pptype,newpath,form_part);
		});
	}
	else if (ptype in service.jsonrpc_desc.types) {
		newpath = path.slice();
		newpath.push(pname);
// 		var level = 0;
// 		for (var idx in newpath) {
// 			console.debug(newpath[idx]);
// 			if (rx_listitem.test(newpath[idx])) {
// 				level = 0;
// 				continue
// 			}
// 			level++;
// 		}
		
		var form_part = $('<div name="'+newpath.join(".")+'"><div class="title">'+pname+' (' + ptype + ')</div></div>');
		$(element).append(form_part);
// 			newpresets = null;
// 			if (presets && typeof(presets[pname])=="object") {
// 				newpresets = presets[pname];
// 			}
// 			newselections = null;
// 			if (selections && typeof(selections[pname])=="object") {
// 				newselections = selections[pname];
// 			}
		formBuilder(service,service.jsonrpc_desc.types[ptype],null,newpath,form_part);
	}
}



function formBuilder(service,params_info,params_order,path,element) {
	$(element).addClass('class-type');
	if (!params_order) {
		params_order = [];
		$.each(params_info, function(key, value) { params_order.push(key) });
	}
	var presets = null;
	var selections = null;
	for (var p in params_order) {
		var pname = params_order[p];
		var pinfo = params_info[pname];
		var ptype = pinfo;
		if (typeof(ptype)=="object") {
			ptype = pinfo["type"];
		}
		var defval = pinfo.default;
		formDomInsert(service,pname,ptype,path,element,defval);
	}
}

function callFormBuilder(service,method,options) {
	$("#method-args-form").children().remove();
	$("#response-outerdiv").removeClass();
	$("#response-data").html("");
	var method_info = service.methodInfo(method);
	var params_info = method_info.params_info;
	var params_order = method_info.params_order;
	$("div#service-call div#title").html(method);
	formBuilder(service,params_info,params_order,[],$("#method-args-form"));
	var run_button = $("<button>Run</button>");
	run_button.click(function() {
		$("#response-outerdiv").removeClass();
		$("#response-outerdiv").addClass("waiting");
		service.callMethod(method,formToObject(),null,function(resp,reflection,fullresp,req) {
			$("#response-status").html("<b>Status code: " + req.status + "</b>");
			if (fullresp.type == 'jsonwsp/fault') {
				$("#response-outerdiv").removeClass();
				$("#response-outerdiv").addClass("servicefault");
				$("#response-data").html(JSON.stringify(fullresp.fault,null,4)+"\n");
			}
			else if (fullresp.type == 'jsonwsp/response') {
				$("#response-outerdiv").removeClass();
				$("#response-outerdiv").addClass("success");
				$("#response-data").html(JSON.stringify(resp,null,4));
			}
			else {
				$("#response-outerdiv").removeClass();
				$("#response-outerdiv").addClass("serverfault");
				if (fullresp.type == 'serverfault') {
					$("#response-data").html(fullresp.fault);
				}
				else {
					$("#response-data").html(JSON.stringify(fullresp,null,4));
				}
			}
		});
	});
	var cancel_button = $("<button>Cancel</button>");
	cancel_button.click(function() {
		$("#service-call").fadeOut();
	});
	var buttons = $("<div class='invoke-buttons'></div>");
	buttons.append(cancel_button,run_button);
	$("#method-args-form").append(buttons);
	$("#service-call").fadeIn();
}

function extendObject(obj,path,value) {
	var path = path.split(".");
	obj_point = obj;
	for (var idx=0; idx<path.length-1; idx++) {
		key = path[idx];
		m = rx_listitem.exec(key);
		if (m) {
			key = m[1];
		}
		if (key in obj_point) {
			obj_point = obj_point[key];
			continue;
		}
		else {
			var new_obj = {};
			obj_point[key] = new_obj;
			obj_point = new_obj;
			continue;
		}
	}
	var leaf = path[path.length-1];
	m = rx_listitem.exec(leaf);
	if (m) {
		obj_point[m[1]] = value;
	}
	else {
		obj_point[path[path.length-1]] = value;
	}
	return obj;
}

$.fn.sortByDepth = function() {
    var ar = this.map(function() {
            return {length: $(this).parents().length, elt: this}
        }).get(),
        result = [],
        i = ar.length;


    ar.sort(function(a, b) {
        return a.length - b.length;
    });

    while (i--) {
        result.push(ar[i].elt);
    }
    return $(result);
};

function flattenObject(obj,path) {
	var path = path.split('.');
	obj_pointer = obj;
	parent = obj;
	for (var idx=0; idx<path.length; idx++) {
		var key = path[idx];
		m = rx_listitem.exec(key);
		if (m) {
			if (m[1] in obj_pointer) {
				parent = obj_pointer;
				obj_pointer = obj_pointer[m[1]];
			}
			else {
				if (idx==path.length-1) {
					obj_pointer[m[1]] = [];
				}
				return;
			}
		}
		else {
			if (key in obj_pointer) {
				parent = obj_pointer;
				obj_pointer = obj_pointer[key];
			}
			else {
				if (idx==path.length-1) {
					obj_pointer[key] = [];
				}
				return;
			}
		}
	}
	parent[key] = $.map(obj_pointer, function(val, key) { return val; });
}

function formToObject() {
	var obj = {}
	$("#method-args-form").find("*[role=param]").each( function() {
		var val = $(this).val();
		if ($(this).attr("type")=="checkbox") {
			val = $(this).is(":checked")
		}
		extendObject(obj,$(this).attr('name'),val);
	});
	$("#method-args-form").find("ul").sortByDepth().map( function() {
		flattenObject(obj,$(this).attr('name'));
	});
	return obj;
}

function removeNullKeys(obj,inrecursion) {
	var obj2 = obj;
	if (!inrecursion) {
		obj2 = $.extend({},obj);
	}
	
	$.each(obj2, function(key, val) {
		if (val instanceof Object) {
			removeNullKeys(val,true);
		}
		else if (val==null) {
			delete obj2[key];
		}
	});
	return obj2;
}

function invokeMethod(service,method,options) {
	var e = null;
	var cb = null;
	var presets = null;
	var selections = null;
	var multiselections = null;
	if (typeof(options)=='object') {
		e = options['mouseevent'];
		cb = options['callback'];
		presets = options['presets'];
		selections = options['selections'];
		multiselections = options['multiselections'];
	}
	var method_info = service.methodInfo(method);
	var params_info = method_info.params_info;
	var params_order = method_info.params_order;
	$("#form-fieldset").children().remove();
	
	buildFormPart(service,null, params_info,[],params_order,presets,selections);
	
	var pos = { my: "center", at: "center", of: window };
	if (e) {
		pos = [e.pageX-10,e.pageY+20];
	}
	$("#method-args-form").dialog( {
		position: pos,
		draggable: true,
		modal: true,
		title: method,
		buttons: [{ 
			text: "Ok", 
			click: function() {
				dlg = $(this);
				var args = {};
				$("#method-args-form input,select").each( function(obj) {
					name = $(this).attr("name");
					nameparts = name.split('.');
					var cur_argview = args;
					for (pidx in nameparts) {
						if (pidx == nameparts.length-1) {
							if ($(this).attr('type')=='checkbox') {
								cur_argview[nameparts[pidx]] = $(this).is(":checked");
							}
							else {
								cur_argview[nameparts[pidx]] = $(this).val();
							}
						}
						else {
							if (typeof(cur_argview[nameparts[pidx]])=='undefined') {
								cur_argview[nameparts[pidx]] = {};
							}
							cur_argview = cur_argview[nameparts[pidx]];
						}
					}
				});
				
				service.callMethod(method,args,null,function(res,reflection,full) {
					if (typeof(full.fault)=="object") {
						$("#dialog-error").children().remove();
						$("#dialog-error").append('<p>'+full.fault.string+'</p>');
						$("#dialog-error").dialog( {
							position: [pos[0]+20,pos[1]+20],
							draggable: true,
							modal: true,
							title: method + ' (Error)'
						});
					}
					else {
						dlg.dialog( "close" );
						if (cb) {
							cb(true,res);
						}
					}
				});
			}
		},{
			text: "Cancel", 
			click: function() {
				$( this ).dialog( "close" );
				if (cb) {
					cb(false);
				}
			}
		}
		]
	});
	$("#method-args-form").siblings("div.multiselections").remove();
	$("<div class='multiselections'></div>").insertAfter("#method-args-form");
	for (mskey in multiselections) {
		$("#method-args-form").siblings("div.multiselections").append("<div class='ui-state-default arg-object level0'>"+mskey+"</div>");
		$("#method-args-form").siblings("div.multiselections").append("<select class='"+multiselections[mskey]+"' multiple></select>");
	}
	$("#method-args-form").siblings("div.multiselections").find(".chzn-container").css("width","auto");
	$("#method-args-form").siblings("div.multiselections").find(".chzn-container").children().css("width","auto");
}

var object_cache = {};

function listObjects(service,method,target,options) {
	var args = null;
	var list_attr = null;
	var cb = null;
	var cacheid = null;
	var hide_columns = null;
	var click = null;
	var inner_attr = null;
	var multi_op_buttons = null;
	var single_op_buttons = null;
	
	if (typeof(options)=='object') {
		args = options['args'];
		list_attr = options['attribute'];
		inner_attr = options['innerattribute'];
		cacheid = options['cacheid'];
		hide_columns = options['hidecolumns'];
		cb = options['callback'];
		click = options['click'];
		multi_op_buttons = options['multiOperationalButtons'];
		single_op_buttons = options['singleOperationalButtons'];
	}
	service.callMethod(method,args,null,function(resp,reflection,full) {
		if (typeof(full.fault)=="object") {
			$("#dialog-error").children().remove();
			$("#dialog-error").append('<p>'+full.fault.string+'</p>');
			$("#dialog-error").dialog( {
				position: [pos[0]+20,pos[1]+20],
				draggable: true,
				modal: true,
				title: method + ' (Error)'
			});
		}
		$(target).children().remove();
		rtype_name = service.jsonrpc_desc.methods[method].ret_info.type;
		rtype = service.jsonrpc_desc.types[rtype_name];
		if (list_attr) {
			rtype = rtype[list_attr]['type'];
		}
		else {
			rtype = rtype['type'];
		}
		obj_type = service.jsonrpc_desc.types[rtype[0]];
		if (inner_attr) {
			obj_type = service.jsonrpc_desc.types[obj_type[inner_attr].type];
		}
		header_html = '<th>Select</th>';
		attr_list = [];
		for (var k in obj_type) {
			if (hide_columns && $.inArray(k,hide_columns)>-1) {
				continue;
			}
			attr_list.push(k);
			header_html += '<th>'+k+'</th>';
		}
		var cur_list = resp;
		if (list_attr) {
			cur_list = resp[list_attr];
		}
		if (cacheid) {
			object_cache[cacheid] = cur_list;
		}
		var table_data_rows = '';
		for (var ridx in cur_list) {
			row_data_html = '';
			row_data_html += '<td><input type="checkbox" class="delete-obj" value="'+ridx+'"/></td>';
			obj = cur_list[ridx];
			if (inner_attr) {
				obj = cur_list[ridx][inner_attr];
			}
			for (var aidx in attr_list) {
				data = obj[attr_list[aidx]];
				if (click && typeof(click[attr_list[aidx]])!="undefined") {
					row_data_html += '<td name="'+attr_list[aidx]+'"><a href="#" name="'+attr_list[aidx]+'">'+data+'</a></td>';
				}
				else {
					row_data_html += '<td name="'+attr_list[aidx]+'">'+data+'</td>';
				}
			}
			extraclass = ridx==cur_list.length-1 ? 'class="last-row"' : "";
			table_data_rows += '<tr '+extraclass+'>'+row_data_html+'</tr>';
		}
		$(target).append('<table id="object-data" cellspacing="0" cellpadding="0" class="ui-widget ui-corner-all ui-state-default"><tr class="ui-widget-header">'+header_html+'</tr>'+table_data_rows+'</table>');
		$(multi_op_buttons).attr("disabled", 'disabled').fadeTo(300,.5);
		$(single_op_buttons).attr("disabled", 'disabled').fadeTo(300,.5);
		$(target).find('input[type=checkbox]').click( function() {
			checked = $(target).find('input[type=checkbox]:checked');
			if (checked.length==0) {
				$(multi_op_buttons).attr("disabled", 'disabled').fadeTo(300,.5);
				$(single_op_buttons).attr("disabled", 'disabled').fadeTo(300,.5);
			}
			else if (checked.length==1) {
				$(single_op_buttons).attr("disabled", false).fadeTo(300,1);
				$(multi_op_buttons).attr("disabled", false).fadeTo(300,1);
			}
			else if (checked.length>1) {
				$(multi_op_buttons).attr("disabled", false);
				$(single_op_buttons).attr("disabled", 'disabled').fadeTo(300,.5);
			}
		});
		for (var col_name in click) {
			$(target).find("a[name="+col_name+"]").click( function () {
				cache_idx = $(this).parent().parent().find('input.delete-obj').val();
				click[col_name](cur_list[cache_idx]);
			});
		}
		if (cb) {
			cb();
		}
	});
}


function deleteObjects(service,method,pname,cacheid,options) {
	var obj_attr_name = null;
	parent_element = $("body");
	var cb = null;
	if (typeof(options)=='object') {
		parent_element = options['parent'];
		obj_attr_name = options['attribute'];
		cb = options['callback'];
	}
	delete_selected = $(parent_element).find(" .delete-obj:checked");
	jobs = delete_selected.length;
	delete_selected.each( function () {
		var args = {};
		if (obj_attr_name) {
			args[pname] = object_cache[cacheid][parseInt($(this).attr('value'))][obj_attr_name];
		}
		else {
			args[pname] = object_cache[cacheid][parseInt($(this).attr('value'))];
		}
		service.callMethod(method,removeNullKeys(args),null,function(result,reflection,full) {
			if (typeof(full.fault)=="object") {
				$("#dialog-error").children().remove();
				$("#dialog-error").append('<p>'+full.fault.string+'</p>');
				$("#dialog-error").dialog( {
					draggable: true,
					modal: true,
					title: method + ' (Error)'
				});
			}
			jobs--;
			if (jobs==0) {
				if (cb) {
					cb();
				}
			}
		});
	});
}

function init_service_ui(sname) {
	service = new JSONWSPClient();
	service.setViaProxy(true);
	service.loadDescription("jsonwsp/description",function() {
		service.setViaProxy(true);
		$(".invokable").css("cursor","pointer").click( function () {
			callFormBuilder(service,$(this).attr("name"));
		});
	});
}
