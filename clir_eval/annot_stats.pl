#!/usr/bin/env perl

use strict;
use warnings;
use Math::Combinatorics;
use Data::Dumper;

use List::Util qw/sum/;

my $lang = $ARGV[0];
my $data_type = $ARGV[1];
my $clue_path = "data/$data_type.$lang.clue";
my $annot_path = "annot/$data_type.$lang.annot1";

#my @systems = ('b0','gt','ref');    # ommitting v1 only for German
my @systems = ('b0','v1','gt','ref');    
if ($lang eq "de" && $data_type eq "mt-test") {
    push @systems, "v1d";
}
my @sys_pairs = combine(2, @systems);
    
sub update_annot_stats {
    my ($stats, $item_annot, $clue_line) = @_;
    (my $ord, $clue_line) = split /\t/, $clue_line;
    my @clue_vals = split / /, $clue_line;
    my %clue = map {$clue_vals[$_] => chr(ord('a')+$_)} (0 .. @clue_vals-1);

    foreach my $pair (@sys_pairs) {
        my ($p1, $p2) = @$pair;
        # assings -1, 0, 1
        #print STDERR Dumper($item_annot);
        my $res = $item_annot->{$clue{$p1}} <=> $item_annot->{$clue{$p2}};
        $stats->{"$p1-$p2"}->[$res+1]++;
    }

    #print STDERR $clue_line ."\n"; 
    #print STDERR  join ", ", (map {$_ . "=" . $item_annot->{$_}} (keys %$item_annot));
    #print STDERR "\n";
    #print STDERR Dumper($stats);

}

sub print_normal {
    my ($stats) = @_;

    print "s1-s2\ts1>s2\ts1=s2\ts1<s2\n";
    print "-----------------------------\n";
    foreach my $key (keys %$stats) {
        print $key . "\t";
        print join "\t", @{$stats->{$key}};
        print "\n";
    }
}

sub print_tex {
    my ($stats) = @_;

    print " & ". (join " & ", @systems) . "\n";
    foreach my $s1 (@systems) {
#        print $s1;
        foreach my $s2 (@systems) {
            if ($s1 eq $s2) {
                print " & --";
                next;
            }
            my $better;
            my $count;
            if (defined $stats->{"$s1-$s2"}) {
                $better = $stats->{"$s1-$s2"}->[2];
                $count = sum @{$stats->{"$s1-$s2"}};
            }
            else {
                $better = $stats->{"$s2-$s1"}->[0];
                $count = sum @{$stats->{"$s2-$s1"}};
            }
            printf " & %.4f", $better / $count;
        }
        print "\n";
    }
    my %sum_stats = map {$_ => [0, 0]} @systems;
    foreach my $key (keys %$stats) {
        my ($s1, $s2) = split /-/, $key;
        $sum_stats{$s1}->[0] += $stats->{$key}->[0];
        $sum_stats{$s2}->[0] += $stats->{$key}->[2];
        $sum_stats{$s1}->[1] += $stats->{$key}->[2];
        $sum_stats{$s2}->[1] += $stats->{$key}->[0];
    }
#    print "> others";
    foreach my $s1 (@systems) {
        printf " & %.4f", $sum_stats{$s1}->[0] / sum @{$sum_stats{$s1}};
    }
    print "\n";
}

sub proportion_of_ties {
    my ($stats) = @_;

    print "TIES RATIO:\n";
    foreach my $sys (@systems) {
        my $ties_for_sys = 0;
        my $all_for_sys = 0;
        foreach my $key (keys %$stats) {
            my ($s1, $s2) = split /-/, $key;
            next if ($s1 ne $sys && $s2 ne $sys);
            $ties_for_sys += $stats->{$key}->[1];
            $all_for_sys += sum @{$stats->{$key}};
        }
        printf "%s: %.2f\n", $sys, $ties_for_sys / $all_for_sys; 
    }
    my $ties_all = 0;
    my $all = 0;
    foreach my $key (keys %$stats) {
        my ($s1, $s2) = split /-/, $key;
        $ties_all += $stats->{$key}->[1];
        $all += sum @{$stats->{$key}};
    }
    printf "all: %.2f\n", $ties_all / $all;
}

open my $clue_file, "<", $clue_path;
open my $annot_file, "<", $annot_path;

my $stats = {};

my $empty_lines = 0;
my $order = 1;
my %item_annot = ();
while (my $annot_line = <$annot_file>) {
    chomp $annot_line;
    $annot_line =~ s/\r$//;
    if ($empty_lines == 1) {
        my @letters = split /, ?/, $annot_line;
        $item_annot{$_} = $order foreach (@letters);
        $order++;
    }


    if ($annot_line =~ /^\s*$/) {
        $empty_lines++;
    }
    if ($empty_lines == 2) {
        my $clue_line = <$clue_file>;
        chomp $clue_line;

        update_annot_stats($stats, \%item_annot, $clue_line);

        $empty_lines = 0;
        $order = 1;
        %item_annot = ();
    }
}
close $clue_file;
close $annot_file;
print_normal($stats);
print "========================\n";
print_tex($stats);
print "========================\n";
proportion_of_ties($stats);
#print Dumper($stats);
