# Settings:
#
# znotify_target -- send events to this zmq url
#   default: tcp://localhost:11111

use strict;
use Irssi;
use vars qw($VERSION %IRSSI $CTX $SOCK $STATE);

use JSON;
use ZMQ::LibZMQ3;
use ZMQ::Constants qw/:all/;

$VERSION = "1";

%IRSSI = (
    authors     => 'Lars Kellogg-Stedman',
    contact     => 'lars@oddbit.com',
    name        => 'znotify.pl',
    description => 'Send events to a ZeroMQ broker.',
    license     => 'GNU General Public License',
    url         => 'http://github.com/larsks/znotify',
);

$CTX = zmq_init;
$SOCK = undef;
$STATE = 0;

sub send_event {
	my ($event, $message, $data) = @_;

	zmq_send($SOCK, "irssi." . $event, -1, ZMQ_SNDMORE);
	zmq_send($SOCK, to_json({
		message => $message,
		data => $data,
	}));
}

sub query_created {
    my ($query, $auto) = @_;

    my $qwin   = $query->window();
    my $server = $query->{server};
    my $nick   = $query->{name};
    my $tag    = lc $query->{server_tag};

	send_event("query.created",
		"New query with " . $nick . ".",
		{
			nick => $nick,
			away => $server->{usermode_away},
		});
}

sub message_private {
	my ($server, $msg, $nick, $address) = @_;

	send_event("message.private",
		"Private message from " . $nick . ".",
		{
			nick => $nick,
			message => $msg,
			away => $server->{usermode_away},
		});
}

sub window_item_hilight {
	my ($item) = @_;
	my $server = $item->{server};

	return unless $item->{data_level} == 3;
	
	send_event("window.item.hilight",
		"Hilight in " . $item->{name} . ".",
		{
			name => $item->{name},
			away => $server->{usermode_away},
		});
}

sub cmd_znotify_reconnect {
	my ($data, $server, $item) = @_;
	$SOCK = zmq_socket($CTX, ZMQ_PUB);

	my $target = Irssi::settings_get_str('znotify_target');
	zmq_connect($SOCK, $target);
	Irssi::print("Connected to $target.");

	send_event("znotify.connect",
		"Connected to " . $target . ".",
		{
			target => $target,
			away => $server->{usermode_away},
		});
}

sub cmd_znotify {
	my ($data, $server, $item) = @_;

	if ($data ne '') {
		Irssi::command_runsub ('znotify', $data, $server, $item);
	} else {
		Irssi::print("znotify is " . ( $STATE ? "enabled" : "disabled" ) . ".");
	}
}

sub cmd_znotify_off {
	my ($data, $server, $item) = @_;

	Irssi::signal_remove('query created',   \&query_created);
	Irssi::signal_remove('message private', \&message_private);
	Irssi::signal_remove('window item hilight',  \&window_item_hilight);

	Irssi::print("znotify is disabled");

	send_event("znotify.off",
		'znotify has been disabled.',
		{
			away => $server->{usermode_away},
		});

	$STATE = 0;
}

sub cmd_znotify_on {
	my ($data, $server, $item) = @_;

	Irssi::signal_add('query created',   \&query_created);
	Irssi::signal_add('message private', \&message_private);
	Irssi::signal_add('window item hilight',  \&window_item_hilight);

	Irssi::print("znotify is enabled");

	send_event("znotify.on",
		'znotify has been enabled.',
		{
			away => $server->{usermode_away},
		});

	$STATE = 1;
}

Irssi::settings_add_str('znotify', 'znotify_target', 'tcp://localhost:11111');

Irssi::command_bind('znotify',           \&cmd_znotify);
Irssi::command_bind('znotify on',        \&cmd_znotify_on);
Irssi::command_bind('znotify off',       \&cmd_znotify_off);
Irssi::command_bind('znotify reconnect', \&cmd_znotify_reconnect);

cmd_znotify_reconnect;
cmd_znotify_on;

1;

# vim: ts=4 sw=4
