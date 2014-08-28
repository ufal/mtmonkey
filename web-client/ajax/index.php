<!DOCTYPE html>
<?php
# TODO set your supported language pairs here
$lang_pairs = array('en-de', 'de-en', 'en-fr', 'fr-en', 'en-cs', 'cs-en');

$lang_names = array();
$src_langs = array();
$dest_langs = array();

# Get language names for ISO codes
foreach ($lang_pairs as $pair){
    $langs = preg_split('/-/', $pair);
    foreach ($langs as $lang){
        if (!isset($lang_names[$lang])){
            $lang_names[$lang] = locale_get_display_language($lang, 'en');
        }
    }
    if (!isset($src_langs[$langs[0]])){
        $src_langs[$langs[0]] = array();
    }
    array_push($src_langs[$langs[0]], $langs[1]);
    if (FALSE === array_search($langs[1], $dest_langs)){
        array_push($dest_langs, $langs[1]);
    }
}

?>
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <script src="js/jquery.js" type="text/javascript"></script>
  <script src="js/mtmonkey_query.js" type="text/javascript"></script>
  <script type="text/javascript">
$(document).ready(function(){
<?php
foreach ($src_langs as $src => $dests){
    print "\t$('#radio-src-$src').data('compatible', ['" . implode("', '", $dests) . "']);\n";
}
?>
    langSetup();
});
  </script>
  <link href="css/main.css" rel="stylesheet" type="text/css" />
</head>
<body>
  <div id="wrap">
    <div id="header">
      <div style="float:left;">
          <img src="img/logo.png" alt="Logo" style="width:200px;float:right;" />
      </div>
      <span style="float:right;margin-top:34px;">MTMonkey AJAX web client</span>
    </div>  <!-- header -->

    <div id="main">
        <!-- Source -->
        <div id="source">
            <div id="src-lang">
<?php
foreach ($src_langs as $src => $dests){
    # keep 1st language pair checked by default
    $checked = strpos($lang_pairs[0], $src) === 0 ? 'checked="checked"' : '';
    print "\t\t\t<input type=\"radio\" id=\"radio-src-$src\" name=\"radio-src\" value=\"$src\" $checked/>";
    print "<label for=\"radio-src-$src\">" . $lang_names[$src] . "</label>\n";
}
?>
            </div>
            <div>
                <textarea id="src" name="text" wrap="SOFT" tabindex="0"
                        spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off"></textarea>
            </div>
        </div> <!-- source -->

        <div id="destination">
            <div id="dest-lang">
<?php
foreach ($dest_langs as $dest){
    # keep 1st language pair checked by default
    $checked = substr($lang_pairs[0], -strlen($dest)) === $dest ? 'checked="checked"' : '';
    print "\t\t\t<input type=\"radio\" id=\"radio-dest-$dest\" name=\"radio-dest\" value=\"$dest\" $checked/>";
    print "<label for=\"radio-dest-$dest\">" . $lang_names[$dest] . "</label>\n";
}
?>
            </div>
            <div>
                <textarea id="dest" disabled="disabled" name="text" wrap="SOFT"
                        spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off"></textarea>
            </div>
        </div> <!-- destination -->

        <span id="go" class="button4">Translate &gt;&gt;</span>
    </div>  <!-- main -->

    <div id="align-wrap">
      <div id="align"></div>
    </div> <!-- align -->

    <div id="right">
      <h1 id="detail-show">+ JSON API Request & Response (click to show)</h1>
      <div id="detail">
      <div id="q-div">
        <textarea id="q" readonly="readonly"></textarea>
      </div>
      <div id="r-div">
        <textarea id="r" readonly="readonly"></textarea>
      </div>
      </div>
    </div>  <!-- right -->

    <div id="footer">
      <hr>
      <div id="logo">
This work was funded by the European Union in the context of the KHRESMOI project (grant number 257528).<br>
© 2012-2014 Charles University, Institute of Formal and Applied Linguistics</div>
    </div>  <!-- footer -->
  </div>  <!-- wrap -->
</body>
