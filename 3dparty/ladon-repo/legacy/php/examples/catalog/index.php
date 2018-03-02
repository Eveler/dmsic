<?php

// Include ladon files
include '../../src/phpLadonServiceCatalog.php';

// Include service files
include '../classes/CalculatorService.php';
include '../classes/ShopService.php';
include '../classes/UserService.php';

// Declare the service catalog
$serviceCatalog = new phpLadonServiceCatalog("Test Services","These testservices are just som random classes that can be used to explore and test the phpLadon functionality.");

// Add services to the catalog
$serviceCatalog->addService("CalculatorService");
$serviceCatalog->addService("ShopService");
$serviceCatalog->addService("UserService");

// Add interfaces the services can use
$serviceCatalog->addInterface("jsonwsp");
$serviceCatalog->addInterface("soap");
$serviceCatalog->addInterface("simplexml");
$serviceCatalog->addInterface("htmlform");
$serviceCatalog->addInterface("xmlrpc");

// Execute service catalog dispatcher
$serviceCatalog->dispatch();