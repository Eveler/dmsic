<?php

class phpLadonService
{

	private $className;
	private $modelReflection;
	private $typeArray;
	private $debugging = false;
	
	/**
	 * Get the complete service description array of the phpLadonService
     	 * @return [mixed] Returns the internal service description of the service
     	 */
	public function phpLadonGetServiceDescription() 
	{
        $this->typeArray = array();
		$this->className = get_class ($this);	
		$this->modelReflection = new ReflectionClass($this->className);
		
		$serviceDescription = array();
	   	$serviceDescription["serviceName"] = get_class ($this);
	   	$serviceDescription["serviceUrl"] = "http".($_SERVER["HTTPS"] == "on" ? 's' : '')."://".$_SERVER["SERVER_NAME"].":".$_SERVER["SERVER_PORT"].$_SERVER["REQUEST_URI"];
	   	$serviceDescription["description"] = phpLadonDocComment::getDocCommentDescription($this->modelReflection->getDocComment());
	   	$serviceDescription["methods"] = $this->phpLadonGetMethodDescriptionList();
	   	$serviceDescription["types"] = $this->phpladonFetchTypeDefinitions();
       	return $serviceDescription;
    }
	
	/**
	 * Outputs the servicedescription using the passed interface
	 * @param $interface PHPLadonInterface The interface that is used to deliver 
	 * @return bool Returns true if the service description was succesfully called
	 */
	public function phpLadonOutputServiceDescription($interface) 
	{
		if($interface instanceof PHPLadonInterface) {
			$description = $this->phpLadonGetServiceDescription();
			$interface->outputServiceDescription($description);
			return true;
		}
		else {
			$this->phpLadonDebugOutput("Could not output service description. The interface does not implement the PHPLadonInteface interface.");
			return false;
		}
	}
	
	/**
	 * Processes a service call to the ladon service using the specified interface
	 * @param $interface PHPLadonInterface The interface used to extract request information and return the service response
	 * @return bool Returns true on success and false when the parsing or execution of the request resulted in an error
	 */
	public function phpLadonProcessServiceCall($interface) 
	{
		
		// Get the service description
		$serviceDescription = $this->phpLadonGetServiceDescription();
		
		// Get request dataqwe
		$requestData = $interface->fetchRequestData($serviceDescription);
		
		// Check request data
		if(!$this->phpLadonCheckServiceRequestData($interface,$serviceDescription,$requestData)) {
			return false;
		}
		
		// Call function
		$exeString = '$response = $this->'.$requestData["serviceMethod"].'(';
		foreach($serviceDescription["methods"][$requestData["serviceMethod"]]["params"] as $parameterName => $parameterData) {
			if($parameterData["def_order"] != 1) $exeString .= ',';
			$exeString .= '$requestData["parameters"]["'.$parameterName.'"]'; 
		}
		$exeString .= ');';
		eval($exeString);

		
		// Return response
		$returnData = $this->phpLadonParseReturnValue($response,$serviceDescription["methods"][$requestData["serviceMethod"]]["return"]["type"],$serviceDescription["methods"][$requestData["serviceMethod"]]["return"]["isarray"],$serviceDescription);
		$interface->ouputResponseData($returnData,$requestData,$serviceDescription);
		return true;
	}
	
	/***** RESPONSE HELPERS *****/
	
	/**
	 * Parses the return value from the function, to make it match the method return description. 
	 * Arrays are normalized and custom object types are converted to property arrays
	 */
	private function phpLadonParseReturnValue($data,$type,$isarray,$serviceDescription)
	{
	
		// If is array
		if($isarray) {
			
			$returnArray = array();
		
			// If custom type
			if(isset($serviceDescription["types"][$type])) {
				if(!is_array($data)) {
					$returnArray[] = $this->phpLadonParseCustomReturnType($data,$type,$serviceDescription);
				} else {
					foreach($returnArray as $returnItem) {
						$returnArray[] = $this->phpLadonParseCustomReturnType($returnItem,$type,$serviceDescription);
					}
				}
			}
			
			// Not custom type
			else {
				if(!is_array($data)) {
					$returnArray[] = $data;
				} else {
					foreach($returnArray as $returnItem) {
						$returnArray[] = $returnItem;
					}
				}
			}
			
			return $returnArray;
		}
		
		// Not array
		else {
			// If custom type
			if(isset($serviceDescription["types"][$type])) {
				return $this->phpLadonParseCustomReturnType($data,$type,$serviceDescription);
			}
			
			// Not custom type
			else {
				return $data;
			}
	
		}
	}

	
	/**
	 * Parses an costum type object into an array of its own properties.
	 * @param $data mixed The costum type object to be parsed
	 * @param $type string The name of the costum type, used to check the $data object and find information about what properties to extract from the object.
	 * @param $serviceDescription mixed The servicedescription array, used to lookup information about the custom type, and possibly other types existing in the type
	 * @return mixed Returns an array corresponding to the $data object, where the keys in the array corresponds to the propertynames, and the values corresponds to that propertys value in the object. Values can be yet another parsed custom type, arrays etc.
	 */
	private function phpLadonParseCustomReturnType($data,$type,&$serviceDescription) {

		if(get_class($data) != $type || $data == NULL) return null;
		$propertyArray = array();

		$typeDescription = $serviceDescription["types"][$type];
		foreach($typeDescription["properties"] as $propertyName => $propertyData) {
			$propertyArray[$propertyName] = $this->phpLadonParseReturnValue($data->$propertyName,$propertyData["type"],$propertyData["isarray"],$serviceDescription);
		}
		
		return $propertyArray;
	}
	
	/***** REQUEST HELPERS *****/
	
	/**
	 * Checks that the requestData array returned by the interface contains valid data, that can be used to call a service method
	 * @param $interface PHPLadonInterface The interface used by the service. Used to ouput interface errors
	 * @param $serviceDescription mixed The service description, used to lookup request information to check if they are valid
	 * @param $requestData mixed The requestData array from the interface, containing information about the service request. Contains the data that is checked by this method
	 * @return bool Returns true if the request information is valid, and can be used to call a service method
	 */
	private function phpLadonCheckServiceRequestData(&$interface,&$serviceDescription,&$requestData) 
	{
		// Check servicename
		if($requestData["serviceName"] != $serviceDescription["serviceName"]) {
			$interface->outputServiceFault($serviceDescription,"-1","Servicename not valid.","The servicename \"".$requestData["serviceName"]."\" does not match the called service.","",0,null);
			false;
		}
		
		// Check method name
		if(!isset($serviceDescription["methods"][$requestData["serviceMethod"]])) {
			$interface->outputServiceFault($serviceDescription,"-1","Invalid servicemethod","There is no method by the name \"".$requestData["serviceMethod"]."\" in this service.","",0,null);
			return false;
		}
		
		// Check parameters
		$methodDescription = $serviceDescription["methods"][$requestData["serviceMethod"]];
		foreach($methodDescription["params"] as $parameterName => $parameterData) {

			// Check if parameter is not optional
			if($parameterData["optional"] == false && !isset($requestData["parameters"][$parameterName])) {
				$interface->outputServiceFault($serviceDescription,"-1","Required parameter is not set.","The required parameter \"".$parameterName."\" is not set.","",0,null);
				return false;
			}
			
			// Check if parameter is array
			if(isset($requestData["parameters"][$parameterName]) && $parameterData["isarray"] == true && !is_array($requestData["parameters"][$parameterName])) {
				$interface->outputServiceFault($serviceDescription,"-1","Parameter is not array","The parameter \"".$parameterName."\" is required to be an array, but the request parameter is of type ".gettype($requestData["parameters"][$parameterName]).".","",0,null);
				return false;
			}
			
			// Check if parameter is type
			if(isset($requestData["parameters"][$parameterName]) && isset($serviceDescription["types"][$parameterData["type"]]) && gettype($requestData["parameters"][$parameterName]) != $parameterData["type"]) {
				$interface->outputServiceFault($serviceDescription,"-1","Invalid type in","The parameter \"".$parameterName."\" expected an object of type \"".$parameterData["type"]."\" but \"".gettype($requestData["parameters"][$parameterName])."\" was given in the request.","",0,null);
				return false;
			}
			
			// If optional and not set
			if($parameterData["optional"] == true && !isset($requestData["parameters"][$parameterName])) {
				$requestData["parameters"][$parameterName] = $parameterData["default"];
			}
		}
		
		return true;
		
	}
	
	
	/***** DESCRIPTION HELPERS *****/

	/**
	 * Gets the complete method description array containing descriptions of all methods in the service.
	 * @return mixed Returns an array containing all service method descriptions
	 */
    	private function phpLadonGetMethodDescriptionList() 
    	{
        	$methodDescription = array();
		$methods = $this->modelReflection->getMethods();
		foreach($methods as $method) {
			if($method->class == $this->className && $method->name != "__construct" && phpLadonDocComment::hasDocCommentTag($method->getDocComment(),"@ladonize")) {
              			$methodReflection = $this->modelReflection->getMethod($method->name);
				if($methodReflection->isPublic()) {
					$methodDescription[$method->name] = $this->phpLadonGetMethodDescription($methodReflection);
				}
			}
		}
		return $methodDescription;
    	}

	/**
	 * Creates a method description array and returns it
	 * @param $methodReflection ReflectionFunction The reflectionobject of the method, used to create the description array
	 * @return mixed Returns a method description array based on the $methodReflection object
	 */
	private function phpLadonGetMethodDescription($methodReflection) 
	{
        	$returnVars = phpLadonDocComment::getDocCommentTags($methodReflection->getDocComment(),"@return",2,false);
		if($returnVars == null) $returnVars = array("unknown_type","");
		$this->phpLadonAddTypeDefinitionName($returnVars[0]);
		$methodDescription = array();
		$methodDescription["doc_lines"] = phpLadonDocComment::getDocCommentDescription($methodReflection->getDocComment());
		$methodDescription["params"] = $this->fetchMethodParameterDescription($methodReflection,  phpLadonDocComment::getDocCommentTags($methodReflection->getDocComment(),"@Param",3,true,1));
		$methodDescription["return"] = array("doc_lines" => $returnVars[1], "type" => $this->phpLadonExtractType($returnVars[0]), "isarray" => $this->phpLadonIsTypeArray($returnVars[0]));
		return $methodDescription;
	}

	/**
	 * Creates a description array for a specific methods parameters. Extracts type and doc information from the parameters and returns them in an array
	 * @param $methodReflection ReflectionFunction The reflection object for the method to extract parameter information for.
	 * @param $parameterDocArray mixed An array containing the doc lines for the method, split into parts describing name, type and description.
	 * @return mixed Returns an array containing the parameter descriptions for the method, the keys in the array corresponds to the name of the parameter
	 */
    	private function fetchMethodParameterDescription($methodReflection,$parameterDocArray) 
    	{

		$parameters = $methodReflection->getParameters();
		$parameterDescription = array();

		foreach($parameters as $parameter) {

			$parDoc = $parameterDocArray["$".$parameter->getName()];
			$typeClass = $parameter->getClass();
			if($typeClass != null) $type = $typeClass->name;
			else if($parDoc != null) $type = $parDoc[0];
			else $type = "unknown_type";

			$this->phpLadonAddTypeDefinitionName($type);

			$parameterDescription[$parameter->getName()] = array(
				"def_order" => $parameter->getPosition()+1,
				"doc_lines" => array(($parDoc == null ? "" : $parDoc[2])),
				"type" => $this->phpLadonExtractType($type),
                		"isarray" => $this->phpLadonIsTypeArray($type),
				"optional" => $parameter->isOptional()
			);

			if($parameter->isOptional() == true) {
				$parameterDescription[$parameter->getName()]["default"] = $parameter->getDefaultValue();
			} else {
				$parameterDescription[$parameter->getName()]["default"] = "";
			}
			
		}

		return $parameterDescription;

	}

	/***** TYPE HELPERS *****/

	/**
	 * Adds a class type to the current method description. The type is checked to be a valid class not already in the type list, before it is added.
	 * @param $typeName string The name of the class type to add to the description.
	 * @return null
	 */
    	private function phpLadonAddTypeDefinitionName($typeName) 
    	{
      		$tmpTypeName = $this->phpLadonExtractType($typeName);
      		if(trim($tmpTypeName) == "" || trim($tmpTypeName) == "unknown_type" || in_array($tmpTypeName,$this->typeArray) || !class_exists($tmpTypeName)) return;
      		$this->typeArray[] = $tmpTypeName;
    	}

	/**
	 * Generates the custom class type definition array for the service. It takes all valid types and generates the description array for the types
	 * @return mixed The type description array
	 */
    	private function phpladonFetchTypeDefinitions() 
    	{
		$classDefinitions = array();
        	for($i=0; $i < count($this->typeArray); $i++) {
			$classDefinitions[$this->typeArray[$i]] = $this->getTypeDescription($this->typeArray[$i]);
		}
		return $classDefinitions;
	}

	/**
	 * Fetches the type description array for a specific custom type
	 * @param $typeName mixed The type description array
	 */
    	private function getTypeDescription($typeName) 
    	{
      
      		$classReclection = new ReflectionClass($typeName);
      		$propertyList = $classReclection->getProperties();
      		$typeDescription = array("properties" => array(), "dependencies" => array());

      		foreach($propertyList as $property) {
        		if($property->isPublic()) {

          			// Extract property info from
          			$typeCommentParts = phpLadonDocComment::getDocCommentTags($property->getDocComment(), "@var", 2);
          			if($typeCommentParts[0] == "") $typeCommentParts[0] = "unknown";
          			if($typeCommentParts[1] == "") $typeCommentParts[1] = phpLadonDocComment::getDocCommentDescription($property->getDocComment());

          			// Add to type array
          			$this->phpLadonAddTypeDefinitionName($typeCommentParts[0]);

          			// Check if in the type array
          			if(in_array($typeCommentParts[0], $this->typeArray) && !in_array($typeCommentParts[0], $typeDescription["dependencies"])) {
            				$typeDescription["dependencies"][] = $typeCommentParts[0];
          			}

          			// Make type description
          			$typeDescription["properties"][$property->getName()] = array(
            				"type" => $this->phpLadonExtractType($typeCommentParts[0]),
            				"isarray" => $this->phpLadonIsTypeArray($typeCommentParts[0]),
            				"doc_lines" => $typeCommentParts[1]
          			);
          	
			}
      		}

      		return $typeDescription;
    	}

	/**
	 * Extracts the typename from a string by removing array indicators
	 * @param @type string from documentation etc. that can contain array indicators
	 * @return string The actual type name without array indicators
	 */	
    	private function phpLadonExtractType($type) 
    	{
      		return str_replace(array("[","]"),array("",""),$type);
    	}

	/**
	 * Returns is a type is an array by checking for array indicators
	 * @param $type string The name of the type
	 * @return bool Returns true if the type has array indicators
	 */
    	private function phpLadonIsTypeArray($type) 
    	{
      		$tmpType = trim($type);
      		return ($tmpType[0] == "[" && $tmpType[strlen($tmpType)-1] == "]");
    	}


	/***** OTHER HELPERS *****/

	/**
 	 * Outputs debug information for phpLadon, if debugging is enabled
 	 * This can be used to track errors or problems in a service.
	 */
	private function phpLadonDebugOutput($string) 
	{
		echo "DEBUG MESSAGE: ".$string;
	}

}
