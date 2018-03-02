<?php

include_once('../../src/phpLadonService.php');

/**
 * The calculator service can perform basic Mathematical functions
 * as well as simple calculator logic as a memory function and return
 * last result.
 */
class CalculatorService extends phpLadonService
{

	/**
	 * @ladonize
	 * Adds 2 numbers together
	 * @param double $number1 The first number to add
	 * @param double $number2 The second number to add
	 * @return double The result of the add calculation
	 */
	public function add($number1,$number2) {
		return $this->setLastResult($number1+$number2);
	}
	
	/**
	 * @ladonize
	 * Adds all numbers in the array together
	 * @param [double] $numberArray An array of numbers to add
	 * @return double The result of the add calculation
	 */
	public function addArray($numberArray) {
		if(!is_array($numberArray)) return 0;
		$sum = 0;
		foreach($numberArray as $number) $sum += $number;
		return $sum;
	}

	/**
	 * @ladonize
	 * Subtracts a number from another
	 * @param double $number1 The number that is subtracted from
	 * @param double $number2 The number that is subtracted
	 * @return double The result of the subtraction
	 */
	public function subtract($number1,$number2) {
		return $this->setLastResult($number1-$number2);
	}
	
	/**
	 * @ladonize
	 * Multiplies 2 numbers together
	 * @param double $number1 The first number to be multiplied
	 * @param double $number2 The second number to be multiplied
	 * @return double Returns the result of the multiplication
	 */
	public function multiply($number1,$number2) {
		return $this->setLastResult($number1*$number2);
	}

	/**
	 * @ladonize
	 * Divides 2 numbers and returns the result.
	 * @param double $number1 The number to divide
	 * @param double $number2 The number that is divided with
	 * @return double The result of the division
	 */
	public function divide($number1,$number2) {
		return $this->setLastResult($number1/$number2);
	}

	/**
	 * @ladonize
	 * Returns the square root of a specific number
	 * @param double $number Number to get the square root of
	 * @return double The squareroot of the $number variable.
	 */	
	public function sqrt($number) {
		return $this->setLastResult($this->setLastResult(sqrt($number)));
	}

	/**
	 * @ladonize
	 * Raises a number to the power of another number
	 * @param double $base The base number
	 * @param double $exp The exponential
	 * @return double The base raised in the exponential
	 */
	public function power($base,$exp) {
		return $this->setLastResult(pow($base,$exp));
	}

	/**
	 * @ladonize
	 * Saves a number into the memory of the calculater for later retrival
	 * @param double $number The number to save into the calculators memory
	 */
	public function memorySave($number) {
		$_SESSION["calculator"]["memory"] = $number;
	}

	/**
	 * @ladonize
	 * Returns the number previously saved in the memory
	 * @return double The number saved in the calculators memory
	 */
	public function memoryLoad() {
		return floatval($_SESSION["calculator"]["memory"]);
	}

	/**
	 * @ladonize
	 * Clears the saved number from the calculators memory
	 */
	public function memoryReset() {
		unset($_SESSION["calculator"]["memory"]);
	}

	/**
	 * @ladonize
	 * Gets the last result from the calculators memory.
	 * @return double The last result returned by the calculator
	 */ 
	public function lastResult() {
		return floatval($_SESSION["calculator"]["last"]);
	}

	/**
	 * @ladonize
	 * Sets the last result and returns it.
	 * @param double $number The number to save as the calculators last result
	 * @return double Returns the $number var
	 */
	private function setLastResult($number) {
		$_SESSION["calculator"]["last"] = $number;
		return $number;
	}

}
