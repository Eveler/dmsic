# -*- coding: utf-8 -*-

from ladon.compat import PORTABLE_STRING

catalog_default_template = PORTABLE_STRING("""
<!DOCTYPE html>
<html>
	<head>
		<meta content="text/html; charset={{ charset }}" http-equiv="Content-Type" />
		<title>{{ catalog_name }}</title>
		<style>
{{ css }}
{{ extra_css }}
		</style>
	</head>
	<body>
		<div class="catName">{{ catalog_name }}</div>
		<div class="catDesc">{{ catalog_desc }}</div>
		<div class="catContent">
			<ul class="catService">
{% for service in services %}
				<li>
					<b><a href="{{ service.servicename }}/{{ '?' if query_string }}{{query_string}}">{{ service.servicename }}</a></b><br/>
					{{ service.doc }}
				</li>
{% endfor %}
			</ul>
		</div>
		<div class="catGen">Powered by Ladon for Python</div>
	</body>
</html>
""")

service_default_template = PORTABLE_STRING("""
<html>
	<head>
		<meta content="text/html; charset={{ charset }}" http-equiv="Content-Type" />
		<title>{{ servicename }}</title>
		<style>
{{ css }}
		</style>
	</head>
	<body>
		<div class="serviceName">
			<div class="title">{{ servicename }}</div>
			<form method="get" class="skin-selector">
				<label for="skin-select">skins:</label>
				<select id="skin-select" name="skin" onchange="document.forms[0].submit()">
					<option value="">Default</option>
					{% for skin in skins %}
					<option value="{{skin}}"{% if skin == current_skin %} selected{% endif %}>{{ skin|title }}</option>
					{% endfor %}
				</select>
			</form>
		</div>
		<div class="serviceDesc">
			<span class="descriptionHead">Service Description:</span>
			<div class="docLines">
				{{ doc }}
			</div>
		</div>
		<div class="serviceInterfaces">
			<span class="interfaceHead">Available Interfaces:</span>
			<ul class="interfaceList">
{% for interface in interfaces %}
				<li>{{ interface }} [ <a href="{{ interface }}">url</a> <a href="{{ interface }}/description">description</a> ]</li>
{% endfor %}
			</ul>
		</div>
		<div class="serviceDocumentation">
			<span class="methodsHead">Methods:</span>
			<ul class="methodList">
{% for method in methods %}
				<li class="methodEntry">
					<div class="methodDef">
						<span class="methodName">{{ method.methodname }}</span>
						(
	{% set sep = '' %}
	{% for param in method.params %}
						{{ sep }} 
						<span class="paramType">
		{% if param.ladontype %}
							<a href="#{{ param.ladontype }}">{{ param.type }}</a>
		{% else %}
							{{ param.type }}
		{% endif %}
						</span> 
						<span class="paramName">{{ param.name }}</span>
		{% set sep = ',' %}
	{% endfor %}
						)
					</div>
					<div class="docLines">
						{{ method.doc }}
					</div>
	{% for param in method.params %}
		{% if loop.first %}
					<u>Paramters:</u>
					<ul>
		{% endif %}
						<li class="paramDesc">
							<span class="paramName">{{ param.name }}</span>: <span class="paramType">
		{% if param.ladontype %}
								<a href="#{{ param.ladontype }}">{{ param.type }}</a>
		{% else %}
								{{ param.type }}
		{% endif %}
							</span>
		{% if param.optional %}
								[ default: {{ param.default }} ]
		{% endif %}
							<br/>
							<div class="docLines">
								{{ param.doc }}
							</div>
						</li>
		{% if loop.last %}
					</ul>
		{% endif %}
	{% endfor %}
					<u>Returns:</u>
					<span class="paramType">
	{% if method.returns.ladontype %}
						<a href="#{{ method.returns.ladontype }}">{{ method.returns.type }}</a>
	{% else %}
						{{ method.returns.type }}
	{% endif %}
					</span>
					<div class="docLines">
						{{ method.returns.doc }}
					</div>
				</li>
{% endfor %}
			</ul>
			<span class="TypesHead">Types:</span>
			<ul>
{% for type in types %}
				<li>
					<div class="typeDef"><a name="{{ type.name }}"><span class="typeName">{{ type.name }}</span></a></div>
					<br/>
					<u>Attributes:</u>
					<ul>
	{% for k,v in type.attributes.items() %}
						<li class="typeAttrib">
							<span class="paramName">{{ k }}</span>:
							<span class="paramType">
		{% if v.ladontype %}
							<a href="#${v.ladontype}">{{ v.type }}</a>
		{% else %}
								{{ v.type }}
		{% endif %}
							</span>
						</li>
	{% endfor %}
					</ul>
				</li>
{% endfor %}
			</ul>
		</div>
		<div class="catGen">Powered by Ladon for Python</div>
	</body>
</html>
""")
