MTMonkey web clients
====================

These are simple web clients that can connect to your MTMonkey Appserver 
and dispatch translation requests:

* `simple` -- a very simple PHP client
* `ajax` -- a more fancy client that uses AJAX requests to process translations

Installation
------------

### Simple client ###

Just place the `index.php` file somewhere to a path on your web server 
that gets processed by PHP. Edit the file and setup your Appserver's URL
and language capabilities in the `$server_url`, `$supported_source_langs`,
and `$supported_target_langs` variables.

### AJAX client ###

Copy the whole `ajax/` subdirectory to path on your web server that 
gets processed by PHP. Then you need to:

1. Set up the server URL in `query.php`
2. Edit `index.php` to add correct radio buttons for all supported languages.
3. Edit `js/mtmonkey_query.js` to adjust for the number of supported language
    pairs and the main pivot language (if it is not English).


TODOs
-----

* Make the AJAX client more flexible
