#!/usr/bin/perl -w
use v5.26.0;
use warnings;

my $usage = <<'END_USAGE';
    Usage: make_python_polynomials [options]

        -s  make the optimal mixed strategy polynomials
            for each state (mixed_strategy_polynomials.py)

        -q  make the complete explicit formula for q
            (q_polynomial.py)

END_USAGE

die $usage unless (@ARGV == 1 && $ARGV[0] =~ m{^-[sq]$});

my $option = $ARGV[0];

my $parens;
$parens = qr{
\(
(?:
(?:[^()]++ |
(??{ $parens }))*
)
\)
}x;

system "julia polynomials.jl -$option > out$option.txt";

open(my $in_fh, '<', "out$option.txt") or die "$!";

$/ = undef; # slurp mode
my $polys = <$in_fh>;
close $in_fh;

$polys =~ s{//1}{}g;
$polys =~ s{\^}{**}g;
$polys =~ s{\b(\d+)p}{$1*p}g;
$polys =~ s{\b(\d+)\(}{($1)*(}g;
$polys =~ s{\b (?<!\() (\d+) \b (?!\))}{($1)}gx;

my $make_mpf = sub {
    my $digits = shift;
    return length($digits) > 3 ? "mpf('$digits')" : $digits;
};

$polys =~ s{\( (\d+) \)}{$make_mpf->($1)}gex;

my $write_file_name = $option eq '-s' ? 'mixed_strategy_polynomials.py' : 'q_polynomial.py';

open(my $python_fh, '>', $write_file_name) or die "$!";

my $ndigs = 512;

print $python_fh "from mpmath import mp, mpf\n";
print $python_fh "mp.dps = $ndigs\n";
print $python_fh "mp.prec = $ndigs\n";

if ($option eq '-s'){
    my @formulas = ($polys =~ m{($parens: $parens[ ]*/[ ]*$parens)}g);
    my $dict_body = join ",\n", @formulas;
    
    print $python_fh "STRATEGY_FORMULAS = lambda p: \{\n";
    print $python_fh $dict_body;
    print $python_fh "\n\}";
}
else {
    print $python_fh "Q_FORMULA = lambda p: ";
    print $python_fh $polys;       
}

close $python_fh;

