#!/bin/sh -e
# vim:se sw=2 ts=2 sts=2 et ai tw=78:
echo "I: check 'git status'"
git status
echo "================================================================="
if ! git diff --quiet || ! git diff --cached --quiet; then
	echo "E: git repository UN-clean.  Clean it first" >&2
	exit 1
else
  echo "I: git repository clean."
fi
echo "================================================================="
UPSTREAM_VERSION="$(sed -n -e 's/__version__ *= *"\([0-9.]*\)"/\1/p' src/imediff/__init__.py)"
echo "new upstream version: $UPSTREAM_VERSION"
# check version
debian/check_version
git rm -rf debian
git commit -m "upstream/$UPSTREAM_VERSION"
git tag --force "upstream/$UPSTREAM_VERSION"
git reset --hard HEAD^
git clean -d -f -x
git deborig --force
sbuild
git reset --hard HEAD
git clean -d -f -x
echo "dgit push-source"

