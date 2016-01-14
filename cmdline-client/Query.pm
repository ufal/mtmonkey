package Query;
use Moose;
use utf8;
use strict;
use warnings;

use WWW::Curl::Easy;
use JSON;

has url => ( is => 'ro', isa => 'Str', default => 'http://quest.ms.mff.cuni.cz:8888/khresmoi' );

has sourceLang => ( is => 'rw', isa => 'Str', default => 'cs' );

has targetLang => ( is => 'rw', isa => 'Str', default => 'en' );

has systemId => ( is => 'ro', isa => 'Str', default => '' );

sub call {
    my ($self, $text) = @_;

    my $query = {
        action => "translate",
        sourceLang => $self->sourceLang,
        targetLang => $self->targetLang,
        text => $text,
        #alignmentInfo => JSON::false,
        systemId => $self->systemId,
    };

    my $curl = WWW::Curl::Easy->new;

    #$curl->setopt(CURLOPT_HEADER,1);
    $curl->setopt(CURLOPT_URL, $self->url);
    $curl->setopt(CURLOPT_USERPWD, "test:test123");
    $curl->setopt(CURLOPT_HTTPAUTH, CURLAUTH_BASIC);
    #$curl->setopt(CURLOPT_RETURNTRANSFER, "true");
    $curl->setopt(CURLOPT_POST, 1);
    $curl->setopt(CURLOPT_HTTPHEADER, ['Content-Type: application/json; charset=utf-8']);
    $curl->setopt(CURLOPT_POSTFIELDS, encode_json($query));

    my $response;
    $curl->setopt(CURLOPT_WRITEDATA,\$response);

    my $retcode = $curl->perform;

    if ($retcode == 0) {
        my $returned_data = decode_json($response);
        my $errorCode = $returned_data->{errorCode};
        if ( $errorCode == 0) {
            # If the input line was segmented into more sentences,
            # concatenate those sentences' translations into one string.
            # Take only the 1-best translation
            # (nBestSize default value is 1, so there should be no other variants anyway).
            my @sentences = @{$returned_data->{translation}};
            my $translation = join ' ', map {$_->{translated}->[0]->{text}} @sentences;

            if ( defined $translation ) {
                return $translation;
            }
            else {
                warn ("A problem occured: " . $curl->getinfo(CURLINFO_RESPONSE_CODE) . "\n");
                return undef;
            }
        }
        else {
            warn ("The MT service returned an error: $errorCode " .
                $returned_data->{errorMessage} . "\n");
            return undef;
        }
    } else {
        # Error code, type of error, error message
        warn ("A networking error happened: $retcode " . $curl->strerror($retcode) . " " . $curl->errbuf . "\n");
        return undef;
    }
}

1;

=head1 NAME 



=head1 DESCRIPTION

=head1 PARAMETERS

=over

=back

=head1 AUTHOR

Rudolf Rosa <rosa@ufal.mff.cuni.cz>

=head1 COPYRIGHT AND LICENSE

Copyright © 2013 by Institute of Formal and Applied Linguistics,
Charles University in Prague

This module is free software; you can redistribute it and/or modify it
under the same terms as Perl itself.

