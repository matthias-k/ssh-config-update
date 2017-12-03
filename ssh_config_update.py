#!/usr/bin/env python3

import os
from datetime import datetime, timedelta
import time

from executor.ssh.client import RemoteCommand, RemoteConnectFailed
import yaml
import click


def check_remote(remote, data, timeout=60, verbose=False):
    if verbose:
        print("Checking {} ({}s)...".format(remote, timeout), end=' ', flush=True)
    cmd = RemoteCommand('{}@{}'.format(data['User'], data['Hostname']), '/bin/true', connect_timeout=timeout, port=data['Port'])
    try:
        cmd.start()
        cmd.wait()
    except RemoteConnectFailed:
        print("Failed")
        return False
    print("Sucess")
    return True


def check_remotes(remotes, timeout=None, verbose=False, last_remote=None):
    if timeout is None:
        for timeout in [1, 5, 10, 30, 60]:
            remote = check_remotes(remotes, timeout=timeout, verbose=verbose, last_remote=last_remote)
            if remote:
                return remote
        else:
            return None
    else:
        ordered_remotes = sorted(remotes, key=lambda remote: (remote != last_remote, remote))
        for remote in ordered_remotes:
            if check_remote(remote, remotes[remote], timeout=timeout, verbose=verbose):
                return remote
        return None


def set_remote(data, remote):
    config_file = os.path.expanduser(data['configfile'])
    with open(config_file, 'w') as f:
        f.write('# {}\n'.format(remote))
        f.write('Host {}\n'.format(data['target']))
        _data = data['remotes'][remote]
        f.write('\tUser {}\n'.format(_data['User']))

        for key, value in _data.items():
            f.write('\t{} {}\n'.format(key, value))


def get_remote(data):
    config_file = os.path.expanduser(data['configfile'])
    if not os.path.isfile(config_file):
        return None
    else:
        config = open(config_file, 'r').read()
        lines = config.split('\n', 1)
        if not lines:
            return None
        if not lines[0].startswith('# '):
            return None
        parts = lines[0].split()
        if not len(parts) == 2:
            return None
        return parts[1]


def announce_remote(data, remote):
    import pgi
    pgi.install_as_gi()
    pgi.require_version('Notify', '0.7')
    from gi.repository import Notify
    Notify.init("Network Switcher")
    Hello=Notify.Notification.new("Network change detected", "{} set to {}".format(data['target'], remote), "dialog-information")
    Hello.show()


def update_remote(data):
    last_remote = get_remote(data)
    print("last remote:", last_remote)
    new_remote = check_remotes(data['remotes'], verbose=True, last_remote=last_remote)
    if new_remote and new_remote != last_remote:
        set_remote(data, new_remote)
        announce_remote(data, new_remote)


@click.group()
def cli():
    pass


def _update():
    config = yaml.load(open('config.yaml'))
    for key, data in config['targets'].items():
        if 'target' not in data:
            data['target'] = key
        update_remote(data)

@cli.command(help="Check and update all targets")
def update():
    _update()


@cli.command(help="watch for changes and update")
def watch():
    _update()
    last_update = datetime.utcnow()
    while True:
        if datetime.utcnow() - last_update > timedelta(seconds=60):
            _update()
            last_update = datetime.utcnow()
        time.sleep(1)



if __name__ == '__main__':
    cli()
