#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

import os

from setuptools import find_packages, setup
from setuptools.command.develop import develop

# Importing __version__ from ssh_ident fails for some reason, so import directly
from ssh_ident.ssh_ident import VERSION


class SshIdentDevelop(develop):

    user_options = develop.user_options + [
        ("symlinks", "s", "Create script symlinks"),
    ]
    boolean_options = develop.boolean_options + ['symlinks']

    def initialize_options(self):
        self.symlinks = False
        develop.initialize_options(self)

    def run(self):
        develop.run(self)

        if not self.symlinks:
            return

        print("Creating symlinks for scripts")
        for script in self.distribution.scripts or []:
            fname = os.path.basename(script)
            script_abs_path = os.path.abspath(script)
            dest_file = os.path.join(self.script_dir, fname)
            if os.path.isfile(dest_file):
                os.remove(dest_file)
            print("%s -> %s" % (dest_file, script_abs_path))
            os.symlink(script_abs_path, dest_file)


setup(name='ssh-ident',
      version=VERSION,
      description="Start and use ssh-agent and load identities as necessary.",
      long_description="Start and use ssh-agent and load identities as necessary.",
      url='https://github.com/ccontavalli/ssh-ident',
      license="BSD",
      packages=find_packages(),
      namespace_packages=['ssh_ident'],
      entry_points={'console_scripts':
                    ['ssh_ident_exec = ssh_ident.ssh_ident:main',
                     'ssh_ident_cli = ssh_ident.ssh_ident_cli:main'
                    ]
      },
      scripts=[
          'scripts/ssh-ident-completion.bash',
          'scripts/ssh_ident.sh',
      ],
      cmdclass={'develop': SshIdentDevelop},
      zip_safe=False,
      classifiers=[
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: BSD License',
          'Natural Language :: English',
          'Operating System :: POSIX'
      ])
