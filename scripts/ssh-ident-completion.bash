_SSH_COMPLETION_FILE=${SSH_IDENT_SSH_COMPLETION:-/usr/share/bash-completion/completions/ssh}
source $_SSH_COMPLETION_FILE

# Save function named in $1 as name in $2
save_function() {
	local ORIG_FUNC=$(declare -f $1)
	local NEWNAME_FUNC="$2${ORIG_FUNC#$1}"
	eval "$NEWNAME_FUNC"
}

save_function _ssh_configfile __ssh_configfile_orig

_ssh_ident_configfile_override()
{
	if [ ! -z ${__ssh_ident_config+x} ]; then
		configfile=$__ssh_ident_config
	fi

	set -- "${words[@]}"
	while [[ $# -gt 0 ]]; do
		if [[ $1 == -F* ]]; then
			if [[ ${#1} -gt 2 ]]; then
				configfile="$(dequote "${1:2}")"
			else
				shift
				[[ $1 ]] && configfile="$(dequote "$1")"
			fi
			break
		fi
		shift
	done
}

_ssh_ident_ssh()
{
	# Set the ssh config path if available
	if [[ "${SSH_IDENT_CONFIG}" != "" ]]; then
		__ssh_ident_config=${SSH_IDENT_CONFIG}
	fi

	# Override function _ssh_configfile in _SSH_COMPLETION_FILE
	save_function _ssh_ident_configfile_override _ssh_configfile
	_ssh $@
	# Restore _ssh_configfile function
	save_function __ssh_configfile_orig _ssh_configfile

	unset __ssh_ident_config

	return 0
} && shopt -u hostcomplete && complete -F _ssh_ident_ssh ssh slogin autossh


_ssh_ident_scp()
{
	# Set the ssh config path if available
	if [[ "${SSH_IDENT_CONFIG}" != "" ]]; then
		__ssh_ident_config=${SSH_IDENT_CONFIG}
	fi

	# Override function _ssh_configfile in _SSH_COMPLETION_FILE
	save_function _ssh_ident_configfile_override _ssh_configfile
	_scp $@
	# Restore _ssh_configfile function
	save_function __ssh_configfile_orig _ssh_configfile

	unset __ssh_ident_config

	return 0
} && complete -F _ssh_ident_scp scp


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
