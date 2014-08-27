#!/usr/bin/env perl
#
# Translating a column in a CSV file.
#

use strict;
use warnings;
use utf8;
use autodie;

use Query;
use Text::CSV;
use Getopt::Long;

binmode STDOUT, ':utf8';
binmode STDERR, ':utf8';

{
    # converting command line arguments to UTF-8
    use I18N::Langinfo qw(langinfo CODESET);
    use Encode qw(decode);
    my $codeset = langinfo(CODESET);
    @ARGV = map { decode $codeset, $_ } @ARGV;
}

my $USAGE = "Usage: $0 -u url -f sourceLang -t targetLang [-c col] " .
        "[-s system-name] [-e encoding] < in.csv > out.csv \n";

my $url;
my ($sourceLang, $targetLang);
my $col = 0;
my $system_name = 'KhresmoiTranslator';
my $encoding = 'utf8';

GetOptions(
    'url|u=s' => \$url,
    'sourceLang|srcLang|src|from|f=s' => \$sourceLang,
    'targetLang|trgLang|trg|to|t=s' => \$targetLang,
    'column|colno|col|c=i' => \$col,
    'systemName|sysName|system|sys|s=s' => \$system_name,
    'encoding|enc|e=s' => \$encoding,
) or die($USAGE);


if (!$url or !$sourceLang or !$targetLang or @ARGV){
    die($USAGE);
}

binmode STDIN, ":encoding($encoding)";

my $query = Query->new({
        sourceLang => $sourceLang,
        targetLang => $targetLang,
        url => $url,
    });


my $csv = Text::CSV->new();
my $line_no = 0;

while ( my $row = $csv->getline( \*STDIN ) ) {
    
    if ($line_no == 0){
        push @$row, "Col $col translated ($system_name:$sourceLang-$targetLang)";
    }
    else {
        my $result = $query->call($row->[$col]);
        if ( defined $result ) {
            push @$row, $result;
        } 
        else {
            push @$row, "ERROR";
            warn "ERROR on line $line_no!\n";
       }
   }
   $csv->print(\*STDOUT, $row);
   print STDOUT "\n";
   $line_no++;
}

