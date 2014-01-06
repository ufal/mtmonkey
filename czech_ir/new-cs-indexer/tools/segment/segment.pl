#!/usr/bin/env perl

use warnings;
use strict;
use CS::Segment;

my $PARAMS = {
    use_paragraphs => 1,
    use_lines => 0,
    detect_lists => 100,
    limit_words => 250,
};

my @lines = <STDIN>;
my $text = join "\n", @lines;

my @segs = CS::Segment::get_segments($text, $PARAMS);

print join "\n", @segs;
print "\n";
