<?php
if (isset($_POST['sourceLang'])) {
##	list($sourceLang, $targetLang) = split("-", $_POST["langs"], 2);
	$url = "http://quest.ms.mff.cuni.cz:8888/khresmoi";
	$curl = curl_init($url);
	$q = array(
		"action" => "translate",
		"sourceLang" => $_POST["sourceLang"],
		"targetLang" => $_POST["targetLang"],
		"text" => $_POST["text"],
		"alignmentInfo" => (isset($_POST["alignmentInfo"]) ? "true":"false")
	);
	$opts = array(
		CURLOPT_USERPWD => "test:test123",
		CURLOPT_HTTPAUTH => CURLAUTH_BASIC,
		CURLOPT_RETURNTRANSFER => true,
		CURLOPT_POST => true,
		CURLOPT_HTTPHEADER => array('Content-Type: application/json; charset=utf-8'),
		CURLOPT_POSTFIELDS => json_encode($q)
	);
	curl_setopt_array($curl, $opts);
	$response = curl_exec($curl);
	curl_close($curl);
} else {
	$_POST["targetLang"] = "de";
}
?>

<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>Khresmoi: CUNI Machine Translation Services</title>
  <meta name="author" content="Jakub Bystroň" />
  <meta name="robots" content="all" />
  <meta http-equiv="cache-control" content="no-cache" />
  <meta charset="UTF-8" />
  <style>
    body {
	    background: #B0C4DE;
	    font-family: Verdana, Geneva, sans-serif;
	    font-size: 14px;
    }
    big {
	    font-family: Courier New, monospace;
    }
    h3 {
	    font-weight: normal;
	    font-size: 15px;
    }
    label {
	    float: left;
	    min-width: 240px;
    }
    #response {
	    font-weight: bold;
	    font-size: 15px;
    }
  </style>
</head>
<body>
  <h1>Khresmoi: CUNI Machine Translation Services</h1>

  <pre>Cluster URL (REST API): http://quest.ms.mff.cuni.cz:8888/khresmoi</pre>
  <form action="" method="post">
  <fieldset>
    <label>action</label>
    <span>translate</span>
    <br/>

    <label>userId</label>
    <input type="text" maxLength="32" disabled="disabled" />
    <br />

    <label for="sourceLang">sourceLang</label>
    <select name="sourceLang" id="sourceLang">
      <option value="en" <? echo $_POST["sourceLang"]=="en" ? "selected":"" ?>>en</option>
      <option value="de" <? echo $_POST["sourceLang"]=="de" ? "selected":"" ?>>de</option>
      <option value="fr" <? echo $_POST["sourceLang"]=="fr" ? "selected":"" ?>>fr</option>
      <option value="cs" <? echo $_POST["sourceLang"]=="cs" ? "selected":"" ?>>cs</option>
    </select>
    <br />

    <label>targetLang</label>
    <select name="targetLang">
      <option value="en" <? echo $_POST["targetLang"]=="en" ? "selected":"" ?>>en</option>
      <option value="de" <? echo $_POST["targetLang"]=="de" ? "selected":"" ?>>de</option>
      <option value="fr" <? echo $_POST["targetLang"]=="fr" ? "selected":"" ?>>fr</option>
      <option value="cs" <? echo $_POST["targetLang"]=="cs" ? "selected":"" ?>>cs</option>
    </select>
    <br />

    <label>text</label>
    <textarea rows="4" cols="60" name="text" style="font-size:14px;" maxLength="512"><? echo
    isset($_POST["text"]) ? $_POST["text"]:"This work was funded by the European Union in the context of the KHRESMOI project." ?></textarea>
    <br />

    <label>nBestSize</label>
    <input type="text" name="nBestSize" style="width:48px;" maxLength="2" disabled="disabled" />
    <br />

    <label>alignmentInfo</label>
    <input type="checkbox" name="alignmentInfo" />
    <br />

<p>
    <label>docType</label>
    <input type="text" name="wordAlignment" disabled="disabled" />
    <br />

    <label>profileType</label>
    <input type="text" name="wordAlignment" disabled="disabled" />
    <br />
    </p>

  </fieldset>
  <p>
    <input type="submit" value="Translate!" style="font-size:17px;" />
  </p>
  </form>
  <hr>
  <h3>Request (JSON format)</h3>
  <textarea rows="5" cols="100" readonly="yes"><?php
  	if (isset($q)) {
	        $s = str_replace('",', "\",\n  ", json_encode($q));
		$s = str_replace('{', "{\n  ", $s);
		$s = str_replace('}', "\n}", $s);
		print_r($s);
	}
  ?></textarea>
  <hr>
  <h3>Response (JSON format)</h3>
  <div id="response">
  <textarea rows="14" cols="100" readonly="yes"><?php
  	if (isset($response)) {
	  	print_r($response);
	}
  ?></textarea>
  </div>
  <hr>
<?
if (isset($_POST['text'])) { ?>
      <p>
    <i>You can alternatively use a curl tool like this:</i>
    <pre>curl -i -H "Content-Type: application/json" -X POST -d '{
	    "action":"translate", "sourceLang":"<? echo $_POST["sourceLang"]; ?>",
	    "targetLang":"<? echo $_POST["targetLang"]; ?>",
	    "text": "<? echo $_POST["text"] ?>" }'
	    http://quest.ms.mff.cuni.cz:8888/khresmoi</pre> 
    </p>
<?
}
?>


  <hr>
  "This work was funded by the European Union in the context of the
  KHRESMOI project (grant number 257528)".<br>
  <p>
  &copy; 2012 Charles University, <a href="http://ufal.ms.mff.cuni.cz/">Institute of Formal and
  Applied Linguistics</a><br /> Webpage generated at <? echo date('d/m/Y h:i:s A', time()); ?>.
  </p>
  <p>
  Contacts: pecina or bystron at ufal mff cuni cz
  </p>
</body>
</html>
