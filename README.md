
MTMonkey – an infrastructure for Machine Translation web services
=================================================================

Authors: Aleš Tamchyna, Ondřej Dušek, Rudolf Rosa

Copyright © 2013 Institute of Formal and Applied Linguistics,
   Charles University in Prague.

Licensed under the Apache License, Version 2.0.

When using this software in your scientific work, please cite the
following paper: 
Aleš Tamchyna, Ondřej Dušek, and Rudolf Rosa: "MTMonkey: A scalable
infrastructure for a Machine Translation web service". In *Prague
Bulletin of Mathematical Linguistics* 100, 2013 (in print).

Contents of this package
------------------------

* `appserver` – source codes of the application server
* `config-example` – example configuration files
* `install` – installation scripts and instructions
* `scripts` – application server, worker and Moses servers startup scripts
* `web-client` – a simple PHP-based web client for the service
* `worker` – source codes of the worker, incl. text pre- and post-processing
             tools.

Subdirectories not mentioned in this list are used for testing purposes.

Usage
-----

For installation notes for both workers and the application
server, see `install/README.md`.

For a more detailed description of the overall architecture of this system,
see the above mentioned paper (a link will be added as soon as the paper
will be published).
