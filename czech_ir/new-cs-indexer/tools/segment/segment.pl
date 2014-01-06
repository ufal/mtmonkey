#!/usr/bin/env perl

use warnings;
use strict;
use CS::Segment;

BEGIN { $| = 1 }

my $PARAMS = {
    use_paragraphs => 1,
    use_lines => 0,
    detect_lists => 100,
    limit_words => 250,
};

while (my $text = <STDIN>) {
    my @segs = CS::Segment::get_segments($text, $PARAMS);
    print join "\n", @segs;
    print "\n<DOC>\n";
}
