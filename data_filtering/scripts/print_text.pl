#!/usr/bin/env perl

use strict;
use warnings;

use JSON;
use Data::Dumper;
use Getopt::Long;

#binmode STDIN, ":encoding(UTF-8)";
binmode STDOUT, ":utf8";

my $lang_def;

my %yali_to_lang = (
    'ces' => 'cs',
    'deu' => 'de',
    'eng' => 'en',
    'fra' => 'fr',
    'ita' => 'it',
    'slk' => 'sk',
    'spa' => 'sp',
);

GetOptions(
    "lang|l=s" => \$lang_def,
);

#binmode STDOUT, ":utf8";

while (my $line = <STDIN>) {
    chomp $line;
    my $decoded_json = JSON::decode_json( $line );

    my $text = $decoded_json->{'text'};
    my $lang = $decoded_json->{'lang'};
    my $yali_khresmoi_lang = $decoded_json->{'yali_khresmoi_id'};
    my $yali_lang = $decoded_json->{'yali_id'};

    if (!$lang_def || ($lang_def && ($lang eq $lang_def) && ($yali_to_lang{$yali_khresmoi_lang} eq $lang_def) && ($yali_to_lang{$yali_lang} eq $lang_def))) {
        print $text . "\n";
    }
}   
