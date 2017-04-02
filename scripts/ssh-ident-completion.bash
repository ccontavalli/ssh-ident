source /usr/share/bash-completion/completions/ssh

_ssh_ident()
{
	# Set the ssh config path if available
	if [[ "${SSH_IDENT_CONFIG}" != "" ]]; then
		set -- "${@:1:2}" "-F$SSH_IDENT_CONFIG" "${@:3}"
    fi
	_ssh $@

    return 0
} && shopt -u hostcomplete && complete -F _ssh_ident ssh slogin autossh
