#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use autodie;

use Query;

sub say {
    my $line = shift;
    print "$line\n";
}

sub tsvsay {
    my $line = join "\t", @_;
    print "$line\n";
}

binmode STDIN, ':utf8';
binmode STDOUT, ':utf8';
binmode STDERR, ':utf8';

{
    # I want my arguments to be UTF-8
    use I18N::Langinfo qw(langinfo CODESET);
    use Encode qw(decode);
    my $codeset = langinfo(CODESET);
    @ARGV = map { decode $codeset, $_ } @ARGV;
}

if ( @ARGV != 3 ) {
    die("Usage: $0 sourceLang targetLang text \n");
}

my ($sourceLang, $targetLang, $text) = @ARGV;

my $query = Query->new({sourceLang => $sourceLang, targetLang => $targetLang});
my $result = $query->call($text);
if ( defined $result ) {
    say $result;
}

