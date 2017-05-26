Help on module ssh-ident:

NAME
    ssh-ident - Start and use ssh-agent and load identities as necessary.

FILE
    /opt/projects/ssh-ident.git/ssh-ident

DESCRIPTION
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

CLASSES
    __builtin__.object
        AgentManager
        Config
        SshIdentPrint
    
    class AgentManager(__builtin__.object)
     |  Manages the ssh-agent for one identity.
     |  
     |  Methods defined here:
     |  
     |  FindUnloadedKeys(self, keys)
     |      Determines which keys have not been loaded yet.
     |      
     |      Args:
     |        keys: dict as returned by FindKeys.
     |      
     |      Returns:
     |        iterable of strings, paths to private key files to load.
     |  
     |  GetLoadedKeys(self)
     |      Returns an iterable of strings, each the fingerprint of a loaded key.
     |  
     |  GetShellArgs(self)
     |      Returns the flags to be passed to the shell to run a command.
     |  
     |  LoadKeyFiles(self, keys)
     |      Load all specified keys.
     |      
     |      Args:
     |        keys: iterable of strings, each string a path to a key to load.
     |  
     |  LoadUnloadedKeys(self, keys)
     |      Loads all the keys specified that are not loaded.
     |      
     |      Args:
     |        keys: dict as returned by FindKeys.
     |  
     |  RunSSH(self, argv)
     |      Execs ssh with the specified arguments.
     |  
     |  __init__(self, identity, sshconfig, config)
     |      Initializes an AgentManager object.
     |      
     |      Args:
     |        identity: string, identity the ssh-agent managed by this instance of
     |            an AgentManager will control.
     |        config: object implementing the Config interface, allows access to
     |            the user configuration parameters.
     |      
     |      Attributes:
     |        identity: same as above.
     |        config: same as above.
     |        agents_path: directory where the config of all agents is kept.
     |        agent_file: the config of the agent corresponding to this identity.
     |      
     |      Parameters:
     |        DIR_AGENTS: used to compute agents_path.
     |        BINARY_SSH: path to the ssh binary.
     |  
     |  ----------------------------------------------------------------------
     |  Static methods defined here:
     |  
     |  EscapeShellArguments(argv)
     |      Escapes all arguments to the shell, returns a string.
     |  
     |  GetAgentFile(path, identity)
     |      Returns the path to an agent config file.
     |      
     |      Args:
     |        path: string, the path where agent config files are kept.
     |        identity: string, identity for which to load the agent.
     |      
     |      Returns:
     |        string, path to the agent file.
     |  
     |  GetPublicKeyFingerprint(key)
     |      Returns the fingerprint of a public key as a string.
     |  
     |  IsAgentFileValid(agentfile)
     |      Returns true if the specified agentfile refers to a running agent.
     |  
     |  RunShellCommand(command)
     |      Runs a shell command, returns (status, stdout), (int, string).
     |  
     |  RunShellCommandInAgent(agentfile, command, stdin=None, stdout=-1)
     |      Runs a shell command with an agent configured in the environment.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
    
    class Config(__builtin__.object)
     |  Holds and loads users configurations.
     |  
     |  Methods defined here:
     |  
     |  Get(self, parameter)
     |      Returns the value of a parameter, or causes the script to exit.
     |  
     |  Load(self)
     |      Load configurations from the default user file.
     |  
     |  Set(self, parameter, value)
     |      Sets configuration option parameter to value.
     |  
     |  __init__(self)
     |  
     |  ----------------------------------------------------------------------
     |  Static methods defined here:
     |  
     |  Expand(value)
     |      Expand environment variables or ~ in string parameters.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)
     |  
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |  
     |  defaults = {'BINARY_DIR': None, 'BINARY_SSH': None, 'DEFAULT_IDENTITY'...
    
    class SshIdentPrint(__builtin__.object)
     |  Wrapper around python's print function.
     |  
     |  Methods defined here:
     |  
     |  __call__ = write(self, *args, **kwargs)
     |  
     |  __init__(self, config)
     |        config: object implementing the Config interface, allows access to
     |            the user configuration parameters.
     |      
     |      Attributes:
     |        config: same as above.
     |        python_print: python's print function (hopefully)
     |      
     |      Parameters:
     |        SSH_BATCH_MODE: used to check if messages should be printed or not
     |        VERBOSITY: used to check if messages should be printed or not
     |  
     |  write(self, *args, **kwargs)
     |      Passes all parameters to python's print,
     |      unless output is disabled by the configuration.
     |      The interface is compatible with python's print, but supports the
     |      optional parameter 'loglevel' in addition.
     |  
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |  
     |  __dict__
     |      dictionary for instance variables (if defined)
     |  
     |  __weakref__
     |      list of weak references to the object (if defined)

FUNCTIONS
    AutodetectBinary(argv, config)
        Detects the correct binary to run and sets BINARY_SSH accordingly,
        if it is not already set.
    
    FindIdentity(argv, config)
        Returns the identity to use based on current directory or argv.
        
        Args:
          argv: iterable of string, argv passed to this program.
          config: instance of an object implementing the same interface as
              the Config class.
        
        Returns:
          string, the name of the identity to use.
    
    FindIdentityInList(elements, identities)
        Matches a list of identities to a list of elements.
        
        Args:
          elements: iterable of strings, arbitrary strings to match on.
          identities: iterable of (string, string), with first string
            being a regular expression, the second string being an identity.
        
        Returns:
          The identity specified in identities for the first regular expression
          matching the first element in elements.
    
    FindKeys(identity, config)
        Finds all the private and public keys associated with an identity.
        
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
    
    FindSSHConfig(identity, config)
        Finds a config file if there's one associated with an identity
        
        Args:
          identity: string, name of the identity to load strings of.
          config: object implementing the Config interface, providing configurations
              for the user.
        
        Returns:
          string, the configuration file to use
    
    GetSessionTty()
        Returns a file descriptor for the session TTY, or None.
        
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
    
    ParseCommandLine(argv, config)
        Parses the command line parameters in argv
        and modifies config accordingly.
    
    ShouldPrint(config, loglevel)
        Returns true if a message by the specified loglevel should be printed.
    
    main(argv)

DATA
    LOG_CONSTANTS = {'LOG_DEBUG': 4, 'LOG_ERROR': 1, 'LOG_INFO': 3, 'LOG_W...
    LOG_DEBUG = 4
    LOG_ERROR = 1
    LOG_INFO = 3
    LOG_WARN = 2
    print_function = _Feature((2, 6, 0, 'alpha', 2), (3, 0, 0, 'alpha', 0)...


