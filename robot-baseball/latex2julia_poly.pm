#!/usr/bin/perl -w
use v5.26.0;
use warnings;

die "Incorrect number of command line arguments present" unless @ARGV == 1;

my $arg;
$arg = qr{
\{
(?<contents>
(?:[^{}]++ |
(??{ $arg }))*
)
\}
}x;

my $bs = qr{(?<!\\)\\};

$/ = undef;
my $text = <>; #slurp

$text =~ s{p\^$arg}{(p^$1)}g;

$text =~ s{(?<!\()p\^(\d+)(?!\))}{(p^$1)}g;

while ($text =~ m{\\frac$arg$arg}) {
    $text =~ s{\\frac$arg$arg}{(($1)/($2))}g;
}

$text =~ s{\)\(}{)*(}g;



print $text;
