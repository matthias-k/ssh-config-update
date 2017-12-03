# SSH Config Update

This is a simple tool to automatically update parts of the ssh config based on the reachability of ssh hosts. It's intended usecase is for remote connections that differ depending on which network you are on (e.g. your company/university local network or eduroam or the internet). In these cases you might always just do an `ssh mymachine` and don't care about how exactly to reach this machine. `ssh_config_update` helps you with that by checking the different ssh connections and updating your ssh config with the connection that works right now.

## Setup

* create a `config.yaml` based on `config_example.yaml` that reflects your setup
* `ssh_config_update` is intended to overwrite one config file for each ssh target that you want to update. The `config.yaml` states the file for each target with the `configfile` variable. You need to include these files in your main ssh config `~/.ssh/config` with the `Include` statement:

```name=~/.ssh/config
Include config.d/hnauto

# all other config goes here
```

* run `ssh_config_update` either once with `./ssh_config_update.py update` or keep it running with `./ssh_config_update.py watch`.
* With the `--notify` option you will get desktop notifications via libnotify in case of config updates
