<?php

interface phpLadonInterface
{
	
	public function outputServiceDescription($serviceDescription);
	public function fetchRequestData($serviceDescription);
	public function ouputResponseData($responseData,$requestData,$serviceDescription);
	public function outputServiceFault($serviceDescription,$code,$message,$details="",$filename="unknown",$lineno=0,$backtrace=null);
	
}