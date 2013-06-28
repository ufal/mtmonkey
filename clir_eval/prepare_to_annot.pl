#!/usr/bin/env perl

use strict;
use warnings;
use List::Util qw/shuffle/;
use Digest::MD5 qw/md5_hex/;

sub get_text_annot {
    my ($ord, $src_line, $lines, $keys) = @_;

    my $text = "";
    $text .= "$ord: $src_line\n";
    for (my $i = 0; $i < @$keys; $i++) {
        $text .= chr(ord('a')+$i) . ") ";
        $text .= $lines->{$keys->[$i]};
        $text .= "\n";
    }
    $text .= "\n";
}

sub get_text_clue {
    my ($ord, $keys) = @_;
    my $text .= $ord . "\t" . (join " ", @$keys) . "\n";
}

#################################################################

my $src_lang = shift @ARGV;
my $filestem = shift @ARGV;

srand(hex(substr(md5_hex($src_lang),0,4)));

my %tst_paths = (
    'b0' => "$filestem-b0.$src_lang-en",
    'gt' => "$filestem-gt.$src_lang-en",
    'ms' => "$filestem-ms.$src_lang-en",
    'v1' => "$filestem-v1.$src_lang-en",
    'ref' => "$filestem.en",
);
my $src_path = "$filestem.$src_lang";
my $to_annot_path = "$filestem.$src_lang.to_annot";
my $clue_path = "$filestem.$src_lang.clue";

my %tst_fhs = ();
foreach my $key (keys %tst_paths) {
    my $fh;
    open $fh, "<", $tst_paths{$key};
    $tst_fhs{$key} = $fh;
}
open my $src_fh, "<", $src_path;
open my $to_annot_fh, ">", $to_annot_path;
open my $clue_fh, ">", $clue_path;

my $ord = 1;
while (my $src_line = <$src_fh>) {
    chomp $src_line;
    my %lines = ();
    foreach my $key (keys %tst_fhs) {
        my $fh = $tst_fhs{$key};
        $lines{$key} = <$fh>;
        chomp $lines{$key};
    }
    my @shuff_keys = shuffle keys %tst_fhs;
    print $to_annot_fh get_text_annot($ord, $src_line, \%lines, \@shuff_keys);
    print $clue_fh get_text_clue($ord, \@shuff_keys);
    $ord++;
}

foreach my $key (keys %tst_fhs) {
    my $fh = $tst_fhs{$key};
    close $fh;
}
close $src_fh;
close $to_annot_fh;
close $clue_fh;
