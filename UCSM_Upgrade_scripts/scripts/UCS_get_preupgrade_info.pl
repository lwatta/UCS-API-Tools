#!/usr/bin/perl

use Expect;
$| = 1;

use strict;
# Set advanced BIOS options, including enabled optionRom, set GEN2 link speed,
# and also set boot order.
# For ceph C220,  slot 1 (broadcom card)  and slot 2 (LSI card).
# 

my $cimc = shift;
my $user = shift;
my $pass = shift;

my $db;

my @cmds = (
   "show cluster state",
   "connect nxos A",
   "show int brief | grep -v down | wc -l",
   "show platform fwm info hw-stm | grep '1.' | wc -l",
   "exit",
   "connect nxos B",
   "show int brief | grep -v down | wc -l",
   "show platform fwm info hw-stm | grep '1.' | wc -l",
   "exit"
);

sub error {
    my($msg) = $_[0];

    $db->hard_close() if $db;
    print STDOUT $msg,"\n";

    exit 99;
}

print "Connecting to $cimc\n";

my $cmd = qq{/usr/bin/ssh -oStrictHostKeyChecking=no $user\@$cimc};
($db = Expect->spawn($cmd)) || error("Couldn't spawn $cmd");
$db->max_accum(4096);

my $which = expect(30, "Password:");
print "password prompt \n";
error "did not get password prompt" if $which != 1;
print $db $pass, "\n";

my $which = expect(240, "# ");
print "prompt \n";
error "did not get prompt" if $which != 1;

my $need_reboot;
my @copy_of_cmds = @cmds;
while (my $cmd = shift @copy_of_cmds) {
    print " (sending $cmd) ";
    print $db "$cmd\n";
    my $which = expect(240, "# ", "reboot the system?[y|N]", "continue?[y|N]");
    if ($which == 1) {
	# ok
    } elsif ($which == 2) {
	#print $db "y\n";
	#$which = expect(240, "has been initiated");
	#error "reboot not initiated" if $which != 1;
	#if (@copy_of_cmds && $copy_of_cmds[0] ne "exit") {		# Remaining commands.
	#    die "required reboot\n";
	#} else {
	#    exit;
	#}
	push @copy_of_cmds, "scope chassis", "power cycle" unless $need_reboot++;
	print $db "N\n";
	my $which = expect(240, "# ");
	error "did not get prompt" if $which != 1;
    } elsif ($which == 3) {
	print $db "y\n";
	my $which = expect(240, "# ");
	error "did not get prompt" if $which != 1;
    } else {
	error "did not get prompt";
    }
}

$db->hard_close();

sub expect {
    #
    # Just a nice little interface to the real expect function so that the
    # interaction section above is cleaner and more robust.
    #
    my($timeout, @possibilities) = @_;
    my($mPos, $err, $mStr, $mBefore, $mAfter);

    ($mPos, $err, $mStr, $mBefore, $mAfter) 
	= $db->expect($timeout, @possibilities);

    if ($err) {
	#
	# Expect.pm returns an error with "1:" prefixed in the event of a
	# timeout.
	#
	if ($err =~ /^1:/) {
	    error("Time out. "
		. ($mBefore !~ /^\s+$/ ? "Previous output:\n" . $mBefore
		: "No previous output"));
	}
    } else {
	return $mPos;
    }
}
