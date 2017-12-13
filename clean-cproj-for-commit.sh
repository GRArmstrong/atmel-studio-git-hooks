#!/bin/sh
#
# pre-commit hook, runs before prompt for commit message
#

echo "git hook pre-commit: started"

CPROJ_PATH="Project-Name/Project-Name.cproj"
TARGET_ELEMENTS_JSON_PATH="cproj_target_elements.json"

# Check for existance of Python
if ! hash python ; then
	cat <<\EOF
ERROR: Could not run pre-commit hook.

Cannot find Python executable.

Download Python 3 from the Python website:
https://www.python.org/downloads/release/python-363/
EOF
	exit 1
fi


# Check if the .CPROJ has been changed

# Unstaged:  M Project-Name/Project-Name.cproj
#   Staged: M  Project-Name/Project-Name.cproj

GIT_STATUS="$(git status -s $CPROJ_PATH)"
if [[ $GIT_STATUS == M* ]] ; then
	# If file is staged

	# Backup project file
	if ! cp $CPROJ_PATH $CPROJ_PATH~ ; then
		echo "ERROR: Could not backup '$CPROJ_PATH'"
		exit 1
	fi
	echo "Backed up '$CPROJ_PATH' to '$CPROJ_PATH~'"

	# Format using Python script.
	python "clean-cproj.py" $CPROJ_PATH $TARGET_ELEMENTS_JSON_PATH

	# Stage project file
	git add $CPROJ_PATH

elif [[ ! $GIT_STATUS ]]; then
	#statements
	echo "No changes to '$CPROJ_PATH'; nothing to do."
else
	# If file is not staged
	echo "File '$CPROJ_PATH' is not staged; nothing to do."
fi

echo "git hook pre-commit: finished"
exit 0
