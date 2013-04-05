<!DOCTYPE html>
<html lang="en">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
  <script src="js/jquery.js" type="text/javascript"></script>
  <script src="js/khresmoi.js"></script>
  <link href="css/main.css" rel="stylesheet" type="text/css" />
</head>
<body>
  <div id="wrap">
    <div id="header">
      <div style="float:left;">
          <img src="img/logo.png" alt="Logo" style="width:200px;float:right;" />
      </div>
      <span style="float:right;margin-top:34px;">CUNI Machine Translation Service</span>
    </div>  <!-- header -->

    <div id="main">
        <!-- Source -->
        <div id="source">
            <div id="src-lang">
                <input type="radio" id="radio1" name="radio-src" l="en" checked="checked"
                /><label for="radio1">English</label>
                <input type="radio" id="radio2" name="radio-src" l="fr" /><label for="radio2">French</label>
                <input type="radio" id="radio3" name="radio-src" l="de" /><label for="radio3">German</label>
                <input type="radio" id="radio4" name="radio-src" l="cs" /><label for="radio4">Czech</label>
            </div>
            <div>
                <textarea id="src" name="text" wrap="SOFT" tabindex="0"
                        spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off"></textarea>
            </div>
        </div> <!-- source -->

        <div id="destination">
            <div id="dest-lang">
                <input type="radio" id="radio5" style="display:none;" name="radio-dest" l="en"
                /><label style="display:none;" for="radio5">English</label>
                <input type="radio" id="radio6" name="radio-dest" l="fr" /><label for="radio6">French</label>
                <input type="radio" id="radio7" name="radio-dest" l="de" checked="checked"
                /><label for="radio7">German</label>
                <input type="radio" id="radio8" name="radio-dest" l="cs" /><label for="radio8">Czech</label>
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
                                      "This work was funded by the European Union in the context
                                      of the KHRESMOI project (grant number 257528)".<br>
                                                                      © 2012 Charles University,
                                                                      Institute of Formal and
                                                                      Applied Linguistics</div>
    </div>  <!-- footer -->
  </div>  <!-- wrap -->
</body>
