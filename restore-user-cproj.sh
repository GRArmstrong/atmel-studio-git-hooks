#!/bin/sh
#
# post-commit hook, runs after commit
#

CPROJ_PATH="Project-Name/Project-Name.cproj"

if [ -e $CPROJ_PATH~ ] ; then
	echo "git hook post-commit: restoring user *.cproj"
	rm $CPROJ_PATH
	mv $CPROJ_PATH~ $CPROJ_PATH
fi

exit 0
