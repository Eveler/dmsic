<?php

class phpLadonDocComment
{
	
	public static function getDocCommentDescription($DocComment)
	{
		$lines = explode("\n",$DocComment);
		$newLines = array();
		for($i=0;$i<count($lines);$i++) {
			$lineString = trim(str_replace(array("/*","*/","* "),array("","",""),$lines[$i]));
			if($lineString != "" && $lineString != "*" && $lineString[0] != "@") {
				$newLines[] = $lineString;
			}
		}
		return implode("\n",$newLines);
	}


    public static function hasDocCommentTag($docStr,$docTag)
    {
    	return strpos($docStr,$docTag) !== false;
    }

    /**
	 * Extracts fields from the doc string
	 * @param string docStr The documentation string to extract field information from
	 * @param string docTag The name of the doc-tag, ex "@Param"
	 * @param int partCount Number of parts expected after the doc-tag, the parts ware split by spaces and the last part will contain the rest of the string
	 * @param bool returnAll If all lines that matches the docTag should be returned, og only the first one, default is false to only return 1
	 * @param int namedArray Defines if the return array should use string indexes instead of normal indexes. The namedArray defines the part number from 0 to parts - 1 that are used as index. The default is -1 to indicate that normal indexes (integer) should be used
	 */
	public static function getDocCommentTags($docStr,$docTag,$partCount,$returnAll=false,$namedArray=-1) {

		$docParts = self::explodei($docTag,$docStr);
		$tags = array();

		for($i=1;$i<count($docParts);$i++) {

			if(strpos($docParts[$i],"\n") === FALSE) { $tagLine = trim($docParts[$i]); }
			else { $tagLine = trim(strstr($docParts[$i],"\n",true)); }

			$parts = explode(" ",$tagLine);
			$tagParts = array_fill(0,$partCount,"");
			$partIndex = 0;

			while($partIndex < ($partCount-1) && count($parts) > 0) {
				$tagParts[$partIndex] = array_shift($parts);
				$partIndex++;
			}

			if(count($parts) > 0) {
				$tagParts[$partIndex] = implode(" ",$parts);
			}

			if($returnAll == false) {
				return $tagParts;
			}

			if($namedArray == -1) $tags[] = $tagParts;
			else $tags[$tagParts[$namedArray]] = $tagParts;

		}

		return $tags;
	}

	// Case-insensitive explode funciton
	private static function explodei($separator, &$txt)
	{
		if(function_exists("str_ireplace")){
		     $separator_l=strtolower($separator);
		     return explode($separator_l,  str_ireplace($separator, $separator_l, $txt));
   		}
	}
	
	
}
