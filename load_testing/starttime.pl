#!/usr/bin/env perl
use strict;
use warnings;
use utf8;
use autodie;

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

if ( @ARGV != 1 ) {
    die("Usage: $0 start_in_seconds \n");
}

my $starttimeinfile = 'start.time';

my $now = time;
say "Current time is $now";

my $starttime = $now + $ARGV[0];
{
    open my $file, '>', $starttimeinfile;
    print $file $starttime;
    close $file;
}
say "Start time set to $starttime";

