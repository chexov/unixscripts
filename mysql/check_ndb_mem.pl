#!/usr/bin/env perl
# check_ndb_mem.pl
# checks memory usage on specified nodes
#
# MonKey, 2013

use strict;
use warnings;

use Getopt::Long;

my $check_command = '/usr/local/mysql/bin/ndb_mgm ';
my $check_expression = 'report MemoryUsage';
my $warn_thresh=70;
my $crit_thresh=80;

my $host=undef;
my $nodes=undef;
my $usage=undef;
my $debug=undef;
my $exit_code=0;

GetOptions(
                        "host=s"                        => \$host,
                        "nodes=s"               => \$nodes,
                        "warning=s"             => \$warn_thresh,
                        "critical=s"    => \$crit_thresh,
                        "usage"                 => \$usage,
                        "debug"                 => \$debug,
);

sub main {
        if ($usage || !defined $host || !defined $nodes ) {
                usage();
                exit(3); # Exit with code for UNKNOWN
        }

        my @node_ids = split(",", $nodes);  # Get the comma separated IDs from the option
        my $status = "";

        foreach(@node_ids) { # Loop all IDs given
                if($_ !~ /^\d+$/) {
                        print "Non-numeric node id, " . $nodes . " is not valid \n";
                        exit(3); # Exit with code for UNKNOWN
                }

                $status .= check_mem($_);
        }

        # Give CRITICAL if one or more of the nodes have exceeded threshold
        if($exit_code == 2) {
                print "CRITICAL memory threshold exceeded | $status\n";
        }
        elsif($exit_code == 1) {
                print "WARNING memory threshold exeeded | $status\n";
        }
        else {
                print "OK | $status\n";
        }

        exit($exit_code);
}

# Checks memory usage for the node id passed as argument
# Sets the global is_critical or is_warning if applicable
sub check_mem {
        my ($node) = @_;
        my $data;
        my $index;

        my $command = "$check_command  --ndb-mgmd-host=$host -e \"$node $check_expression\" 2>&1";
        my @ndb_output = `$command`; # Get output from ndb_mgm and STDERR
        if($? != 0) {
                print "Error running ndb command: " . $command . "\n";
                exit(3); # Exit with code for UKNOWN
        }

        # Loop output and grab percent used
        foreach(@ndb_output) {
                if ($_ =~ m/Data/) {
                        ($data) = $_ =~ m/(\d+)%/;
                }
                elsif ($_ =~ m/Index/) {
                        ($index) = $_ =~ m/(\d+)%/;
                }
                elsif ($_ =~ m/not a NDB node/) { # Error code should take care of this. Check nevertheless.
                        print "Unable to get info for node ${node}. Does it exist?";
                        exit(3); # Exit with nagios UNKNOWN code
                }
        }
        # Set warning or critical if thresholds are exceeded
        if($index > $crit_thresh || $data > $crit_thresh) {
                $exit_code = 2;
        }
        elsif(($index > $warn_thresh || $data > $warn_thresh) && $exit_code == 0) {
                $exit_code = 1;
        }

        return "Node_${node}_Data=$data% Node_${node}_Index=$index% ";
}

sub usage {
        print "check_ndb_mem usage:\n";
        print "\t--host \t\tThe ndb manager to connect to\n";
        print "\t--nodes \tThe IDs of the nodes to check, comma separated\n";
        print "\t--warning \tThe percent of usage threshold for warning. Defaults to 70 if not specified\n";
        print "\t--critical \tThe percent of usage threshold for critical. Defaults to 80 if not specified\n";

        return 0;
}

main();
