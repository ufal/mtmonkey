#!/usr/bin/env perl

use warnings;
use strict;
use CS::Tokenize;

foreach my $sentence (<STDIN>) {
    chomp $sentence;
    my $ws_sentence = CS::Tokenize::tokenize_sentence($sentence);
    print "$ws_sentence\n";
}
