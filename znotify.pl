# Settings:
#
# znotify_target -- send events to this zmq url
#   default: tcp://localhost:11111

use strict;
use Irssi;
use vars qw($VERSION %IRSSI $CTX $SOCK $STATE);

use MIME::Base64;
use ZeroMQ qw/:all/;

$VERSION = "1";

%IRSSI = (
    authors     => 'Lars Kellogg-Stedman',
    contact     => 'lars@oddbit.com',
    name        => 'znotify.pl',
    description => 'Send events to a ZeroMQ broker.',
    license     => 'GNU General Public License',
    url         => 'http://github.com/larsks/znotify',
);

$CTX = ZeroMQ::Context->new;
$SOCK = undef;
$STATE = 0;

sub query_created {
    my ($query, $auto) = @_;

    my $qwin = $query->window();
    my $serv = $query->{server};
    my $nick = $query->{name};
    my $tag  = lc $query->{server_tag};

	$SOCK->send_as(json => {
		event => "query created",
		message => "New query with " . $nick . ".",
		data => {
			nick => $nick,
		},
	});
}

sub message_private {
	my ($server, $msg, $nick, $address) = @_;

	$SOCK->send_as(json => {
		event => "message private",
		message => "Private message from " . $nick . ".",
		data => {
			nick => $nick,
			message => $msg,
		},
	});
}

sub window_item_hilight {
	my ($item) = @_;

	return unless $item->{data_level} == 3;
	
	$SOCK->send_as(json => {
		event => "window item hilight",
		message => "Hilight in " . $item->{name} . ".",
		data => {
			name => $item->{name},
		},
	});
}

sub cmd_znotify_reconnect {
	$SOCK = $CTX->socket(ZMQ_PUB);

	my $target = Irssi::settings_get_str('znotify_target');
	$SOCK->connect($target);
	Irssi::print("Connected to $target.");

	$SOCK->send_as(json => {
		event => "connect",
		message => "Connected to " . $target . ".",
		data => {
			target => $target,
		},
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
	Irssi::signal_remove('query created',   \&query_created);
	Irssi::signal_remove('message private', \&message_private);
	Irssi::signal_remove('window item hilight',  \&window_item_hilight);

	Irssi::print("znotify is disabled");

	$SOCK->send_as(json=>{
		event => 'znotify off',
		message => 'znotify has been disabled.',
	});

	$STATE = 0;
}

sub cmd_znotify_on {
	Irssi::signal_add('query created',   \&query_created);
	Irssi::signal_add('message private', \&message_private);
	Irssi::signal_add('window item hilight',  \&window_item_hilight);

	Irssi::print("znotify is enabled");

	$SOCK->send_as(json=>{
		event => 'znotify on',
		message => 'znotify has been enabled.',
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

# vim: ts=4
