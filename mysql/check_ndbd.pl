#!/usr/bin/perl -X
# check_ndbd.pl
# checks memory usage on specified nodes
#


=head1 NAME

check_ndbd.pl

=head1 SYNOPSIS

Can be run without any arguments if you change the inner-defaults:

./check_ndbd.pl

Or everything can be customized with command-line parameters:

check_ndbd.pl --check_command='ndb_mgm' --check_expression='show' --{mgm,ndb,sql}_thresh=3

The threshholds should be customized for your environment

i.e. Set the thresholds to one less than your total number of nodes for strict checking

=head1 DESCRIPTION

This script provides checking of your MySQL NDB cluster.  It should be run on the mgm host
via nagios.  Returns the expected return/exit signals to nagios for critical/warning/OK as
well as useful messaging.

=head1 METHODS
=cut

use strict;
use warnings;

use Getopt::Long;

my $command_prefix = '/usr/local/mysql/bin/';
my $check_command = 'ndb_mgm';
my $check_expression = 'show';
my $host=undef;
my $mgm_thresh=1;
my $ndb_thresh=1;
my $sql_thresh=2;
my $usage=undef;
my $debug = '';

GetOptions(             "host=s"                        => \$host,
                        "check_command=s"               => \$check_command,
                        "check_expression=s"    => \$check_expression,
                        "mgm_thresh=s"                  => \$mgm_thresh,
                        "ndb_thresh=s"                  => \$ndb_thresh,
                        "sql_thresh=s"                  => \$sql_thresh,
                        "usage"                                 => \$usage,
                        "debug"                                 => \$debug,
);

=head2 main

Wrapper function that handles the signals/exitting and messaging

=cut

sub main {
        if ($usage||  !defined $host ) {
                usage();
                exit(0);
        }
        my $is_critical=0;
        my $mgm_value=0;
        my $ndb_value=0;
        my $sql_value=0;
        my @mgm_node_ids = typecheck('MGM');
        my @ndb_node_ids = typecheck('NDB');
        my @sql_node_ids = typecheck('SQL');
        foreach(@mgm_node_ids) {
                $mgm_value += status_check($_);
        }
        foreach(@ndb_node_ids) {
                $ndb_value += status_check($_);
        }
        foreach(@sql_node_ids) {
                $sql_value += status_check($_);
        }
        if ( $mgm_value > $mgm_thresh ) { print "CRITICAL: $mgm_value MGM nodes not connected; "; $is_critical=1; }
        if ( $ndb_value > $ndb_thresh ) { print "CRITICAL: $ndb_value NDB nodes are not in the started state; "; $is_critical=1; }
        if ( $sql_value > $sql_thresh ) { print "CRITICAL: ".($sql_value-$sql_thresh)." SQL nodes not connected; "; $is_critical=1; }
        if ($is_critical) {
                print "\n";
                exit(2);
        } else {
                print "OK -  MGM: $mgm_value, NDB: $ndb_value, SQL: .($sql_value-$sql_thresh). Acceptable number of nodes connected.\n";
                exit(0);
        }
}

=head2 typecheck

Determines the type of node that is being checked (MGM,NDB,SQL)

=cut

sub typecheck {
        my ($type_to_check) = @_;
        if ($debug) {
                print "$type_to_check\n";
        }
        open(NS, $command_prefix.$check_command." --ndb-mgmd-host=$host  -e $check_expression |") || die "Command failed! Check the script cause it sucks...\n";
        my $node_type;
        my @results;
        while ( <NS> ) {
                my $line = $_;
                if ($line =~ m/NDB/) {
                        $node_type = 'NDB';
                }
                elsif ($line =~ m/MGM/) {
                        $node_type = 'MGM';
                }
                elsif ($line =~ m/API/) {
                        $node_type = 'SQL';
                }
                if ($line =~ m/id=(\d+)/) {
                        if ( $node_type eq $type_to_check ) { push(@results, $1); }
                }
        }
        close(NS);
        return (@results);
}

=head2 status_check

For each node in the list, it runs the check command and returns
the current status for that node.

=cut

sub status_check {
        my ($node) = @_;

        my $status;
        $check_expression = "\'$node status\'";
        open(NS, $command_prefix.$check_command." -e $check_expression |") || die "Command failed!  Is your path (prefix) correct?\n";
        while( <NS> ) {
                if ($_ =~ m/started/) {
                        $status = 0;
                }
                elsif ($_ =~ m/: connected/){
                        $status = 0;
                }
                elsif ($_ =~ m/not connected/){
                        $status = 1;
                }
                elsif ($_ =~ m/starting/) {
                        $status = 1;
                }
        }
        close(NS);
        if ($debug) {
                print "$node - $status\n";
        }
        return $status;
}

=head2 usage

If run without the proper parameters, returns this usage block.

=cut

sub usage {
        print "\nndbd node status checker\n";
        print "Usage:\n";
        print "\t--host \t\tThe ndb manager to connect to\n";
        print "\t--mgm_thresh=n   Sets mgm minimum node threshold\n";
        print "\t--ndb_thresh=n   Sets ndb minimum node threshold\n";
        print "\t--sql_thresh=n   Sets sql minimum node threshold\n\n";
        return 0;
}

main();

=head1 AUTHOR

Steven W. Carter
steven.w.carter@gmail.com

=head1 LICENSE

This library is free software, you can redistribute it and/or modify it under the same terms as Perl itself.

=cut
