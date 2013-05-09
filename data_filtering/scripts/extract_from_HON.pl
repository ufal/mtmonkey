#!/usr/bin/env perl

use strict;
use warnings;

use JSON;
use Data::Dumper;

#binmode STDOUT, ":utf8";

while (my $line = <STDIN>) {
    chomp $line;
    my $decoded_json = JSON::decode_json( $line );

    my $text = $decoded_json->{'doc'}{'htmlContent'}{'text'};
    my $title = $decoded_json->{'doc'}{'title'};
    my $lang = $decoded_json->{'doc'}{'language'};

    my $instance = {
        lang => $lang,
        title => $title,
        text => $text,
    };

    my $encoded_json = JSON::encode_json($instance);
    print $encoded_json . "\n";

    #print Dumper($decoded_json);
    #print $text;
    #print "\n";
    #print "\n";
}   
