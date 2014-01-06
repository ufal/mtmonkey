package CS::Tokenize;
use utf8;

sub tokenize_sentence {

    my ( $sentence ) = @_;

    #print STDERR $sentence."\n";

    # first off, add a space to the beginning and end of each line, to reduce necessary number of regexps.
    $sentence =~ s/$/ /;
    $sentence =~ s/^/ /;

    # detect web sites and email addresses and protect them from tokenization
    ($sentence, my $urls) = _mark_urls($sentence);

    # the following characters (double-characters) are separated everywhere
    $sentence =~ s/(;|!|<|>|\{|\}|\[|\]|\(|\)|\?|\#|\$|£|\%|\&|``|\'\'|‘‘|"|“|”|«|»|--|–|—|„|‚|‘|\*|\^|\|)/ $1 /g; ## no critic (RegularExpressions::ProhibitComplexRegexes) this is not complex

    # short hyphen is separated if it is followed or preceeded by non-alphanuneric character and is not a part of --, or a unary minus
    $sentence =~ s/([^\-\w])\-([^\-0-9])/$1 - $2/g;
    $sentence =~ s/([0-9]\s+)\-([0-9])/$1 - $2/g; # preceded by a number - not a unary minus
    $sentence =~ s/([^\-])\-([^\-\w])/$1 - $2/g;
    
    # plus is separated everywhere, except at the end of a word (separated by a space) and as unary plus
    $sentence =~ s/(\w)\+(\w)/$1 + $2/g;
    $sentence =~ s/([0-9]\s*)\+([0-9])/$1 + $2/g;
    $sentence =~ s/\+([^\w\+])/+ $1/g;

    # apostroph is separated if it is followed or preceeded by non-alphanumeric character, is not part of '', and is not followed by a digit (e.g. '60).
    $sentence =~ s/([^\'’\w])([\'’])([^\'’\d])/$1 $2 $3/g;
    $sentence =~ s/([^\'’])([\'’])([^\'’\w])/$1 $2 $3/g;

    # dot, comma, slash, and colon are separated if they do not connect two numbers
    $sentence =~ s/(\D|^)([\.,:\/])/$1 $2 /g;
    $sentence =~ s/([\.,:\/])(\D|$)/ $1 $2/g;

    # three dots belong together
    $sentence =~ s/\.\s*\.\s*\./.../g;

    # get back web sites and e-mails
    $sentence = _restore_urls($sentence, $urls);

    # clean out extra spaces
    $sentence =~ s/\s+/ /g;
    $sentence =~ s/^ *//g;
    $sentence =~ s/ *$//g;

    # pad with spaces for easier regexps
    $sentence =~ s/^(.*)$/ $1 /;

    # Czech conditional enclitic "-li" should be treated as a separate token
    $sentence =~ s/ (\p{Letter}+)-(li|LI) / $1 - $2 /g;
    
    # Number ranges are considered 3 tokens in PDT (and thus learned to be treated so by parsers)
    $sentence =~ s/([0-9])\-([0-9])/$1 - $2/g;

    # clean out extra spaces
    $sentence =~ s/^\s*//g;
    $sentence =~ s/\s*$//g;

    return $sentence;
}

# internally marks URLs, so they won't be splitted
sub _mark_urls {
    my ( $sentence ) = @_;
    my @urls;
    while ( $sentence =~ s/(\W)((http:\/\/)?([\w\-]+\.)+(com|cz|de|es|eu|fr|hu|it|sk))(\W)/$1 XXXURLXXX $6/ ) { ## no critic (RegularExpressions::ProhibitComplexRegexes) this is not complex
        push @urls, $2;
    }
    return ($sentence, \@urls);
}

# pushes bask URLs, marked by C<_mark_urls>
sub _restore_urls {
    my ( $sentence, $urls ) = @_;
    while (@$urls) {
        my $url = shift @$urls;
        $sentence =~ s/XXXURLXXX/$url/;
    }
    return $sentence;
}

1;

__END__

=encoding utf-8

=head1 NAME 

CS::Tokenize

=head1 DESCRIPTION

Each sentence is split into a sequence of tokens.

=head1 AUTHORS

David Mareček <marecek@ufal.mff.cuni.cz>

Ondřej Dušek <odusek@ufal.mff.cuni.cz>

Michal Novák <mnovak@ufal.mff.cuni.cz>

=head1 COPYRIGHT AND LICENSE

Copyright © 2011-2014 by Institute of Formal and Applied Linguistics, Charles University in Prague

This module is free software; you can redistribute it and/or modify it under the same terms as Perl itself.
