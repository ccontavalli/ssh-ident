source /usr/share/bash-completion/completions/ssh

_ssh_ident_ssh()
{
	# Set the ssh config path if available
	if [[ "${SSH_IDENT_CONFIG}" != "" ]]; then
		set -- "${@:1:2}" "-F$SSH_IDENT_CONFIG" "${@:3}"
    fi
	_ssh $@

    return 0
} && shopt -u hostcomplete && complete -F _ssh_ident_ssh ssh slogin autossh


# scp completion with _ssh_ident_scp doesn't work properly due to the extra call
# 'set -- "${words[@]}"' in function _scp() in
# /usr/share/bash-completion/completions/ssh

#_ssh_ident_scp()
#{
#	# Set the ssh config path if available
#	if [[ "${SSH_IDENT_CONFIG}" != "" ]]; then
#		conf="-F$SSH_IDENT_CONFIG"
#		conf_len=${#conf}
#		set -- "${@:1:1}" "$conf" "${@:2}"
#		COMP_WORDS=("$@")
#		COMP_CWORD=$((COMP_CWORD+1))
#		COMP_LINE=$(printf " %s" "$@")
#		COMP_LINE=${COMP_LINE:1}
#		COMP_POINT=$((COMP_POINT+$conf_len+1))
#    fi
#
#	_scp $@
#
#    return 0
#} && complete -F _ssh_ident_scp scp
