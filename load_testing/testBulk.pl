#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use autodie;

use Time::HiRes qw( usleep ualarm gettimeofday tv_interval nanosleep
clock_gettime clock_getres clock_nanosleep clock stat );
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

if ( @ARGV < 2 || @ARGV > 3 ) {
    die("Usage: $0 filename sourceLang [targetLang] \n");
}

my ($filename, $sourceLang, $targetLang) = @ARGV;
if ( !defined $targetLang ) {
    $targetLang='en';
}
my $starttimeinfile = 'start.time';

my $starttime;
{
    open my $file, '<:utf8', $starttimeinfile;
    $starttime = <$file>;
    chomp $starttime;
    close $file;
}

my $query = Query->new({
        sourceLang => $sourceLang,
        targetLang => $targetLang,
        # url => 'http://quest.ms.mff.cuni.cz:8889/khresmoi',
    });
my $t0;
my $t1;
my $linecount = 0;
my $wordcount = 0;
my $charcount = 0;
{
    open my $file, '<:utf8', $filename;
    my $line;
    
    # wait for it
    while ( $starttime > time ) {
        my $now = time;
        if ( ($starttime - 2) > $now ) {
            # more than 2 secs to go -> sleep for a while...
            warn "sleeping for " . ($starttime - $now - 2) . "s...\n";
            sleep ($starttime - $now - 2);
        }
    }

    # translate
    $t0 = [gettimeofday];
    while ($line = <$file>) {
        chomp $line;
        $query->call($line);
    }
    $t1 = [gettimeofday];

    # analyze file
    seek $file, 0, 0;
    while ($line = <$file>) {
        $linecount++;
        chomp $line;
        $charcount += length $line;
        my @words = split /[ ,\.\-]/, $line;
        $wordcount += @words;
    }    

    close $file;
}    

my $interval = tv_interval($t0, $t1) * 1000;
tsvsay( $interval, 'ms total' );
tsvsay( $interval/$linecount, 'ms avg per line' );
tsvsay( $interval/$wordcount, 'ms avg per word' );
tsvsay( $interval/$charcount, 'ms avg per char' );


