#!/usr/bin/env perl

use strict;
use warnings;

use JSON;
use Digest::SHA qw(sha1);

my %text_hash = ();

while (my $line = <STDIN>) {
    chomp $line;
    my $decoded_json = JSON::decode_json( $line );
    my $text = $decoded_json->{'doc'}{'htmlContent'}{'text'};
    
    my $sha_sum = sha1($text);
    #print STDERR $sha_sum . "\n";
    if (!defined $text_hash{$sha_sum}) {
        print $line."\n";
        $text_hash{$sha_sum}++;
    }
}
