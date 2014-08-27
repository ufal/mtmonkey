#!/usr/bin/env perl
#
# Translating a text file, line-by-line
#

use strict;
use warnings;
use utf8;
use autodie;

use Query;
use Getopt::Long;

binmode STDIN, ':utf8';
binmode STDOUT, ':utf8';
binmode STDERR, ':utf8';

{
    # converting command line arguments to UTF-8
    use I18N::Langinfo qw(langinfo CODESET);
    use Encode qw(decode);
    my $codeset = langinfo(CODESET);
    @ARGV = map { decode $codeset, $_ } @ARGV;
}

my $USAGE = "Usage: $0 -u url -f sourceLang -t targetLang < in.txt > out.txt\n";

my $url;
my ($sourceLang, $targetLang);

GetOptions(
    'url|u=s' => \$url,
    'sourceLang|srcLang|src|from|f=s' => \$sourceLang,
    'targetLang|trgLang|trg|to|t=s' => \$targetLang,
) or die($USAGE);

if (!$url or !$sourceLang or !$targetLang or @ARGV){
    die($USAGE);
}

my $query = Query->new({
        sourceLang => $sourceLang,
        targetLang => $targetLang,
        url => $url,
    });

my $line_no = 0;

while (my $line = <STDIN>) {
    chomp $line;
    my $result = $query->call($line);
    if ( defined $result ) {
        print $result, "\n";
    } 
    else {
        print "ERROR on line ", $line_no, "\n";
        warn "ERROR on ", $line_no, "\n";
    }
}
