<?php

include_once('../../src/phpLadonService.php');


/**
 * The user class contains information on a user.
 */
class User {
	
	public $id;
	public $name;
	public $username;
	public $email;
	private $password;

	
	public function getPassword() {
		return $this->password;		
	}
	
	/**
	 * The user class constructer initializes the objects members.
	 */
	public function __construct($id,$name,$username,$email,$password) {
		$this->id = $id;
		$this->name = $name;
		$this->username = $username;
		$this->email = $email;
		$this->password = $password;
	}
	
}

/**
 * Ther UserService is used to fetch information about users and to log in.
 */
class UserService extends phpLadonService 
{
	
	private $userList;
	
	/**
 	 * The userservice constructor initializes the userslist with the avaliable users
	 */
	public function __construct()
	{
		$this->userList = array();
		$this->userList[] = new User(1, "Jens Jensen", "jennermand","jens@jensen.dk","jen1234");
		$this->userList[] = new User(2, "Hans Hansen", "jennermand","jens@jensen.dk","jen1234");
		$this->userList[] = new User(3, "Peter Petersen", "jennermand","jens@jensen.dk","jen1234");
		$this->userList[] = new User(4, "Jakob Jakobsen", "jennermand","jens@jensen.dk","jen1234");
		$this->userList[] = new User(5, "Rasmus Rasmussen", "jennermand","jens@jensen.dk","jen1234");
	}
	
    /**
     * @ladonize
     * Returns the user with the specified user id
     * @param int $userid The user id of the user to return
     * @return User The user with the specified user id
     */
	public function getUser($userid) 
	{
      foreach($this->userList as $user) {
        if($user->id == $userid) {
          return $user;
        }
      }
      return null;
	} 

	/**
	 * @ladonize
	 * Get the user with the specified e-mail adress.
	 * @param string $email The e-mail adress of the user to return	 
	 * @return User Returns the user with the specified e-mail adress or null if no user has that e-mail adress.
	 */
	public function getUserByEmail($email)
	{
      foreach($this->userList as $user) {
        if($user->email == $email) {
          return $user;
        }
      }
      return null;
	}

	/**
	 * @ladonize
	 * Get the user with the specified username
	 * @param string $username The username of the user to return
	 * @return User The user with the specified username or null if the user does not exist 
	 */
	public function getUserByUsername($username)
	{
      foreach($this->userList as $user) {
        if($user->username == $username) {
          return $user;
        }
      }
      return null;
	}

	/**
	 * @ladonize
	 * Get a list of all the users in the service
	 * @return [User] List of all users
	 */
	public function listUsers() 
	{
		return $this->userList;
	}
	
	/**
	 * @ladonize
	 * Perform a search of the users and return users that match the search string
	 * @param string $search The search string to use in the search
	 * @return [User] A list of the users that match the searchstring on their name, e-mail or username
	 */
	public function searchUsers($search)
	{
      $userlist = array();
      foreach($this->userList as $user) {
        if(strpos($user->name,$search) || strpos($user->username,$search) || strpos($user->email,$search)) {
          $userlist[] = $user;
        }
      }
      return $userlist;
	}
	
	/**
	 * @ladonize
	 * Check if credentials are correct
	 * @param string $username The username to use in authorization
	 * @param string $password The password to use in authorization
	 * @return bool Returns true if the credentials are correct and false if not
	 */
	public function credentialsCorrect($username,$password)
	{
      $user = self::getUserByUsername($username);
      if($user == null) return false;
      return ($user->username == $username && $user->getPassword() == $password);
	}

	/**
	 * @ladonize
	 * Checks if the user is currently logged in
	 * @return bool Returns true if the user is logged in.
	 */
    public function isLoggedIn()
    {
      return ($_SESSION["login"]["validated"] == true);
    }

    /**
     * @ladonize
     * Try to login to the service to authorize certain actions
     * @param string $username The username to use in authorization
     * @param string $password The password to use in authorization
     * @return bool Returns true if the login was succesful
     */
	public function login($username,$password)
	{
		if(self::credentialsCorrect($username,$password)) {
          $_SESSION["login"]["validated"] = true;
          $_SESSION["login"]["user"] = self::getUserByUsername($username);
          return true;
        } else {
          return false;
        }
	}
	
	/**
	 * @ladonize
	 * Logs out of the service destroying the current session
	 * @return bool Always returns true
	 */
	public function logout() 
	{
      unset($_SESSION["login"]);
      return true;
	}
	
	/**
	 * @ladonize
	 * Returns the userobject of the logged in user
	 * @return User The userobject of the current user, or null if the user is not logged in
	 */
	public function getLoggedInUser() 
	{
		if(self::isLoggedIn) {
          return $_SESSION["login"]["user"];
        } else return null;
	}
	
}
