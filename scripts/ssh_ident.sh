# Bash functions for ssh-ident

#Flag values returned from ssh_ident_cli
__ssh_ident_cli_flag_set_shell_env=1
__ssh_ident_cli_flag_unset_shell_env=2
__ssh_ident_cli_flag_ssh_identity=4
__ssh_ident_cli_flag_ssh_config=8
__ssh_ident_cli_flag_enable_prompt=16
__ssh_ident_cli_flag_disable_prompt=32
__ssh_ident_cli_flag_define_bash_functions=64
__ssh_ident_cli_flag_undefine_bash_functions=128
__ssh_ident_cli_flag_print_output=256
__ssh_ident_cli_flag_verbose=512


define_ssh_ident_bash_funcs () {
	# SSH_IDENT_EXEC_SCRIPT must be global to be available when the functions are executed
	SSH_IDENT_EXEC_SCRIPT=`which ssh_ident_exec`
	export GIT_SSH=$SSH_IDENT_EXEC_SCRIPT
	rsync() { BINARY_SSH=ssh command rsync -e $SSH_IDENT_EXEC_SCRIPT "$@"; }
	sftp()  { BINARY_SSH=ssh command sftp -S $SSH_IDENT_EXEC_SCRIPT "$@"; }
	scp()   { BINARY_SSH=ssh command scp -S $SSH_IDENT_EXEC_SCRIPT "$@"; }
	ssh()   { BINARY_SSH=ssh command $SSH_IDENT_EXEC_SCRIPT "$@"; }
}

undefine_ssh_ident_bash_funcs () {
	unset -f rsync
	unset -f sftp
	unset -f scp
	unset -f ssh
	unset GIT_SSH
}

__ssh_ident_split_output() {
	local cli_action_str
	read -d '' -r cli_action_str cli_stdout <<< "$1"
	# Convert to int
	cli_action=$((cli_action_str + 0))
	# Remove trailing newline
	cli_stdout="${cli_stdout%"${cli_stdout##*[![:space:]]}"}"
}

# Called using PROMPT_COMMAND variable
__ssh_ident_update_ssh_config_var() {
	local cli_action
	local cli_output
	local cli_stdout
	cli_output=`ssh_ident_cli --action-code --config $__SSH_IDENT_PROMPT_ID`
	__ssh_ident_split_output "$cli_output"

	if [[ $(($cli_action & $__ssh_ident_cli_flag_ssh_config)) -gt 0 ]] ; then
		SSH_IDENT_CONFIG=$cli_stdout
	fi
}

# Called using PROMPT_COMMAND variable
__ssh_ident_update_prompt_id() {
	# If SSH_IDENT is set for the shell
	if [[ -n "$SSH_IDENT" ]]; then
		if [[ "$SSH_IDENT" != "$__SSH_IDENT_PROMPT_ID" ]]; then
			__SSH_IDENT_PROMPT_ID=$SSH_IDENT
			__ssh_ident_update_ssh_config_var
			unset __SSH_IDENT_PWD
		fi
		return
	fi

	# Only update __SSH_IDENT_PROMPT_ID if PWD has changed
	if [[ "$__SSH_IDENT_PWD" != "$PWD" ]]; then
		__SSH_IDENT_PWD=$PWD
		local cli_result
		cli_result=`ssh_ident_cli  -iq`
		__SSH_IDENT_PROMPT_ID=$cli_result
		__ssh_ident_update_ssh_config_var
	fi
}

# Activate the ssh-ident shell prompt
ssh_ident_activate() {
	ssh_ident -a $1
}

# Activate the ssh-ident shell prompt
ssh_ident_dectivate() {
	ssh_ident -d
}

# Main entry point to ssh-ident. Calls ssh_ident_cli and acts according to the response
ssh_ident() {
	local cli_output
	local cli_action
	local cli_stdout
	cli_output=`ssh_ident_cli --action-code $@`
	__ssh_ident_split_output "$cli_output"

	if [[ $(($cli_action & $__ssh_ident_cli_flag_verbose)) -gt 0 ]] ; then
		echo "Shell action flags: $cli_action"
	fi

	# Set/Unset shell identity env variable
	if [[ $(($cli_action & $__ssh_ident_cli_flag_set_shell_env)) -gt 0 ]] ; then
		export SSH_IDENT=$cli_stdout
	elif [[ $(($cli_action & $__ssh_ident_cli_flag_unset_shell_env)) -gt 0 ]] ; then
		unset SSH_IDENT
	fi

	# Enable/Disable ssh-ident shell prompt
	if [[ $(($cli_action & $__ssh_ident_cli_flag_enable_prompt)) -gt 0 ]] ; then
		# If prompt already contains __SSH_IDENT_PROMPT_ID, ignore
		if [[ ! "$PS1" == *__SSH_IDENT_PROMPT_ID* ]]; then
			__SSH_IDENT_OLD_PROMPT=$PS1
			PS1="(ssh:\${__SSH_IDENT_PROMPT_ID}) $PS1"
			SSH_IDENT_PROMPT_COMMAND=__ssh_ident_update_prompt_id
			# Add to PROMPT_COMMAND only if not already added
			if [[ ! "$PROMPT_COMMAND" == *SSH_IDENT_PROMPT_COMMAND* ]]; then
				PROMPT_COMMAND=${PROMPT_COMMAND:+$PROMPT_COMMAND; }'$SSH_IDENT_PROMPT_COMMAND'
			fi
		fi
	elif [[ $(($cli_action & $__ssh_ident_cli_flag_disable_prompt)) -gt 0 ]] ; then
		unset SSH_IDENT_PROMPT_COMMAND
		unset __SSH_IDENT_PROMPT_ID
		unset __SSH_IDENT_PWD
		unset -f rsync
		if [ ! -z "${__SSH_IDENT_OLD_PROMPT}" ] ; then
			PS1=$__SSH_IDENT_OLD_PROMPT
			unset __SSH_IDENT_OLD_PROMPT
		fi
	fi

	# Define/Undefine bash function overrides for ssh/scp/sftp/rsync
	if [[ $(($cli_action & $__ssh_ident_cli_flag_define_bash_functions)) -gt 0 ]] ; then
		define_ssh_ident_bash_funcs
	elif [[ $(($cli_action & $__ssh_ident_cli_flag_undefine_bash_functions)) -gt 0 ]] ; then
		undefine_ssh_ident_bash_funcs
	fi

	if [[ $(($cli_action & $__ssh_ident_cli_flag_print_output)) -gt 0 ]] ; then
		echo "$cli_stdout"
	fi
}

# Source the ssh-ident bash completion
source_bash_completion() {
	local ssh_ident_bash_completion_script=ssh-ident-completion.bash
	local script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
	local bash_completion_script_path=`which $ssh_ident_bash_completion_script`

	# If not found, check the dir containing this script
	if [[ -z "$bash_completion_script_path" ]]; then
		bash_completion_script_path=$script_dir/$ssh_ident_bash_completion_script
	fi

	if [[ -f $bash_completion_script_path ]]; then
		source $bash_completion_script_path
	else
		echo "Bash completion script $ssh_ident_bash_completion_script not found!"
	fi
}

source_bash_completion
