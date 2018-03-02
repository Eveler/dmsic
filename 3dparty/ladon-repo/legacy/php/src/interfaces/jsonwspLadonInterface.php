<?php

class jsonwspLadonInterface implements phpLadonInterface
{

	public function outputServiceDescription($serviceDescription)
	{
		//echo $this->indent(json_encode($serviceDescription));
		
		$descArray = array(
			"type" => "jsonwsp/description",
			"version" => "1.0",
			"servicename" => $serviceDescription["serviceName"],
			"url" => $serviceDescription["serviceUrl"],
			"types" => $this->getDescriptionTypes($serviceDescription),
			"methods" => $this->getDescriptionMethods($serviceDescription)
		);
		
		echo $this->indent(json_encode($descArray));
		
	}
	

	private function getDescriptionTypes($serviceDescription) {
		$typeArray = array();
		
		foreach($serviceDescription["types"] as $typeName => $typeData) {
			$typeElement = array();
			foreach($typeData["properties"] as $propertyName => $propertyData) {
				$typeElement[$propertyName] = $this->getDescriptionType($propertyData["type"], $propertyData["isarray"]);
			}
			$typeArray[$typeName] = $typeElement;
		}
		
		return $typeArray;
	}
	
	private function getDescriptionMethods($serviceDescription) {
		$methodArray = array();
		
		foreach ($serviceDescription["methods"] as $methodName => $methodData) {
			
			$methodElement = array(
				"doc_lines" => array($methodData["doc_lines"]), 
				"params" => array(), 
				"return" => array("doc_lines" => $methodData["return"]["doc_lines"],"type" => $this->getDescriptionType($methodData["return"]["type"], $methodData["return"]["isarray"]))
			);
			
			foreach($methodData["params"] as $propertyName => $propertyData) {
				$methodElement["params"][$propertyName] = array(
					"def_order" => $propertyData["def_order"],
					"doc_lines" => $propertyData["doc_lines"],
					"type" => $this->getDescriptionType($propertyData["type"], $propertyData["isarray"]),
					"optional" => $propertyData["optional"]
				);
			}
			
			$methodArray[$methodName] = $methodElement;
		}
		
		return $methodArray;
	}
	
	
	private function getDescriptionType($type,$isArray) {
		if($isArray) {
			return array($type);
		} else {
			return $type;
		}
	}
	

	public function outputServiceFault($serviceDescription,$code,$message,$details="",$filename="unknown",$lineno=0,$backtrace=null)
	{
		$faultData = array(
			"type" => "jsonwsp/fault",
			"version" => "1.0",
			"fault" => array(
				"code" => "server",
				"string" => $message
			)
		);
		
		if($details != "") $faultData["fault"]["details"] = $details;
		if($filename != "unknown") $faultData["fault"]["filename"] = $filename;
		if($lineno != 0) $faultData["fault"]["lineno"] = $lineno;
	}
		
	public function fetchRequestData($serviceDescription)
	{
		$requestInput = file_get_contents('php://input');
		$requestJSON = json_decode($requestInput,true);
		
		if($requestJSON == NULL || !is_array($requestJSON)) {
			$this->outputServiceFault($serviceDescription,"1","Could not parse request JSON.","");
		}
		
		$requestData = array(
			"serviceName" => $serviceDescription["serviceName"],
			"serviceMethod" => $requestJSON["methodname"],
			"parameters" => array()
		);
		
		if(is_array($requestJSON["args"])) {
			foreach($requestJSON["args"] as $argName => $argValue) {
				$requestData["parameters"][$argName] = $this->getArgData($argValue);		
			}
		}
		
		return $requestData;
	}
	
	private function getArgData($data) 
	{
		if(is_array($data)) {
			$retArray = array();
			foreach($data as $name => $value) {
				$retArray[$name] = $this->getArgData($value);
			}
			return $retArray;
		} else {
			return utf8_decode($data);
		}
	}
	
	public function ouputResponseData($responseData,$requestData,$serviceDescription)
	{
		$responseData = array(
			"type" => "jsonwsp/response",
			"version" => "1.0",
			"servicename" => $requestData["serviceName"],
			"methodname" => $requestData["serviceMethod"],
			"result" => $this->getResponseData($responseData) 
		);
		
		echo json_encode($responseData);
	}
	
	private function getResponseData($data) 
	{
		if(is_array($data)) {
			$retArray = array();
			foreach($data as $name => $value) {
				$retArray[$name] = $this->getResponseData($value);
			}
			return $retArray;
		} else {
			return utf8_encode($data);
		}
	}
	
	
	/**
	 * Indents a flat JSON string to make it more human-readable.
	 *
	 * @param string $json The original JSON string to process.
	 *
	 * @return string Indented version of the original JSON string.
	 */
	private function indent($json) {
	
	    $result      = '';
	    $pos         = 0;
	    $strLen      = strlen($json);
	    $indentStr   = '  ';
	    $newLine     = "\n";
	    $prevChar    = '';
	    $outOfQuotes = true;
	
	    for ($i=0; $i<=$strLen; $i++) {
	
	        // Grab the next character in the string.
	        $char = substr($json, $i, 1);
	
	        // Are we inside a quoted string?
	        if ($char == '"' && $prevChar != '\\') {
	            $outOfQuotes = !$outOfQuotes;
	        
	        // If this character is the end of an element, 
	        // output a new line and indent the next line.
	        } else if(($char == '}' || $char == ']') && $outOfQuotes) {
	            $result .= $newLine;
	            $pos --;
	            for ($j=0; $j<$pos; $j++) {
	                $result .= $indentStr;
	            }
	        }
	        
	        // Add the character to the result string.
	        $result .= $char;
	
	        // If the last character was the beginning of an element, 
	        // output a new line and indent the next line.
	        if (($char == ',' || $char == '{' || $char == '[') && $outOfQuotes) {
	            $result .= $newLine;
	            if ($char == '{' || $char == '[') {
	                $pos ++;
	            }
	            
	            for ($j = 0; $j < $pos; $j++) {
	                $result .= $indentStr;
	            }
	        }
	        
	        $prevChar = $char;
	    }
	
	    return $result;
	}
}
