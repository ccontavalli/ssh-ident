#!/usr/bin/env python
# vim: tabstop=2 shiftwidth=2 expandtab
from __future__ import print_function

import argparse
import os
import sys
from os.path import isdir, join

from ssh_ident import IDENTITY_TYPE, Config, FindIdentity, FindSSHConfig
from utils import enum

ACTION_FLAGS = enum(SET_SHELL_ENV=1,
                    UNSET_SHELL_ENV=2,
                    SSH_IDENTITY=4,
                    SSH_CONFIG=8,
                    ENABLE_PROMPT=16,
                    DISABLE_PROMPT=32,
                    DEFINE_BASH_FUNCTIONS=64,
                    UNDEFINE_BASH_FUNCTIONS=128,
                    PRINT_OUTPUT=256,
                    VERBOSE=512)


def get_identities(config):
  identities_path = config.Get("DIR_IDENTITIES")
  return [f for f in os.listdir(identities_path) if isdir(join(identities_path, f))]


def main():
  """

  exits with sys.exit return value indicating an action to be performed
  defined by ACTION_FLAGS enum.

  Exit code 0 means to print the output directly
  """
  parser = argparse.ArgumentParser(add_help=False)
  parser.add_argument("-q", "--quiet", action="store_true", help="Be quieter")
  parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
  parser.add_argument('-h', '--help', action='store_true', dest='help')
  parser.add_argument('--action-code', action='store_true',
                      help='Prefix output with an int containing flags as defined by ACTION_FLAGS')
  group = parser.add_mutually_exclusive_group()
  group.add_argument("-l", "--list", action="store_true", help="List identities")
  group.add_argument("-i", "--identity", action="store_true", help="Show current identity")
  group.add_argument("-a", "--activate", action="store_true", help="Activate ssh-ident with default config settings")
  group.add_argument("-d", "--deactivate", action="store_true", help="Dectivate ssh-ident")
  group.add_argument("-c", "--create", metavar='<identity>', help="Create a new identity")
  group.add_argument("-s", "--shell", metavar='<identity>', nargs='?', const='default-ssh-id',
                     help="Set identity for the shell")
  group.add_argument("-u", "--unset-shell", action="store_true", help="Unset identity for the shell")
  group.add_argument("-p", "--prompt", action="store_true", help="Enable prompt")
  group.add_argument("-r", "--remove-prompt", action="store_true", help="Remove prompt indicator")
  group.add_argument("--config", metavar='<identity>', help="Get config for a specified identity.")

  args = parser.parse_args()
  config = Config().Load()
  import StringIO
  stdoutput = StringIO.StringIO()

  exit_val = 0
  print_help = False

  if args.help:
    print_help = True
  elif args.list:
      exit_val |= ACTION_FLAGS.PRINT_OUTPUT
      idents = get_identities(config)
      print("Identities:", file=stdoutput)
      for i in sorted(idents):
        print("- %s" % i, file=stdoutput)
  elif args.identity:
    exit_val |= ACTION_FLAGS.PRINT_OUTPUT
    idents = get_identities(config)
    identity, id_type, match = FindIdentity(sys.argv, config)
    if identity not in idents:
      print("Bad identity set by %s (%s). Should be one of '%s'" %
            (IDENTITY_TYPE.kstr(id_type), identity, ", ".join(idents)),
            file=stdoutput)
    else:
      if args.quiet:
        print(identity, file=stdoutput)
      else:
        print("%s (set by %s%s)" % (identity, IDENTITY_TYPE.kstr(id_type), " [%s]" % match if match else ""),
              file=stdoutput)
  elif args.create:
    identities_path = config.Get("DIR_IDENTITIES")
    id_path = os.path.join(identities_path, args.create)
    os.mkdir(id_path)
    open(os.path.join(id_path, "config"), 'a').close()
    print("Created identity '%s': %s" % (args.create, id_path), file=stdoutput)
    exit_val |= ACTION_FLAGS.PRINT_OUTPUT
  elif args.shell:
    if args.shell != 'default-ssh-id' and args.shell not in get_identities(config):
      print("Bad identity '%s'" % (args.shell), file=stdoutput)
      exit_val |= ACTION_FLAGS.PRINT_OUTPUT
    else:
      exit_val |= ACTION_FLAGS.SET_SHELL_ENV | ACTION_FLAGS.SSH_IDENTITY
      if args.shell == 'default-ssh-id':
        args.shell = config.Get("DEFAULT_IDENTITY")
      print(args.shell, file=stdoutput, end='')
  elif args.unset_shell:
    exit_val |= ACTION_FLAGS.UNSET_SHELL_ENV
  elif args.prompt:
    exit_val |= ACTION_FLAGS.ENABLE_PROMPT
  elif args.remove_prompt:
    exit_val |= ACTION_FLAGS.DISABLE_PROMPT
  elif args.activate:
    idents = get_identities(config)
    identity, id_type, match = FindIdentity(sys.argv, config)
    if identity in idents:
      exit_val |= ACTION_FLAGS.SSH_IDENTITY
      print(identity, file=stdoutput)
    if config.Get("SSH_IDENT_PROMPT"):
      exit_val |= ACTION_FLAGS.ENABLE_PROMPT
    if config.Get("SSH_IDENT_BASH_FUNCTIONS"):
      exit_val |= ACTION_FLAGS.DEFINE_BASH_FUNCTIONS
  elif args.deactivate:
    exit_val |= ACTION_FLAGS.UNSET_SHELL_ENV
    if config.Get("SSH_IDENT_PROMPT"):
      exit_val |= ACTION_FLAGS.DISABLE_PROMPT
    if config.Get("SSH_IDENT_BASH_FUNCTIONS"):
      exit_val |= ACTION_FLAGS.UNDEFINE_BASH_FUNCTIONS
  elif args.config:
    sshconfig = FindSSHConfig(args.config, config)
    if sshconfig:
      if args.action_code:
        exit_val = ACTION_FLAGS.SSH_CONFIG
      print(sshconfig, file=stdoutput)
      exit_val |= ACTION_FLAGS.PRINT_OUTPUT
  else:
    print_help = True

  if print_help:
    exit_val |= ACTION_FLAGS.PRINT_OUTPUT
    h = parser.format_help()
    print(h, file=stdoutput)

  if args.verbose:
    exit_val |= ACTION_FLAGS.VERBOSE

  if args.action_code:
    print("%d %s" % (exit_val, stdoutput.getvalue().strip()))
  else:
    print(stdoutput.getvalue().strip())


if __name__ == "__main__":
  main()
