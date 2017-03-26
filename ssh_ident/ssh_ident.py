#!/usr/bin/env python
# vim: tabstop=2 shiftwidth=2 expandtab
"""Start and use ssh-agent and load identities as necessary.

Use this script to start ssh-agents and load ssh keys on demand,
when they are first needed.

All you have to do is modify your .bashrc to have:

  alias ssh='/path/to/ssh-ident'

or add a link to ssh-ident from a directory in your PATH, for example:

  ln -s /path/to/ssh-ident ~/bin/ssh

If you use scp or rsync regularly, you should add a few more lines described
below.

In any case, ssh-ident:

- will create an ssh-agent and load the keys you need the first time you
  actually need them, once. No matter how many terminals, ssh or login
  sessions you have, no matter if your home is shared via NFS.

- can prepare and use a different agent and different set of keys depending
  on the host you are connecting to, or the directory you are using ssh
  from.
  This allows for isolating keys when using agent forwarding with different
  sites (eg, university, work, home, secret evil internet identity, ...).
  It also allows to use multiple accounts on sites like github, unfuddle
  and gitorious easily.

- allows to specify different options for each set of keys. For example, you
  can provide a -t 60 to keep keys loaded for at most 60 seconds. Or -c to
  always ask for confirmation before using a key.


Installation
============

All you need to run ssh-ident is a standard installation of python >= 2.6,
python > 3 is supported.

If your system has wget and are impatient to use it, you can install
ssh-ident with two simple commands:

   mkdir -p ~/bin; wget -O ~/bin/ssh goo.gl/MoJuKB; chmod 0755 ~/bin/ssh

   echo 'export PATH=~/bin:$PATH' >> ~/.bashrc

Logout, login, and done. SSH should now invoke ssh-ident instead of the
standard ssh.


Alternatives
============

In .bashrc, I have:

  alias ssh=/home/ccontavalli/scripts/ssh-ident

all I have to do now is logout, login and then:

  $ ssh somewhere

ssh-ident will be called instead of ssh, and it will:
- check if an agent is running. If not, it will start one.
- try to load all the keys in ~/.ssh, if not loaded.

If I now ssh again, or somewhere else, ssh-ident will reuse the same agent
and the same keys, if valid.


About scp, rsync, and friends
=============================

scp, rsync, and most similar tools internally invoke ssh. If you don't tell
them to use ssh-ident instead, key loading won't work. There are a few ways
to solve the problem:

1) Rename 'ssh-ident' to 'ssh' or create a symlink 'ssh' pointing to
   ssh-ident in a directory in your PATH before /usr/bin or /bin, similarly
   to what was described previously. For example, add to your .bashrc:

    export PATH="~/bin:$PATH"

   And run:

    ln -s /path/to/ssh-ident ~/bin/ssh

   Make sure `echo $PATH` shows '~/bin' *before* '/usr/bin' or '/bin'. You
   can verify this is working as expected with `which ssh`, which should
   show ~/bin/ssh.

   This works for rsync and git, among others, but not for scp and sftp, as
   these do not look for ssh in your PATH but use a hard-coded path to the
   binary.

   If you want to use ssh-ident with scp or sftp,  you can simply create
   symlinks for them as well:

    ln -s /path/to/ssh-ident ~/bin/scp
    ln -s /path/to/ssh-ident ~/bin/sftp

2) Add a few more aliases in your .bashrc file, for example:

    alias scp='BINARY_SSH=scp /path/to/ssh-ident'
    alias rsync='BINARY_SSH=rsync /path/to/ssh-ident'
    ...

   The first alias will make the 'scp' command invoke 'ssh-ident' instead,
   but tell 'ssh-ident' to invoke 'scp' instead of the plain 'ssh' command
   after loading the necessary agents and keys.

   Note that aliases don't work from scripts - if you have any script that
   you expect to use with ssh-ident, you may prefer method 1), or you will
   need to update the script accordingly.

3) Use command specific methods to force them to use ssh-ident instead of
   ssh, for example:

    rsync -e '/path/to/ssh-ident' ...
    scp -S '/path/to/ssh-ident' ...

4) Replace the real ssh on the system with ssh-ident, and set the 
   BINARY_SSH configuration parameter to the original value.

   On Debian based system, you can make this change in a way that
   will survive automated upgrades and audits by running:

     dpkg-divert --divert /usr/bin/ssh.ssh-ident --rename /usr/bin/ssh
   
   After which, you will need to use:

     BINARY_SSH="/usr/bin/ssh.ssh-ident"


Config file with multiple identities
====================================

To have multiple identities, all I have to do is:

1) create a ~/.ssh-ident file. In this file, I need to tell ssh-ident which
   identities to use and when. The file should look something like:

  # Specifies which identity to use depending on the path I'm running ssh
  # from.
  # For example: ("mod-xslt", "personal") means that for any path that
  # contains the word "mod-xslt", the "personal" identity should be used.
  # This is optional - don't include any MATCH_PATH if you don't need it.
  MATCH_PATH = [
    # (directory pattern, identity)
    (r"mod-xslt", "personal"),
    (r"ssh-ident", "personal"),
    (r"opt/work", "work"),
    (r"opt/private", "secret"),
  ]

  # If any of the ssh arguments have 'cweb' in it, the 'personal' identity
  # has to be used. For example: "ssh myhost.cweb.com" will have cweb in
  # argv, and the "personal" identity will be used.
  # This is optional - don't include any MATCH_ARGV if you don't
  # need it.
  MATCH_ARGV = [
    (r"cweb", "personal"),
    (r"corp", "work"),
  ]

  # Note that if no match is found, the DEFAULT_IDENTITY is used. This is
  # generally your loginname, no need to change it.
  # This is optional - don't include any DEFAULT_IDENTITY if you don't
  # need it.
  # DEFAULT_IDENTITY = "foo"

  # This is optional - don't include any SSH_ADD_OPTIONS if you don't
  # need it.
  SSH_ADD_OPTIONS = {
    # Regardless, ask for confirmation before using any of the
    # work keys.
    "work": "-c",
    # Forget about secret keys after ten minutes. ssh-ident will
    # automatically ask you your passphrase again if they are needed.
    "secret": "-t 600",
  }

  # This is optional - dont' include any SSH_OPTIONS if you don't
  # need it.
  # Otherwise, provides options to be passed to 'ssh' for specific
  # identities.
  SSH_OPTIONS = {
    # Disable forwarding of the agent, but enable X forwarding,
    # when using the work profile.
    "work": "-Xa",

    # Always forward the agent when using the secret identity.
    "secret": "-A",
  }

  # Options to pass to ssh by default.
  # If you don't specify anything, UserRoaming=no is passed, due
  # to CVE-2016-0777. Leave it empty to disable this.
  SSH_DEFAULT_OPTIONS = "-oUseRoaming=no"

  # Which options to use by default if no match with SSH_ADD_OPTIONS
  # was found. Note that ssh-ident hard codes -t 7200 to prevent your
  # keys from remaining in memory for too long.
  SSH_ADD_DEFAULT_OPTIONS = "-t 7200"

  # Output verbosity
  # valid values are: LOG_ERROR, LOG_WARN, LOG_INFO, LOG_DEBUG
  VERBOSITY = LOG_INFO

2) Create the directory where all the identities and agents
   will be kept:

    $ mkdir -p ~/.ssh/identities; chmod u=rwX,go= -R ~/.ssh

3) Create a directory for each identity, for example:

    $ mkdir -p ~/.ssh/identities/personal
    $ mkdir -p ~/.ssh/identities/work
    $ mkdir -p ~/.ssh/identities/secret

4) Generate (or copy) keys for those identities:

    # Default keys are for my personal account
    $ cp ~/.ssh/id_rsa* ~/.ssh/identities/personal

    # Generate keys to be used for work only, rsa
    $ ssh-keygen -t rsa -b 4096 -f ~/.ssh/identities/work/id_rsa

    ...


Now if I run:

  $ ssh corp.mywemployer.com

ssh-ident will be invoked instead, and:

  1) check ssh argv, determine that the "work" identity has to be used.
  2) look in ~/.ssh/agents, for a "work" agent loaded. If there is no
     agent, it will prepare one.
  3) look in ~/.ssh/identities/work/* for a list of keys to load for this
     identity. It will try to load any key that is not already loaded in
     the agent.
  4) finally run ssh with the environment setup such that it will have
     access only to the agent for the identity work, and the corresponding
     keys.

Note that ssh-ident needs to access both your private and public keys. Note
also that it identifies public keys by the .pub extension. All files in your
identities subdirectories will be considered keys.

If you want to only load keys that have "key" in the name, you can add
to your .ssh-ident:

      PATTERN_KEYS = "key"

The default is:

      PATTERN_KEYS = r"/(id_.*|identity.*|ssh[0-9]-.*)"

You can also redefine:

      DIR_IDENTITIES = "$HOME/.ssh/identities"
      DIR_AGENTS = "$HOME/.ssh/agents"

To point somewhere else if you so desire.


BUILDING A DEBIAN PACKAGE
=========================

If you need to use ssh-ident on a debian / ubuntu / or any other
derivate, you can now build debian packages.

  1. Make sure you have devscripts installed:

    sudo apt-get install devscripts debhelper

  2. Download ssh-ident in a directory of your choice (ssh-ident)

    git clone https://github.com/ccontavalli/ssh-ident.git ssh-ident

  3. Build the .deb package:

    cd ssh-ident && debuild -us -uc

  4. Profit:

    cd ..; dpkg -i ssh-ident*.deb


CREDITS
=======

- Carlo Contavalli, http://www.github.com/ccontavalli, main author.
- Hubert depesz Lubaczewski, http://www.github.com/despez, support
  for using environment variables for configuration.
- Flip Hess, http://www.github.com/fliphess, support for building
  a .deb out of ssh-ident.
- Terrel Shumway, https://www.github.com/scholarly, port to python3.
- black2754, https://www.github.com/black2754, vim modeline, support
  for verbosity settings, and BatchMode passing.
- Michael Heap, https://www.github.com/mheap, support for per
  identities config files.
- Carl Drougge, https://www.github.com/drougge, CVE-2016-0777 fix,
  fix for per user config files, and use /bin/env instead of python
  path.
"""

from __future__ import print_function

import collections
import distutils.spawn
import errno
import fcntl
import getpass
import glob
import os
import re
import socket
import subprocess
import sys
import termios
import textwrap

# constants so noone has deal with cryptic numbers
LOG_CONSTANTS = {"LOG_ERROR": 1, "LOG_WARN": 2, "LOG_INFO": 3, "LOG_DEBUG": 4}
# load them directly into the global scope, for easy use
# not exactly pretty...
globals().update(LOG_CONSTANTS)


def ShouldPrint(config, loglevel):
  """Returns true if a message by the specified loglevel should be printed."""
  # determine the current output verbosity
  verbosity = config.Get("VERBOSITY")

  # verbosity may be a string, e.g. 'LOG_INFO'
  # this happens when it comes from the OS env, but also if quotes are
  # used in the config file
  if isinstance(verbosity, str):
    if verbosity in LOG_CONSTANTS:
      # resolve the loglevel, e.g. 'LOG_INFO' -> 3
      verbosity = LOG_CONSTANTS[verbosity]
    else:
      # the string may also be a number, e.g. '3' -> 3
      verbosity = int(verbosity)
  if loglevel <= verbosity:
    return True
  return False


class SshIdentPrint(object):
  """Wrapper around python's print function."""

  def __init__(self, config):
    """
      config: object implementing the Config interface, allows access to
          the user configuration parameters.

    Attributes:
      config: same as above.
      python_print: python's print function (hopefully)

    Parameters:
      SSH_BATCH_MODE: used to check if messages should be printed or not
      VERBOSITY: used to check if messages should be printed or not
    """
    self.config = config
    self.python_print = print

  def write(self, *args, **kwargs):
    """Passes all parameters to python's print,
    unless output is disabled by the configuration.
    The interface is compatible with python's print, but supports the
    optional parameter 'loglevel' in addition."""
    if self.config.Get("SSH_BATCH_MODE"):
      # no output in BatchMode
      return

    # determine the loglevel of this message
    if "loglevel" in kwargs:
      loglevel = kwargs["loglevel"]
      # make sure not to pass the loglevel parameter to print
      del kwargs["loglevel"]
    else:
      # if the loglevel is not given, default to INFO
      loglevel = LOG_INFO

    if ShouldPrint(self.config, loglevel):
      self.python_print(*args, **kwargs)

  __call__ = write


class Config(object):
  """Holds and loads users configurations."""

  defaults = {
      # Where to find the per-user configuration.
      "FILE_USER_CONFIG": "$HOME/.ssh-ident",

      # Where to find all the identities for the user.
      "DIR_IDENTITIES": "$HOME/.ssh/identities",
      # Where to keep the information about each running agent.
      "DIR_AGENTS": "$HOME/.ssh/agents",

      # How to identify key files in the identities directory.
      "PATTERN_KEYS": r"/(id_.*|identity.*|ssh[0-9]-.*)",

      # How to identify ssh config files.
      "PATTERN_CONFIG": r"/config$",

      # Dictionary with identity as a key, automatically adds
      # the specified options to the ssh command run.
      "SSH_OPTIONS": {},
      # Additional options to append to ssh by default.
      "SSH_DEFAULT_OPTIONS": "-oUseRoaming=no",

      # Complete path of full ssh binary to use. If not set, ssh-ident will
      # try to find the correct binary in PATH.
      "BINARY_SSH": None,
      "BINARY_DIR": None,

      # Which identity to use by default if we cannot tell from
      # the current working directory and/or argv.
      "DEFAULT_IDENTITY": "$USER",

      # Those should really be overridden by the user. Look
      # at the documentation for more details.
      "MATCH_PATH": [],
      "MATCH_ARGV": [],

      # Dictionary with identity as a key, allows to specify
      # per identity options when using ssh-add.
      "SSH_ADD_OPTIONS": {},
      # ssh-add default options. By default, don't keep a key longer
      # than 2 hours.
      "SSH_ADD_DEFAULT_OPTIONS": "-t 7200",

      # Like BatchMode in ssh, see man 5 ssh_config.
      # In BatchMode ssh-ident will not print any output and not ask for
      # any passphrases.
      "SSH_BATCH_MODE": False,

      # Output verbosity
      # valid values are: LOG_ERROR, LOG_WARN, LOG_INFO, LOG_DEBUG
      # use 0 to disable ALL output (not recommended!)
      "VERBOSITY": LOG_INFO,
  }

  def __init__(self):
    self.values = {}

  def Load(self):
    """Load configurations from the default user file."""
    path = self.Get("FILE_USER_CONFIG")
    variables = {}
    try:
      exec(compile(open(path).read(), path, 'exec'), LOG_CONSTANTS, variables)
    except IOError:
      return self
    self.values = variables
    return self

  @staticmethod
  def Expand(value):
    """Expand environment variables or ~ in string parameters."""
    if isinstance(value, str):
      return os.path.expanduser(os.path.expandvars(value))
    return value

  def Get(self, parameter):
    """Returns the value of a parameter, or causes the script to exit."""
    if parameter in os.environ:
      return self.Expand(os.environ[parameter])
    if parameter in self.values:
      return self.Expand(self.values[parameter])
    if parameter in self.defaults:
      return self.Expand(self.defaults[parameter])

    print(
        "Parameter '{0}' needs to be defined in "
        "config file or defaults".format(parameter), file=sys.stderr,
        loglevel=LOG_ERROR)
    sys.exit(2)

  def Set(self, parameter, value):
    """Sets configuration option parameter to value."""
    self.values[parameter] = value

def FindIdentityInList(elements, identities):
  """Matches a list of identities to a list of elements.

  Args:
    elements: iterable of strings, arbitrary strings to match on.
    identities: iterable of (string, string), with first string
      being a regular expression, the second string being an identity.

  Returns:
    The identity specified in identities for the first regular expression
    matching the first element in elements.
  """
  for element in elements:
    for regex, identity in identities:
      if re.search(regex, element):
        return identity
  return None

def FindIdentity(argv, config):
  """Returns the identity to use based on current directory or argv.

  Args:
    argv: iterable of string, argv passed to this program.
    config: instance of an object implementing the same interface as
        the Config class.

  Returns:
    string, the name of the identity to use.
  """
  paths = set([os.getcwd(), os.path.abspath(os.getcwd()), os.path.normpath(os.getcwd())])
  return (
      FindIdentityInList(argv, config.Get("MATCH_ARGV")) or
      FindIdentityInList(paths, config.Get("MATCH_PATH")) or
      config.Get("DEFAULT_IDENTITY"))

def FindKeys(identity, config):
  """Finds all the private and public keys associated with an identity.

  Args:
    identity: string, name of the identity to load strings of.
    config: object implementing the Config interface, providing configurations
        for the user.

  Returns:
    dict, {"key name": {"pub": "/path/to/public/key", "priv":
    "/path/to/private/key"}}, for each key found, the path of the public
    key and private key. The key name is just a string representing the
    key. Note that for a given key, it is not guaranteed that both the
    public and private key will be found.
    The return value is affected by DIR_IDENTITIES and PATTERN_KEYS
    configuration parameters.
  """
  directories = [os.path.join(config.Get("DIR_IDENTITIES"), identity)]
  if identity == getpass.getuser():
    directories.append(os.path.expanduser("~/.ssh"))

  pattern = re.compile(config.Get("PATTERN_KEYS"))
  found = collections.defaultdict(dict)
  for directory in directories:
    try:
      keyfiles = os.listdir(directory)
    except OSError as e:
      if e.errno == errno.ENOENT:
        continue
      raise

    for key in keyfiles:
      key = os.path.join(directory, key)
      if not os.path.isfile(key):
        continue
      if not pattern.search(key):
        continue

      kinds = (
          ("private", "priv"),
          ("public", "pub"),
          (".pub", "pub"),
          ("", "priv"),
      )
      for match, kind in kinds:
        if match in key:
          found[key.replace(match, "")][kind] = key

  if not found:
    print("Warning: no keys found for identity {0} in:".format(identity),
        file=sys.stderr,
        loglevel=LOG_WARN)
    print(directories, file=sys.stderr, loglevel=LOG_WARN)

  return found


def FindSSHConfig(identity, config):
  """Finds a config file if there's one associated with an identity

  Args:
    identity: string, name of the identity to load strings of.
    config: object implementing the Config interface, providing configurations
        for the user.

  Returns:
    string, the configuration file to use
  """
  directories = [os.path.join(config.Get("DIR_IDENTITIES"), identity)]

  pattern = re.compile(config.Get("PATTERN_CONFIG"))
  sshconfigs = collections.defaultdict(dict)
  for directory in directories:
    try:
      sshconfigs = os.listdir(directory)
    except OSError as e:
      if e.errno == errno.ENOENT:
        continue
      raise

    for sshconfig in sshconfigs:
      sshconfig = os.path.join(directory, sshconfig)
      if os.path.isfile(sshconfig) and pattern.search(sshconfig):
        return sshconfig

  return False


def GetSessionTty():
  """Returns a file descriptor for the session TTY, or None.

  In *nix systems, each process is tied to one session. Each
  session can be tied (or not) to a terminal, "/dev/tty".

  Additionally, when a command is run, its stdin or stdout can
  be any file descriptor, including one that represent a tty.

  So for example:

    ./test.sh < /dev/null > /dev/null

  will have stdin and stdout tied to /dev/null - but does not
  tell us anything about the session having a /dev/tty associated
  or not.

  For example, running 

    ssh -t user@remotehost './test.sh < /dev/null > /dev/null'

  have a tty associated, while the same command without -t will not.

  When ssh is invoked by tools like git or rsyn, its stdin and stdout
  is often tied to a file descriptor which is not a terminal, has
  the tool wants to provide the input and process the output.

  ssh-ident internally has to invoke ssh-add, which needs to know if
  it has any terminal it can use at all.

  This function returns an open file if the session has an usable terminal,
  None otherwise.
  """
  try:
    fd = open("/dev/tty", "r")
    fcntl.ioctl(fd, termios.TIOCGPGRP, "  ")
  except IOError:
    return None
  return fd


class AgentManager(object):
  """Manages the ssh-agent for one identity."""

  def __init__(self, identity, sshconfig, config):
    """Initializes an AgentManager object.

    Args:
      identity: string, identity the ssh-agent managed by this instance of
          an AgentManager will control.
      config: object implementing the Config interface, allows access to
          the user configuration parameters.

    Attributes:
      identity: same as above.
      config: same as above.
      agents_path: directory where the config of all agents is kept.
      agent_file: the config of the agent corresponding to this identity.

    Parameters:
      DIR_AGENTS: used to compute agents_path.
      BINARY_SSH: path to the ssh binary.
    """
    self.identity = identity
    self.config = config
    self.ssh_config = sshconfig
    self.agents_path = os.path.abspath(config.Get("DIR_AGENTS"))
    self.agent_file = self.GetAgentFile(self.agents_path, self.identity)

  def LoadUnloadedKeys(self, keys):
    """Loads all the keys specified that are not loaded.

    Args:
      keys: dict as returned by FindKeys.
    """
    toload = self.FindUnloadedKeys(keys)
    if toload:
      print("Loading keys:\n    {0}".format( "\n    ".join(toload)),
          file=sys.stderr, loglevel=LOG_INFO)
      self.LoadKeyFiles(toload)
    else:
      print("All keys already loaded", file=sys.stderr, loglevel=LOG_INFO)

  def FindUnloadedKeys(self, keys):
    """Determines which keys have not been loaded yet.

    Args:
      keys: dict as returned by FindKeys.

    Returns:
      iterable of strings, paths to private key files to load.
    """
    loaded = set(self.GetLoadedKeys())
    toload = set()
    for key, config in keys.items():
      if "pub" not in config:
        continue
      if "priv" not in config:
        continue

      fingerprint = self.GetPublicKeyFingerprint(config["pub"])
      if fingerprint in loaded:
        continue

      toload.add(config["priv"])
    return toload

  def LoadKeyFiles(self, keys):
    """Load all specified keys.

    Args:
      keys: iterable of strings, each string a path to a key to load.
    """
    keys = " ".join(keys)
    options = self.config.Get("SSH_ADD_OPTIONS").get(
        self.identity, self.config.Get("SSH_ADD_DEFAULT_OPTIONS"))
    console = GetSessionTty()
    self.RunShellCommandInAgent(
        self.agent_file, "ssh-add {0} {1}".format(options, keys),
        stdout=console, stdin=console)

  def GetLoadedKeys(self):
    """Returns an iterable of strings, each the fingerprint of a loaded key."""
    retval, stdout = self.RunShellCommandInAgent(self.agent_file, "ssh-add -l")
    if retval != 0:
      return []

    fingerprints = []
    for line in stdout.decode("utf-8").split("\n"):
      try:
        _, fingerprint, _ = line.split(" ", 2)
        fingerprints.append(fingerprint)
      except ValueError:
        continue
    return fingerprints

  @staticmethod
  def GetPublicKeyFingerprint(key):
    """Returns the fingerprint of a public key as a string."""
    retval, stdout = AgentManager.RunShellCommand(
        "ssh-keygen -l -f {0} |tr -s ' '".format(key))
    if retval:
      return None

    try:
      _, fingerprint, _ = stdout.decode("utf-8").split(" ", 2)
    except ValueError:
      return None
    return fingerprint

  @staticmethod
  def GetAgentFile(path, identity):
    """Returns the path to an agent config file.

    Args:
      path: string, the path where agent config files are kept.
      identity: string, identity for which to load the agent.

    Returns:
      string, path to the agent file.
    """
    # Create the paths, if they do not exist yet.
    try:
      os.makedirs(path, 0o700)
    except OSError as e:
      if e.errno != errno.EEXIST:
        raise OSError(
            "Cannot create agents directory, try manually with "
            "'mkdir -p {0}'".format(path))

    # Use the hostname as part of the path just in case this is on NFS.
    agentfile = os.path.join(
        path, "agent-{0}-{1}".format(identity, socket.gethostname()))
    if os.access(agentfile, os.R_OK) and AgentManager.IsAgentFileValid(agentfile):
      print("Agent for identity {0} ready".format(identity), file=sys.stderr,
          loglevel=LOG_DEBUG)
      return agentfile

    print("Preparing new agent for identity {0}".format(identity), file=sys.stderr,
        loglevel=LOG_DEBUG)
    retval = subprocess.call(
        ["/usr/bin/env", "-i", "/bin/sh", "-c", "ssh-agent > {0}".format(agentfile)])
    return agentfile

  @staticmethod
  def IsAgentFileValid(agentfile):
    """Returns true if the specified agentfile refers to a running agent."""
    retval, output = AgentManager.RunShellCommandInAgent(
        agentfile, "ssh-add -l >/dev/null 2>/dev/null")
    if retval & 0xff not in [0, 1]:
      print("Agent in {0} not running".format(agentfile), file=sys.stderr,
          loglevel=LOG_DEBUG)
      return False
    return True

  @staticmethod
  def RunShellCommand(command):
    """Runs a shell command, returns (status, stdout), (int, string)."""
    command = ["/bin/sh", "-c", command]
    process = subprocess.Popen(command, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return process.wait(), stdout

  @staticmethod
  def RunShellCommandInAgent(agentfile, command, stdin=None, stdout=subprocess.PIPE):
    """Runs a shell command with an agent configured in the environment."""
    command = ["/bin/sh", "-c",
               ". {0} >/dev/null 2>/dev/null; {1}".format(agentfile, command)]
    process = subprocess.Popen(command, stdin=stdin, stdout=stdout)
    stdout, stderr = process.communicate()
    return process.wait(), stdout

  @staticmethod
  def EscapeShellArguments(argv):
    """Escapes all arguments to the shell, returns a string."""
    escaped = []
    for arg in argv:
      escaped.append("'{0}'".format(arg.replace("'", "'\"'\"'")))
    return " ".join(escaped)

  def GetShellArgs(self):
    """Returns the flags to be passed to the shell to run a command."""
    shell_args = "-c"
    if ShouldPrint(self.config, LOG_DEBUG):
      shell_args = "-xc"
    return shell_args

  def RunSSH(self, argv):
    """Execs ssh with the specified arguments."""
    additional_flags = self.config.Get("SSH_OPTIONS").get(
        self.identity, self.config.Get("SSH_DEFAULT_OPTIONS"))
    if (self.ssh_config):
      additional_flags += " -F {0}".format(self.ssh_config)

    command = [
        "/bin/sh", self.GetShellArgs(),
        ". {0} >/dev/null 2>/dev/null; exec {1} {2} {3}".format(
            self.agent_file, self.config.Get("BINARY_SSH"),
            additional_flags, self.EscapeShellArguments(argv))]
    os.execv("/bin/sh", command)

def AutodetectBinary(argv, config):
  """Detects the correct binary to run and sets BINARY_SSH accordingly,
  if it is not already set."""
  # If BINARY_SSH is set by the user, respect that and do nothing.
  if config.Get("BINARY_SSH"):
    print("Will run '{0}' as ssh binary - set by user via BINARY_SSH"
          .format(config.Get("BINARY_SSH")), loglevel=LOG_DEBUG)
    return

  # If BINARY_DIR is set, look for the binary in this directory.
  runtime_name = argv[0]
  if config.Get("BINARY_DIR"):
    binary_name = os.path.basename(runtime_name)
    binary_path = os.path.join(config.Get("BINARY_DIR"), binary_name)
    if not os.path.isfile(binary_path) or not os.access(binary_path, os.X_OK):
      binary_path = os.path.join(config.Get("BINARY_DIR"), "ssh")

    config.Set("BINARY_SSH", binary_path)
    print("Will run '{0}' as ssh binary - detected based on BINARY_DIR"
          .format(config.Get("BINARY_SSH")), loglevel=LOG_DEBUG)
    return

  # argv[0] could be pretty much anything the caller decides to set
  # it to: an absolute path, a relative path (common in older systems),
  # or even something entirely unrelated.
  #
  # Similar is true for __file__, which might even represent a location
  # that is entirely unrelated to how ssh-ident was found.
  #
  # Consider also that there might be symlinks / hard links involved.
  #
  # The logic here is pretty straightforward:
  # - Try to eliminate the path of ssh-ident from PATH.
  # - Search for a binary with the same name of ssh-ident to run.
  # 
  # If this fails, we may end up in some sort of loop, where ssh-ident
  # tries to run itself. This should normally be detected later on,
  # where the code checks for the next binary to run.
  #
  # Note also that users may not be relying on having ssh-ident in the
  # PATH at all - for example, with "rsync -e '/path/to/ssh-ident' ..."
  binary_name = os.path.basename(runtime_name)
  ssh_ident_path = ""
  if not os.path.dirname(runtime_name):
    message = textwrap.dedent("""\
    argv[0] ("{0}") is a relative path. This means that ssh-ident does
    not know its own directory, and can't exclude it from searching it
    in $PATH:

      PATH="{1}"

    This may result in a loop, with 'ssh-ident' trying to run itself.
    It is recommended that you set BINARY_SSH, BINARY_DIR, or run
    ssh-ident differently to prevent this problem.""")
    print(message.format(runtime_name, os.environ['PATH']),
          loglevel=LOG_INFO)
  else:
    ssh_ident_path = os.path.abspath(os.path.dirname(runtime_name))

  # Remove the path containing the ssh-ident symlink (or whatever) from
  # the search path, so we do not cause an infinite loop.
  # Note that:
  #  - paths in PATH may be not-normalized, example: "/usr/bin/../foo",
  #    or "/opt/scripts///". Normalize them before comparison.
  #  - paths in PATH may be repeated multiple times. We have to exclude
  #    all instances of the ssh-ident path.
  normalized_path = [
      os.path.normpath(p) for p in os.environ['PATH'].split(os.pathsep)]
  search_path = os.pathsep.join([
      p for p in normalized_path if p != ssh_ident_path])

  # Find an executable with the desired name.
  binary_path = distutils.spawn.find_executable(binary_name, search_path)
  if not binary_path:
    # Nothing found. Try to find something named 'ssh'.
    binary_path = distutils.spawn.find_executable('ssh')

  if binary_path:
    config.Set("BINARY_SSH", binary_path)
    print("Will run '{0}' as ssh binary - detected from argv[0] and $PATH"
          .format(config.Get("BINARY_SSH")), loglevel=LOG_DEBUG)
  else:
    message = textwrap.dedent("""\
    ssh-ident was invoked in place of the binary {0} (determined from argv[0]).
    Neither this binary nor 'ssh' could be found in $PATH.

      PATH="{1}" 

    You need to adjust your setup for ssh-ident to work: consider setting
    BINARY_SSH or BINARY_DIR in your config, or running ssh-ident some
    other way.""")
    print(message.format(argv[0], os.environ['PATH']), loglevel=LOG_ERROR)
    sys.exit(255)

def ParseCommandLine(argv, config):
  """Parses the command line parameters in argv
  and modifies config accordingly."""
  # This function may need a lot of refactoring if it is ever used for more
  # than checking for BatchMode for OpenSSH...
  binary = os.path.basename(config.Get("BINARY_SSH"))
  if binary == 'ssh' or binary == 'scp':
    # OpenSSH accepts -o Options as well as -oOption,
    # so let's convert argv to the latter form first
    i = iter(argv)
    argv = [p+next(i, '') if p == '-o' else p for p in i]
    # OpenSSH accepts 'Option=yes' and 'Option yes', 'true' instead of 'yes'
    # and treats everything case-insensitive
    # if an option is given multiple times,
    # OpenSSH considers the first occurrence only
    re_batchmode = re.compile(r"-oBatchMode[= ](yes|true)", re.IGNORECASE)
    re_nobatchmode = re.compile(r"-oBatchMode[= ](no|false)", re.IGNORECASE)
    for p in argv:
      if re.match(re_batchmode, p):
        config.Set("SSH_BATCH_MODE", True)
        break
      elif re.match(re_nobatchmode, p):
        config.Set("SSH_BATCH_MODE", False)
        break

def main(argv):
  # Replace stdout and stderr with /dev/tty, so we don't mess up with scripts
  # that use ssh in case we error out or similar.
  try:
    sys.stdout = open("/dev/tty", "w")
    sys.stderr = open("/dev/tty", "w")
  except IOError:
    pass

  config = Config().Load()
  # overwrite python's print function with the wrapper SshIdentPrint
  global print
  print = SshIdentPrint(config)

  AutodetectBinary(argv, config)
  # Check that BINARY_SSH is not ssh-ident.
  # This can happen if the user sets a binary name only (e.g. 'scp') and a
  # symlink with the same name was set up.
  # Note that this relies on argv[0] being set sensibly by the caller,
  # which is not always the case. argv[0] may also just have the binary
  # name if found in a path.
  binary_path = os.path.realpath(
    distutils.spawn.find_executable(config.Get("BINARY_SSH")))
  ssh_ident_path = os.path.realpath(
    distutils.spawn.find_executable(argv[0]))
  if binary_path == ssh_ident_path:
    message = textwrap.dedent("""\
    ssh-ident found '{0}' as the next command to run.
    Based on argv[0] ({1}), it seems like this will create a
    loop. 
    
    Please use BINARY_SSH, BINARY_DIR, or change the way
    ssh-ident is invoked (eg, a different argv[0]) to make
    it work correctly.""")
    print(message.format(config.Get("BINARY_SSH"), argv[0]), loglevel=LOG_ERROR)
    sys.exit(255)
  ParseCommandLine(argv, config)
  identity = FindIdentity(argv, config)
  keys = FindKeys(identity, config)
  sshconfig = FindSSHConfig(identity, config)
  agent = AgentManager(identity, sshconfig, config)

  if not config.Get("SSH_BATCH_MODE"):
    # do not load keys in BatchMode
    agent.LoadUnloadedKeys(keys)
  return agent.RunSSH(argv[1:])

if __name__ == "__main__":
  try:
    sys.exit(main(sys.argv))
  except KeyboardInterrupt:
    print("Goodbye", file=sys.stderr, loglevel=LOG_DEBUG)
