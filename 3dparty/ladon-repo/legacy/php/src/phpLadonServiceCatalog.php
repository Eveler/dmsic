<?php

require_once 'phpLadonInterface.php';
require_once 'phpLadonService.php';
require_once 'phpLadonDocComment.php';

class phpLadonServiceCatalog {
	
	private $m_catalogName;
	private $m_catalogDescription;
	private $m_serviceList;
	private $m_interfaceList;
	private $m_pathParts;
	private $m_overviewEnabled = false;
	private $m_descriptionEnabled = false;
	private $m_debugging = false;
	/**
	 * 
	 * phpLadonServiceCatalog constructor, creates a new instance of the catalog with
	 * a specified name and description, to show on the frontpage of the catalog.
	 * @param string $catalogName Name of the service catalog
	 * @param string $catalogDescription A brief description of the service catalog
	 */
	public function __construct($catalogName="",$catalogDescription="",$htmlOverviewEnabled=true,$htmlDescriptionEnabled=true)
	{
		$this->m_catalogName = $catalogName;
		$this->m_catalogDescription = $catalogDescription;
		$this->m_overviewEnabled = $htmlOverviewEnabled;
		$this->m_descriptionEnabled = $htmlDescriptionEnabled;
		$this->m_serviceList = array();
		$this->m_interfaceList = array();
		
		// ENABLE DEBUGGING
		$this->m_debugging = true;
	}
	
	/**
	 * 
	 * Adds a service to the service catalog by its class name.
	 * The class needs to be included before the call to this method, or it will not be loaded.
	 * When a class is added it checks if it inherits from the phpLadonService class, or it will not be added.
	 * @param string $serviceClassName The class name of the service to include in the catalog
	 */
	public function addService($serviceClassName)
	{
		// Check if service is already loaded
		if(isset($this->m_serviceList[$serviceClassName])) {
			if($this->m_debugging) {
				echo "Can't add service: ".$serviceClassName." because it is already loaded!";
			}
			return false;
		}
		
		// Check class
		if(!class_exists($serviceClassName)) {
			if($this->m_debugging) {
				echo "Can't add service: ".$serviceClassName.". Class name does not exist!";
			}
			return false;
		}
		
		// Check reflection
		$classReflection = new ReflectionClass($serviceClassName);
		$parentClassReflection = $classReflection->getParentClass(); 
		
		// Check parent class
		if($parentClassReflection === false || $parentClassReflection->getName() != "phpLadonService") {
			if($this->m_debugging) {
				echo "Can't add service: ".$serviceClassName.". The class does not extend the phpLadonService class!";
			}
			return false;
		}
		
		// Add service
		$this->m_serviceList[$serviceClassName] = $classReflection; 
		return true;
	}
	
	/**
	 * 
	 * Adds an interface to the service catalog that can interact with the phpLadonService class to input/output data
	 * New interfaces can be added to the ladon/interfaces folder and must extend the phpLadonInterface class
	 * The name of the interfaces must match a class in the interfaces folder like xxxxLadonInterface, where xxxx is the name of the 
	 * @param string $interfaceName Name of the interface that has a matcing class
	 */
	public function addInterface($interfaceName)
	{
		$interfaceClassName = $interfaceName."LadonInterface";
		
		if(isset($this->m_interfaceList[$interfaceName])) {
			if($this->m_debugging) {
				echo "Can't add interface: ".$interfaceName." because it is already loaded!";
			}
			return false;
		}
	
		// Check if the class has been included
		$includedFiles = get_included_files();
		if(!in_array($interfaceClassName,$includedFiles)) {
			$includeResult = @include('interfaces/'.$interfaceClassName.".php");
			if($includeResult === false) {
				if($this->m_debugging) {
					echo "Can't add interface: ".$interfaceName.". Class file is missing and can't be included!";
				}
				return false;
			}
		}
		
		// Check class
		if(!class_exists($interfaceClassName)) {
			if($this->m_debugging) {
				echo "Can't add interface: ".$interfaceName.". The interface class does not exist!";
			}
			return false;
		}
		
		// Check reflection
		$classReflection = new ReflectionClass($interfaceClassName);
		$classInterfaces = $classReflection->getInterfaceNames();
		if(!in_array("phpLadonInterface", $classInterfaces)) {
			if($this->m_debugging) {
				echo "Can't add interface: ".$interfaceName.". The class does not implement the phpLadonInterface.";
			}
			return false;
		}
		
		// Add interface
		$this->m_interfaceList[$interfaceName] = $interfaceClassName;
		return true;
	}
	
	/**
	 * 
	 * Executes the catalog dispatcher that automatically detects the service / description / overview to output
	 */
	public function dispatch() {
		
		// Get path info and remove front slash
		$pathInfo = $_SERVER["PATH_INFO"];
		if($pathInfo[0] == "/") $pathInfo = substr($pathInfo,1);
		$this->m_pathParts = explode("/",$pathInfo);
	
		if(strtoupper($_SERVER["REQUEST_METHOD"]) == "POST") {
			$this->processPOSTRequest();
		} else {
			$this->processGETRequest();
		}
	}
	
	public function setDebugging($enabled) {
		$this->m_debugging = $enabled;
	}
	
	private function processGETRequest() {

		if(count($this->m_pathParts) > 0 && trim($this->m_pathParts[0]) != "") {
			
			// Check service
			$serviceName = $this->m_pathParts[0];
			if(isset($this->m_serviceList[$serviceName])) {
				
				// Create service
				eval('$service = new '.$serviceName.'();');
				
				if(count($this->m_pathParts) > 1 && trim($this->m_pathParts[1]) != "") {
					
					$interfaceName = strtolower(trim($this->m_pathParts[1]));
				
					if($interfaceName == "desc" && $this->m_descriptionEnabled == true) {
						$this->printServiceDescription($service->phpLadonGetServiceDescription());
					} else if(isset($this->m_interfaceList[$interfaceName])) {
						eval('$interface = new '.$this->m_interfaceList[$interfaceName].'();');
						
						$service->phpLadonOutputServiceDescription($interface);
					} else {
						$this->showCatalogError("The service '".$serviceName."' does not expose the interface '".$interfaceName."'.");
					}
					
				} else {
					
					if($this->m_overviewEnabled == true) {
						$this->printInterfaceSelection($service->phpLadonGetServiceDescription());
					} else {
						header($_SERVER["SERVER_PROTOCOL"]." 404 Not Found"); 
					}
				}
			} else {
				$this->showCatalogError("No service with the name '".$serviceName."' exists in this catalog.");
			}
		} else {
			if($this->m_overviewEnabled == true) {
				$this->printServiceCatalog();	
			} else {
				header($_SERVER["SERVER_PROTOCOL"]." 404 Not Found"); 
			}
		}
	
	}
	
	private function processPOSTRequest() 
	{
	
		if(count($this->m_pathParts) > 0 && trim($this->m_pathParts[0]) != "") {
			
			// Check service
			$serviceName = $this->m_pathParts[0];
			if(isset($this->m_serviceList[$serviceName])) {
				
				// Create service
				eval('$service = new '.$serviceName.'();');
				
				if(count($this->m_pathParts) > 1 && trim($this->m_pathParts[1]) != "") {
					
					$interfaceName = strtolower(trim($this->m_pathParts[1]));
				
					if(isset($this->m_interfaceList[$interfaceName])) {
						eval('$interface = new '.$this->m_interfaceList[$interfaceName].'();');
						$service->phpLadonProcessServiceCall($interface);
					} else {
						header($_SERVER["SERVER_PROTOCOL"]." 404 Not Found"); 
					}
					
				} else {
					header($_SERVER["SERVER_PROTOCOL"]." 404 Not Found"); 
				}
			} else {
				header($_SERVER["SERVER_PROTOCOL"]." 404 Not Found"); 
			}
		} else {
			header($_SERVER["SERVER_PROTOCOL"]." 404 Not Found"); 
		}

	}
	

	private function printInterfaceSelection($serviceDescription) {
?><html>
	<head>
		<title><?php echo $serviceDescription["serviceName"]; ?></title>
		<style type="text/css">
			body { background-color: white; margin: 0px; padding: 0px; font-size: 12px; font-family: verdana; }
			div.catName { padding: 10px; background-color: #036; font-size: 20px; color: white; }
			div.catDesc { padding: 20px; padding-bottom: 10px; }
			ul.catService { }
			span.interfaceHead { padding-left: 20px; font-weight: bold; }
			ul.catService li { padding-bottom: 10px; }
			div.serviceDesc { text-align: center; padding: 10px; }
			div.catInterfaces { padding: 10px; padding-left: 30px; padding-top: 0px; }
			div.catGen { text-align: center; font-style:italic; margin-top: 20px; }
		</style>
	</head>
	<body>
		<div class=catName><?php echo $serviceDescription["serviceName"]; ?></div>
		<div class=catDesc><?php echo $serviceDescription["description"]; ?></div>
		<div class=catContent>
		
			<span class="interfaceHead">Select service interface:</span>
			<ul class=catService>
			<?php 
				foreach ($this->m_interfaceList as $interfaceName => $interfaceClass) {
					?><li><a href="<?php echo $serviceDescription["serviceName"]; ?>/<?php echo $interfaceName; ?>/"><?php echo $interfaceName; ?></a></li><?php
				}
			?>
			</ul>
		
			<div class=serviceDesc>
				<a href="<?php echo $serviceDescription["serviceName"]; ?>/desc/">View service complete service description</a>
			</div>
		</div>
		
		
		<div class=catGen>Service catalog generated by phpLadon</div>
	</body>	
</html><?PHP		
	}
	
    private function printServiceDescription($serviceDescription) {
?><html>
	<head>
		<title><?php echo $serviceDescription["serviceName"]; ?></title>
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
					?><li><span style="font-size: 14px; font-weight: bold;"><?php 
					
						// Method name
						echo $methodName."("; 
							if(count($methodData["params"]) > 0) {
								$count = 0; $optionalCount = 0;
								foreach($methodData["params"] as $paramName => $paramData) {
									
									if($paramData["optional"] == true) {
										echo " [";
										$optionalCount++;
									}
									
									if($count > 0) echo ", ";
									echo $this->serviceDescGetTypeFormatted($paramData["type"],$methodData["return"]["isarray"],isset($serviceDescription["types"][$paramData["type"]]))." ".$paramName;
									
									if($paramData["default"] != "") {
										echo " = ".$paramData["default"];
									}
									
									$count++;
								}
								
								for($i=0;$i<$optionalCount;$i++) echo "]";
							}
						echo ")</span><br><i>".$methodData["doc_lines"]."</i>";
						
						// Parameters
						if(count($methodData["params"]) > 0) {
							echo "<br><u>Parameters:</u><ul>";
							foreach($methodData["params"] as $paramName => $paramData) {
								echo "<li><b>".$paramName."</b>: <u>".$this->serviceDescGetTypeFormatted($paramData["type"],$methodData["return"]["isarray"],isset($serviceDescription["types"][$paramData["type"]]))."</u>";
								if(count($paramData["doc_lines"]) > 0) echo "<br><i>".implode("<br>",$paramData["doc_lines"])."</i></li>";
							}
							echo "</ul>";
						}
						
						// Returns
						echo "<br><u>Returns</u> ".$this->serviceDescGetTypeFormatted($methodData["return"]["type"],$methodData["return"]["isarray"],isset($serviceDescription["types"][$methodData["return"]["type"]])).": <i>".$methodData["return"]["doc_lines"]."</i>";
				
					?></li><?php
				}
			?>
			</ul>
			
			<span class="interfaceHead">Custom types:</span>
			<ul class=catService>
			<?php 
				foreach ($serviceDescription["types"] as $typeName => $typeData) {
					echo "<li><span style=\"font-size: 14px; font-weight: bold;\"><a name=\"".$typeName."\">".$typeName."</a></span><ul>";

					foreach($typeData["properties"] as $propertyName => $propertyData) {
						echo "<li><b>".$propertyName."</b>: <u>".$this->serviceDescGetTypeFormatted($propertyData["type"],$propertyData["isarray"],isset($serviceDescription["types"][$propertyData["type"]]))."</u>";
						if(trim($propertyData["doc_lines"] != "")) echo "<br><i>".$propertyData["doc_lines"]."</i>";
						echo "</li>";
					}
					
					echo "</ul></li>";
				}
			?>
			</ul>
		</div>
		<div class=catGen>Service catalog generated by phpLadon</div>
	</body>	
</html><?PHP
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

	private function printServiceCatalog() {
?><html>
	<head>
		<title><?php echo $this->m_catalogName; ?> catalog overview</title>
		<style type="text/css">
			body { background-color: white; margin: 0px; padding: 0px; font-size: 12px; font-family: verdana; }
			div.catName { padding: 10px; background-color: #036; font-size: 20px; color: white; }
			div.catDesc { padding: 20px; padding-bottom: 10px; }
			ul.catService { }
			ul.catService li { padding-bottom: 10px; }
			div.catInterfaces { padding: 10px; padding-left: 30px; padding-top: 0px; }
			div.catGen { text-align: center; font-style:italic; margin-top: 20px;  margin-bottom: 20px; }
		</style>
	</head>
	<body>
		<div class=catName><?php echo $this->m_catalogName; ?></div>
		<div class=catDesc><?php echo $this->m_catalogDescription; ?></div>
		<div class=catContent>
			<ul class=catService>
			<?php foreach($this->m_serviceList as $class => $service) { ?>
				<li>
					<b><a href="<?php echo $class; ?>"><?php echo $class; ?></a></b><br>
					<?php 
						echo str_replace("\n","<br>",phpLadonDocComment::getDocCommentDescription($service->getDocComment()));
					?>
				</li>
			<?php } ?>
			</ul>
		</div>
		
		<div class=catInterfaces>
			Exposed interfaces in this catalog: 
			<b><?php 
				$interfaceString = "";
				foreach ($this->m_interfaceList as $interfaceName => $interfaceClass) {
					if($interfaceString != "") $interfaceString .= ", ";
					$interfaceString .= $interfaceName;
				}
				echo $interfaceString;
			?></b>
		</div>
		<div class=catGen>Service catalog generated by phpLadon</div>
	</body>	
</html><?php
	}
	
	private function showCatalogError($errorString) {
?><html>
	<head>
		<title><?php echo $this->m_catalogName; ?> catalog error</title>
		<style type="text/css">
			body { background-color: white; margin: 0px; padding: 0px; font-size: 12px; font-family: verdana; }
			div.catName { padding: 10px; background-color: #036; font-size: 20px; color: white; }
			div.errorContent { text-align: center; color: red; padding: 20px; font-size: 14px; }
			div.backLink { text-align: center; padding: 5px; }
			ul.catService li { padding-bottom: 10px; }
			div.catInterfaces { padding: 10px; padding-left: 30px; padding-top: 0px; }
			div.catGen { text-align: center; font-style:italic; margin-top: 20px;  margin-bottom: 20px;  }
		</style>
	</head>
	<body>
		<div class=catName><?php echo $this->m_catalogName; ?></div>

		<div class=errorContent>
			<b>Catalog error:</b><br>
			<?php echo $errorString; ?>
		</div>
		<div class=backLink><a href="<?php echo $_SERVER["SCRIPT_NAME"]; ?>">To catalog index</a></div>
		<div class=catGen>Service catalog generated by phpLadon</div>
	</body>	
</html><?php
	}
}

?>