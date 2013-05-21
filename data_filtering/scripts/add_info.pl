#!/usr/bin/env perl

use strict;
use warnings;

use JSON;
use Data::Dumper;

use Getopt::Long;

my $yali_ids_path;

GetOptions(
    "yali-ids=s" => \$yali_ids_path,
);

#binmode STDOUT, ":utf8";

open YALI, $yali_ids_path or die $_;

while (my $line = <STDIN>) {
    chomp $line;
    my $lang_id = <YALI>;
    chomp $lang_id;
    
    my $decoded_json = JSON::decode_json( $line );
    $decoded_json->{'yali_id'} = $lang_id;


    my $encoded_json = JSON::encode_json($decoded_json);
    print $encoded_json . "\n";

    #print Dumper($decoded_json);
    #print $text;
    #print "\n";
    #print "\n";
}
close YALI;
