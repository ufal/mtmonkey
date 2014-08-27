<?php

#
# TODO: Set up your Appserver URL and supported languages here
#
$server_url = "&lt;YOUR APPSERVER'S URL&gt;";
$supported_source_langs = array('en', 'de', 'fr', 'cs');
$supported_target_langs = array('en', 'de', 'fr', 'cs');

if (isset($_POST['sourceLang'])) {
    $curl = curl_init($server_url);
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
}
?>

<html>
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <title>MTMonkey simple web client</title>
  <meta name="robots" content="all" />
  <meta http-equiv="cache-control" content="no-cache" />
  <meta charset="UTF-8" />
  <style>
  label {
    font-weight: bold;
  }
  </style>
</head>
<body>
  <h1>MTMonkey simple web client</h1>

  <p>Appserver URL: <?php print($server_url); ?></p>
  <form action="" method="post">
  <fieldset>
    <label>action</label>
    <span>translate</span>
    <br/>

    <label for="sourceLang">sourceLang</label>
    <select name="sourceLang" id="sourceLang">
    <?php
        foreach ($supported_source_langs as $lang){
            echo("<option value=\"$lang\" " . ($_POST["sourceLang"] == $lang ? "selected" : "") . ">$lang</option>");
        }
    ?>
    </select>
    <br />

    <label>targetLang</label>
    <select name="targetLang">
    <?php
        foreach ($supported_target_langs as $lang){
            echo("<option value=\"$lang\" " . ($_POST["targetLang"] == $lang ? "selected" : "") . ">$lang</option>");
        }
    ?>
    </select>
    <br />

    <label>text</label>
    <textarea rows="4" cols="60" name="text" style="font-size:14px;" maxLength="512"><? echo
    isset($_POST["text"]) ? $_POST["text"]:"This is a test." ?></textarea>
    <br />

    <label>nBestSize</label>
    <input type="text" name="nBestSize" style="width:48px;" maxLength="2" />
    <br />

    <label>alignmentInfo</label>
    <input type="checkbox" name="alignmentInfo" />
    <br />

  </fieldset>
  <p>
    <input type="submit" value="Translate!" style="font-size:17px;" />
  </p>
  </form>
<?php
  if (isset($q)){
?>
  <h3>Request (JSON format)</h3>
  <textarea rows="5" cols="100" readonly="yes"><?php
        $s = str_replace('",', "\",\n  ", json_encode($q));
        $s = str_replace('{', "{\n  ", $s);
        $s = str_replace('}', "\n}", $s);
        print_r($s);
  ?></textarea>
  <h3>Response (JSON format)</h3>
  <div id="response">
  <textarea rows="14" cols="100" readonly="yes"><?php
      if (isset($response)) {
          print_r($response);
    }
  ?></textarea>
  </div>
<?php
  }
?>
</body>
</html>
