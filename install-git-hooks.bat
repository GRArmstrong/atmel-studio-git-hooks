::
:: Copy the git commit hooks to the ./.git/hooks directory to
:: keep the *.cproj file clean when committing.
::

copy pre-commit	.git\hooks\pre-commit
copy post-commit .git\hooks\post-commit
