# Home Assistant Add-on: Resticprofile Backup

## How to Use

After installing the add-on, you can start it immediately. On the first run, a
new password for restic backups will be generated and saved in `password.txt`,
along with an example configuration file, `profiles.yaml.example`. Both files
are located in `/addon_configs/xxx_resticprofile-backup/`.

After these files are created, the add-on will stop automatically because no
configuration exists yet. This is expected behavior.

**Important:** Back up the password to a safe place! This password is
**REQUIRED** to restore your backups. If you lose it, you will **PERMANENTLY**
lose access to all your backups. Store it securely (e.g., in a password
manager), or ensure that Add-on configs are included in your default Home
Assistant backup.

### Creating a resticprofile Configuration

After the initial start, copy the contents of `profiles.yaml.example` to a new
file named `profiles.yaml` and modify to your own needs. Alternatively, you can
create your own configuration from scratch. After every change to the config
file, the add-on **needs to be restarted** in order to pick up the new
configuration!

For details on creating or modifying the configuration, refer to the
[resticprofile documentation](https://creativeprojects.github.io/resticprofile/configuration/index.html).

For every repository added in the `profiles.yaml` file, the add-on will also
check if it is initialized and automatically call `restic init` if not.

The following Home Assistant folders are mounted (read-only) inside the add-on
container:

- `/addon_configs`
- `/addons`
- `/backup`
- `/data`
- `/homeassistant`
- `/media`
- `/share`
- `/ssl`

### Mounting Local Disks

To mount local disks (such as USB drives or secondary internal drives), use the
`localdisks` configuration option. This option accepts a comma-separated list of
identifiers, which can be device names (e.g., `sda1`), UUIDs (e.g.,
`0000-0000`), or filesystem labels (e.g., `mylabel`).

Example:

```yaml
localdisks: sda1,0000-0000, mylabel
```

When the add-on starts, it will attempt to mount each specified disk. The add-on
logs will display all available disks that can be mounted, as well as all
supported filesystems at start. This information can help you identify the
correct identifiers to use in your configuration.

Ensure that the disks you want to mount are connected and recognized by the host
system before starting the add-on.

### Mounting SMB Shares

To mount SMB shares for your backups, configure them in the add-on settings.

Example:

```yaml
- host: //192.168.0.1/Backup/
  local: /mnt/my-nas
  username: myusername
  password: secretpassword
```

#### host (required)

The network address of the SMB share to connect to.

#### local (required)

The mount point for the SMB share inside the add-on. This folder will be created
when the add-on starts.

It is recommended to mount shares inside the `/mnt` folder, which exists and is
writable in the add-on container, to avoid conflicts.

#### username (optional)

Username for accessing the SMB share.

#### password (optional)

Password for accessing the SMB share.

#### smb_version (optional)

Specify the SMB protocol version to use when connecting. By default, the client
will attempt to negotiate the best available protocol version.

For available options, see the
[cifs-utils manpage](https://manpages.debian.org/unstable/cifs-utils/mount.cifs.8.en.html#vers=arg).

Only set this if you encounter compatibility or performance issues.
