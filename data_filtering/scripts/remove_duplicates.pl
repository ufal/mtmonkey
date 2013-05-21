#!/usr/bin/env perl

use strict;
use warnings;

use Digest::SHA qw(sha1);

my %text_hash = ();

while (my $line = <STDIN>) {
    my $sha_sum = sha1($line);
    #print STDERR $sha_sum . "\n";
    if (!defined $text_hash{$sha_sum}) {
        print $line;
        $text_hash{$sha_sum}++;
    }
}
