<?php

class htmlformLadonInterface implements phpLadonInterface
{

	
	public function outputServiceDescription($serviceDescription)
	{
?><html>
	<head>
		<title><?php echo $serviceDescription["serviceName"]; ?></title>
		<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>
		<style type="text/css">
			body { background-color: white; margin: 0px; padding: 0px; font-size: 12px; font-family: verdana; }
			div.catName { padding: 10px; background-color: #036; font-size: 20px; color: white; }
			div.catDesc { padding: 20px; padding-bottom: 10px; }
			ul.catService { }
			span.interfaceHead { padding-left: 20px; font-weight: bold; }
			ul.catService li { padding-bottom: 10px; }
			div.serviceDesc { text-align: center; padding: 10px; }
			div.catInterfaces { padding: 10px; padding-left: 30px; padding-top: 0px; }
			div.catGen { text-align: center; font-style:italic; margin-top: 20px; margin-bottom: 20px; }
            table.method { margin-top: 10px; width: 650px; }
            td.methodname { background-color: #036; color: white; font-size: 14px; font-weight: bold; padding: 4px; }
            td.methodcontent { background-color: #eee; padding: 5px; border: 1px solid #036; }
            td { padding: 3px; }
		</style>
	</head>
	<body>
		<div class=catName><?php echo $serviceDescription["serviceName"]; ?></div>
		<div class=catDesc><?php echo $serviceDescription["description"]; ?></div>
		<div class=catContent>
		
			<span class="interfaceHead">Methods:</span>
			<ul class=catService>
			<?php 
				foreach ($serviceDescription["methods"] as $methodName => $methodData) {
                  $this->outputMethod($methodName,$methodData,$serviceDescription);
				}
			?>
			</ul>
		</div>
		<script type="text/javascript">
			function addArrayItem(elm) {
				$(elm).append($(elm).children(':first').html());
			}
		</script>
	</body>	
</html><?PHP
		
	}

    private function outputMethod($methodName,$methodData,$serviceDescription)
    {
      ?><table cellspacing="0" cellpadding="0" class="method">
        <tr><td class="methodname"><?PHP echo $methodName; ?></td></tr>
        <tr><td class="methodcontent">
            <form action="" method="post" style="padding: 0px; margin: 0px;">

              <table style="width: 100%; font-size: 12px; ">
              <?PHP
                foreach($methodData["params"] as $paramName => $paramData) {
                  $this->outputMethodParameter($paramName, $paramData, $serviceDescription);
                }
              ?>
              </table>

              <div style="text-align: right;">
              	<input type=hidden name="phpladonService" value="<?php echo $serviceDescription["serviceName"]; ?>">
              	<input type=hidden name="phpladonMethod" value="<?php echo $methodName; ?>">
                <input type="reset" value="Reset form">
                <input type="submit" value="Execute request">
              </div>

            </form>
        </td></tr>
      </table><?PHP
    }

    private function outputMethodParameter($parameterName,$parameterData,$serviceDescription)
    {
      ?><tr>
        <td valign=top><?PHP echo $parameterName; ?></td>
        <td><?php 
        	$this->outputType($parameterName, $parameterData["type"], $parameterData["isarray"], $serviceDescription);
        ?></td>
        <td valign=top><?php 
        	if(count($parameterData["doc_lines"]) > 0) {
        		?><div style="margin-top: 4px; cursor: help; background-color: #036; color: white; padding: 4px; font-weight: bold; font-size: 10px; width: 7px;" title="<?php echo implode(" ",$parameterData["doc_lines"]); ?>">
        			?
        		</div><?php	
        	}
        ?></td>
      </tr><?PHP
    }
    
  	private function outputType($name,$type,$isArray,$serviceDescription) 
  	{
  	
  		if($isArray) { ?>
  			<div style="padding: 2px; background-color: #36A; color: white;">
  				<div style="float: right; padding: 2px; font-size: 10px; cursor: pointer;" onClick="addArrayItem($(this).parent().next());">tilføj element</div>
  				Liste
  			</div>
  			<div style="border: 1px solid black;">
  		<?php }
  		
  		// Custom type
  		if(isset($serviceDescription["types"][$type])) {
  			echo "<div>";
  			$this->outputTypeForm($name,$type, $serviceDescription);
  			echo "</div>";
  		}
  		// Boolean type
  		else if(strtolower($type) == "bool" || strtolower($type) == "bool") {
  			?><div><input type=checkbox name="<?php echo $name; if($isArray) echo "[]"; ?>" value=1></div><?php	
  		}
  		// Text type
  		else {
  			?><div><input type=text size=40 name="<?php echo $name; if($isArray) echo "[]"; ?>"></div><?php	
  		}
  		
  		if($isArray) { ?>
  			</div>
  		<?php }
  	}
  	
    
    private function outputTypeForm($name,$typeName,$serviceDescription) 
    {

    	?><table cellspacing=0 cellpadding=0 style="margin: 5px; margin-top: 0px; font-size: 12px; border-left: 1px dashed #BBB; border-bottom: 1px dashed #BBB;">
    	<tr><td style="background-color: #36A; color: white;" colspan=3><?php echo $typeName; ?><td></tr>
    	<?php
    	
    	 foreach($serviceDescription["types"][$typeName]["properties"] as $propertyName => $propertyData) {
    	 	?><tr>
    	 		<td valign=top><?php echo $propertyName; ?></td>
    	 		<td valign=top><?php $this->outputType($name."_".$propertyName, $propertyData["type"], $propertyData["isarray"], $serviceDescription); ?>
    	 		<td valign=top><?php 
		        	if(count($propertyData["doc_lines"]) > 0) {
		        		?><div style="margin-top: 4px; cursor: help; background-color: #036; color: white; padding: 4px; font-weight: bold; font-size: 10px; width: 7px;" title="<?php echo implode(" ",$propertyData["doc_lines"]); ?>">
		        			?
		        		</div><?php	
		        	}
		        ?></td>
    	 	</tr><?php
    	 }
    	 
    	 ?></table><?php
    }

	private function serviceDescGetTypeFormatted($typeName,$isArray,$isCustomType=false) {
    	$typeStr = $typeName;

    	if($isCustomType) {
    		$typeStr = "<a href=\"#".$typeName."\">".$typeStr."</a>";	
    	}
    	
    	if($isArray) {
    		$typeStr = "array(".$typeStr.")";	
    	}
    	
    	return $typeStr;
    }
	
	public function fetchRequestData($serviceDescription)
	{
		// Init request data
		$requestData = array(
			"serviceName" => $_POST["phpladonService"],
			"serviceMethod" => $_POST["phpladonMethod"],
			"parameters" => array()
		);
		
		// Get parameters
		if(isset($serviceDescription["methods"][$requestData["serviceMethod"]])) {
			foreach($serviceDescription["methods"][$requestData["serviceMethod"]]["params"] as $parameterName => $parameterData) {
				
				$requestData["parameters"][$parameterName] = $_POST[$parameterName];
				
			}
		}
		
		return $requestData;
	}
	
	public function ouputResponseData($responseData,$requestData,$serviceDescription)
	{
		//echo "RESPONSE:";
		//echo "<pre>".print_r($responseData,true)."</pre>";
		
?><html>
	<head>
		<title><?php echo $serviceDescription["serviceName"]; ?></title>
		<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.5.1/jquery.min.js"></script>
		<style type="text/css">
			body { background-color: white; margin: 0px; padding: 0px; font-size: 12px; font-family: verdana; }
			div.catName { padding: 10px; background-color: #036; font-size: 20px; color: white; }
			div.catDesc { padding: 20px; padding-bottom: 10px; }
			ul.catService { }
			span.interfaceHead { padding-left: 20px; font-weight: bold; }
			ul.catService li { padding-bottom: 10px; }
			div.serviceDesc { text-align: center; padding: 10px; }
			div.catInterfaces { padding: 10px; padding-left: 30px; padding-top: 0px; }
			div.catGen { text-align: center; font-style:italic; margin-top: 20px; margin-bottom: 20px; }
            		table.method { margin-top: 10px; width: 650px; margin-left: 40px; }
            		td.methodname { background-color: #036; color: white; font-size: 14px; font-weight: bold; padding: 4px; }
            		td.methodcontent { background-color: #eee; padding: 5px; border: 1px solid #036; }
            		td { padding: 3px; }
		</style>
	</head>
	<body>
		<div class=catName><?php echo $serviceDescription["serviceName"]; ?></div>
		<div class=catDesc><?php echo $serviceDescription["description"]; ?></div>
		<div class=catContent>
		
			<table cellspacing="0" cellpadding="0" class="method">
        <tr><td class="methodname"><?PHP echo $requestData["serviceMethod"]; ?></td></tr>
        <tr><td class="methodcontent">
            <form action="" method="post" style="padding: 0px; margin: 0px;">

              <table style="width: 100%; font-size: 12px; ">
              <pre><?PHP
                print_r($responseData);
              ?></pre>
              </table>

            </form>
        </td></tr>
      </table>
		</div>
		<script type="text/javascript">
			function addArrayItem(elm) {
				$(elm).append($(elm).children(':first').html());
			}
		</script>
	</body>	
</html><?PHP
	}
	
	
	public function outputServiceFault($serviceDescription,$code,$message,$details="",$filename="unknown",$lineno=0,$backtrace=null)
	{
		
	}
	
	
}
