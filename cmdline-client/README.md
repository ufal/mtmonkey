
MTMonkey command-line clients
=============================

There are two command-line clients written in Perl
(requiring `Moose`, `WWW::Curl::Easy`, and `JSON` from cpan):

* `translate_txt.pl` – translating simple text files, line-by-line
* `translate_csv.pl` – translating a column of a CSV file

Both read from standard input and write to standard output
and both require the Appserver URL and language pair settings
given as command-line parameters.

Please run the commands without any parameters to obtain usage 
information.

