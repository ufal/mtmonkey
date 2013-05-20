#!/usr/bin/env perl

use strict;
use warnings;

use JSON;
use Data::Dumper;
use Getopt::Long;

#binmode STDIN, ":encoding(UTF-8)";
binmode STDOUT, ":utf8";

my $lang_def;

GetOptions(
    "lang|l=s" => \$lang_def,
);

#binmode STDOUT, ":utf8";

while (my $line = <STDIN>) {
    chomp $line;
    my $decoded_json = JSON::decode_json( $line );

    my $text = $decoded_json->{'text'};
    my $lang = $decoded_json->{'lang'};

    if (!$lang_def || ($lang_def && ($lang eq $lang_def))) {
        print $text . "\n";
    }
}   
