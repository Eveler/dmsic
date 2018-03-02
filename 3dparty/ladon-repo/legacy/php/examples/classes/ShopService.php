<?php

include_once('../../src/phpLadonService.php');

/**
 * The cart item represents an item in the cart. 
 * It is basically an item, but with some extra data
 */
class CartItem {

    /**
     *
     * @var Item
     */
	public $item;
	public $quantity;
	public $totalPrice;
	
	public function __construct(Item $item,$quantity) {
		$this->item = $item;
		$this->quantity = $quantity;
		$this->totalPrice = $quantity*$item->price;
	}
	
	public function updateQuantity($quantity) {
		$this->quantity = $quantity;
		$this->totalPrice = $quantity*$this->item->price;
	}
}

/**
 * The Item class represents an item in the shop that can be bought.
 */
class Item {

    /**
     *
     * @var int The product id
     */
	public $productid;
	public $name;
	public $description;
	public $price;
	
	public function __construct($id,$name,$description,$price) {
		$this->productid = $id;
		$this->name = $name;
		$this->description = $description;
		$this->price = $price;
	}
	
}




/**
 * The shop service class holds basic shop functionality
 * It can list product items and these items can be added 
 * to the costumers cart and can later be manipulated.
 */
class ShopService extends phpLadonService
{
	
	private $itemList;
	
	/**
	 * The constructer, initializes the item list with all the items in the shop.
	 */
	public function __construct() {
		
		$this->itemList = array();
		
		// Create items
		$this->itemList[] = new Item(1,"Toy train","A small toy train great is your child loves playing with trains!",299);
		$this->itemList[] = new Item(2,"Teddy bear","A fuzzy teddy bear that brings comfort to every childs sleep!",149);
		$this->itemList[] = new Item(3,"Shotgun","A fake pump action shotgun, great for intimidating random people knocking on your door.",450);
		$this->itemList[] = new Item(4,"Ak-47","An actual Ak-47, used by the resistance in Afghanistan in 2008. This is not a toy!",2999);
		$this->itemList[] = new Item(5,"Toxic waste","Lovely toxic waste imported from Russia. If you want an extra arm growing out of your back, this is the waste for you.",999);
		$this->itemList[] = new Item(6,"Puppy","Lovely Cavalier King Charles spaniel puppy that melts the hearts of every dog hating person out there.",8000);
		$this->itemList[] = new Item(7,"Poncho","C'mon everyone loves a poncho",319);
		$this->itemList[] = new Item(8,"Flowers","Very nice flowers, goes nice with the toxic waste!",49);
		$this->itemList[] = new Item(9,"Used car","Wan't to buy and old wreck? This is the car for you. It can't start but makes a very pretty wall decoration.",2000);
	
	}
	
	/**
	 * @ladoninze
	 * Lists all items in the shop
	 * @return [Item] A list with all items in the shop
	 */
	public function listItems() 
	{
		return $this->itemList;	
	}
	
	/**
	 * @ladonize
	 * Gets an item with a specific product id
	 * @param int $productid The product id of the product to return
	 * @return Item The item matching the product id, or null if it did not exist.
	 */
	public function getItem($productid) 
	{
		foreach($this->itemList as $item) {
			if($item->productid == $productid) {
				return $item;
			}
		}
		return null;
	}
	
	/**
	 * @ladonize
	 * Gets a list of items corresponding to the ids given to the method
	 * @param [int] $productidList The list of product ids of the products to return
	 * @return [Item] The items matching the product ids
	 */
	public function getItems($productidList) 
	{
		$return = array();
		foreach($this->itemList as $item) {
			if(in_array($item->productid, $productidList)) {
				$return[] = $item;
			}
		}
		return $return;
	}
	
	/**
	 * @ladonize
	 * Search all items for the occurance of a specific string and return all items that match the string
	 * @param string $string The search string that is matched with the items
	 * @return [Item] A list of items that matches the search string
	 */
	public function searchItems($string) 
	{
		$searchList = array();
		foreach($this->itemList as $item) {
			if(strpos($item->name,$string) || strpos($item->description,$string)) {
				$searchList[] = $item;
			}
		}
		return $searchList;
	}
	
	/**
	 * @ladonize
	 * Returns all items currently in the costumers cart
	 * @return [CartItem] An array of all the cart items currently in the cart
	 */
	public function getCartItems() {
		if(!isset($_SESSION["cart"])) {
			$_SESSION["cart"] = array();
		}
		return $_SESSION["cart"];
	}
	
	/**
	 * @ladonize
	 * Gets an cart item with a specific product id
	 * @param int $productid The product id of the cart items item
	 * @return CartItem Returns the cartitem with the matching product id or null if not in the cart.
	 */
	public function getCartItem($productid) {
		if(!isset($_SESSION["cart"])) {
			$_SESSION["cart"] = array();
		}
		
		foreach ($_SESSION["cart"] as $cartItem) {
			if($cartItem->item->productid == $productid) {
				return $cartItem;
			}
		}
		return null;
	}
	
	/**
	 * @ladonize
	 * Adds an item to the costumers cart
	 * @param Item $item The item to add to the cart
	 * @param int $quantity The number of items the costumer wants to buy
	 * @return bool Returns true if the item was added to the cart, returns false if the Item was already in the cart or the quantity was not a positive number.
	 */
	public function addItemToCart(Item $item, $quantity = 1) 
	{ 
		if($this->getCartItem($item->productid) != null) {
			return false;
		}
		
		if($quantity <= 0) {
			return false;
		} 
		
		$_SESSION["cart"][] = new CartItem($item, $quantity);
		return true;
	}
	
	/**
	 * @ladonize
	 * Removes a specific CartItem from the cart
	 * @param CartItem $cartItem The cart item to remove from the cart
	 * @return Returns true if the cart item was succesfully removed from the cart
	 */
	public function removeItemFromCart(CartItem $cartItem)
	{
		if(count($_SESSION["cart"]) == 0) return false;
		foreach ($_SESSION["cart"] as $index => $cItem) {
			if($cItem->item->productid == $cartItem->item->productid) {
				unset($_SESSION["cart"][$index]);
				return true;
			}
		}
		return false;
	}
	
	/**
	 * @ladonize
	 * Updates a cart items quantity
	 * @param CartItem $cartItem The cart item to update
	 * @param int $quantity The new quantity of the cart item
	 * @return bool Returns true if the cart item was updated. Returns false if the cart item was not found or the quantity was a non-positive number.
	 */
	public function updateItemQuantity(CartItem $cartItem, $quantity) {
		if(count($_SESSION["cart"]) == 0) return false;
		if($quantity <= 0) return false;
		foreach ($_SESSION["cart"] as $index => $cItem) {
			if($cItem->item->productid == $cartItem->item->productid) {
				$_SESSION["cart"][$index]->updateQuantity($quantity);
				return true;
			}
		}
		return false;
	}
	
	/**
	 * @ladonize
	 * Gets the total price of all items in the cart with their current quantities
	 * @return double The total price of the items in the cart.
	 */
	public function getTotalPrice() 
	{
		$price = 0;
		if(count($_SESSION["cart"]) == 0) return $price;
		foreach ($_SESSION["cart"] as $index => $cItem) {
			$price += $cItem->item->price;
		}
		return $price;
	}
	
	/**
	 * @ladonzie
	 * Resets the cart
	 */
	public function resetCart() 
	{
		$_SESSION["cart"] = array();
	}
	
	
}
