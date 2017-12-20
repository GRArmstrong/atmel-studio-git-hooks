::
:: Copy the git commit hooks to the ./.git/hooks directory to
:: keep the *.cproj file clean when committing.
::

mkdir .git\hooks
copy /-Y pre-commit	.git\hooks\pre-commit
copy /-Y post-commit .git\hooks\post-commit

set /p=Hit ENTER to continue...
