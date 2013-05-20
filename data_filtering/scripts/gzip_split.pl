#!/usr/bin/env perl

use strict;
use warnings;

use PerlIO::gzip;
use Getopt::Long;

my $limit = 100000;

GetOptions(
    "lines|l=i" => \$limit,
);

my $filename = shift @ARGV;

my $fileno = 1;
my $line = 0;

my $fh;

while (<>) {
    if (!$fh || $line >= $limit) {
        my $path = sprintf "%s%03d.gz", $filename, $fileno;
        open $fh, '>:gzip', $path;
        print STDERR "Printing to $path\n";
        $fileno++;
        $line = 0; 
    }
    print $fh $_; 
    $line++;
}
