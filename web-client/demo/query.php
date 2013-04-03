<?php
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
	print $response;
?>
