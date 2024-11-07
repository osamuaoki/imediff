#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
# This is invoked from source tree to test git-ime codes
# Use installed imediff (deb or wheel)
#
# working toss-away repo location
THISFILE="$(realpath $0)"
THISDIR="${THISFILE%/*}"
REPO_DIR="${THISDIR}/repo"
GIT_IME=$THISDIR/../usr/bin/git-ime.in

if [ "$1" = "-c" ]; then
	rm -rf "$REPO_DIR"
	exit
fi

create_repo() {
	git init
	git add .
	git commit -m "initial"
	git tag "initial"
}
commit_data() {
	git add -A .
	git commit -m "data changed"
}
base_data() {
	for i in $(seq 10 29); do
		: >"FILE_$i"
		for j in $(seq 10 29); do
			echo "CONTENT $i -- $j" >>"FILE_$i"
		done
	done
}
change_data() {
	for i in $(seq 10 29); do
		sed -i 's/[257]/X/g' "FILE_$i"
	done
}
change_a_file() {
	mv FILE_10 FILE_99
	sed -i "s/9/X/g" "FILE_99"
	git add FILE_99
}
drop_data() {
	for i in $(seq 10 3 29); do
		rm "FILE_$i"
	done
}
add_data() {
	for i in $(seq 30 39); do
		: >"FILE_$i"
		for j in $(seq 10 29); do
			echo "CONTENT $i -- $j" >>"FILE_$i"
		done
	done
}
junk1_data() {
	for i in $(seq 40 2 45); do
		echo "CONTENT $i" >"FILE_$i"
	done
}
junk2_data() {
	for i in $(seq 11 39); do
		if [ -e "FILE_$i" ]; then
			sed -i 's/^/RANDOM /' "FILE_$i"
		fi
	done
}

test_good1() {
	echo "--- split multiple file commits"
	rm -rf "$REPO_DIR"
	test -d "$REPO_DIR" || mkdir -p "$REPO_DIR"
	cd "$REPO_DIR"
	base_data
	create_repo
	change_data
	commit_data
	echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	# shellcheck disable=SC2086
	$GIT_IME -a
	N_CHANGED="$(git log --pretty=oneline | wc -l)"
	echo "I: >>> changed $N_CHANGED"
	if [ "$N_CHANGED" = "21" ]; then
		echo "NO_ERROR at test_good1 (expected)"
	else
		echo "ERROR at test_good1"
		false
	fi
	cd ..
}

test_good2() {
	echo "--- split a commit with multiple files with changes by file"
	rm -rf "$REPO_DIR"
	test -d "$REPO_DIR" || mkdir -p "$REPO_DIR"
	cd "$REPO_DIR"
	base_data
	create_repo
	drop_data
	add_data
	commit_data
	echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	$GIT_IME -a
	N_CHANGED="$(git log --pretty=oneline | wc -l)"
	echo "I: >>> changed $N_CHANGED" # 31 = 30 (changes)+ 1(initial)
	if [ "$N_CHANGED" = "18" ]; then
		echo "NO_ERROR at test_good2 (expected)"
	else
		echo "ERROR at test_good2"
		false
	fi
	cd ..
}

test_good3() {
	echo "--- split a commit with a moved file"
	rm -rf "$REPO_DIR"
	test -d "$REPO_DIR" || mkdir -p "$REPO_DIR"
	cd "$REPO_DIR"
	base_data
	create_repo
	change_a_file
	commit_data
	echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	$GIT_IME -a
	git log --pretty=oneline
	N_CHANGED="$(git log --pretty=oneline | wc -l)"
	echo "I: >>> changed $N_CHANGED"
	if [ "$N_CHANGED" = "3" ]; then
		echo "NO_ERROR at test_good3 (expected)"
	else
		echo "ERROR at test_good3"
		false
	fi
	cd ..
}

test_bad1() {
	echo "--- revert contents to HEAD^ after commit"
	rm -rf "$REPO_DIR"
	test -d "$REPO_DIR" || mkdir -p "$REPO_DIR"
	cd "$REPO_DIR"
	base_data
	create_repo
	change_data
	drop_data
	add_data
	commit_data
	base_data
	echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	# shellcheck disable=SC2086
	if $GIT_IME $OPTQ; then
		echo "NO_ERROR at test_bad1"
		false
	else
		echo "ERROR at test_bad1 (expected)"
	fi
	cd ..
}

test_bad2() {
	echo "--- add bogus empty directory after commit"
	rm -rf "$REPO_DIR"
	test -d "$REPO_DIR" || mkdir -p "$REPO_DIR"
	cd "$REPO_DIR"
	base_data
	create_repo
	change_data
	drop_data
	add_data
	commit_data
	mkdir -p bogus
	echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	# shellcheck disable=SC2086
	if $GIT_IME $OPTQ; then
		echo "NO_ERROR at test_bad2"
		false
	else
		echo "ERROR at test_bad2 (expected)"
	fi
	cd ..
}

test_bad3() {
	echo "--- add junk files after commit"
	rm -rf "$REPO_DIR"
	test -d "$REPO_DIR" || mkdir -p "$REPO_DIR"
	cd "$REPO_DIR"
	base_data
	create_repo
	change_data
	drop_data
	add_data
	commit_data
	junk1_data
	echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	# shellcheck disable=SC2086
	if $GIT_IME $OPTQ; then
		echo "NO_ERROR at test_bad3"
		false
	else
		echo "ERROR at test_bad3 (expected)"
	fi
	cd ..
}

test_bad4() {
	echo "--- add junk changes after commit"
	rm -rf "$REPO_DIR"
	test -d "$REPO_DIR" || mkdir -p "$REPO_DIR"
	cd "$REPO_DIR"
	base_data
	create_repo
	change_data
	drop_data
	add_data
	commit_data
	junk2_data
	echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
	# shellcheck disable=SC2086
	if $GIT_IME $OPTQ; then
		echo "NO_ERROR at test_bad4"
		false
	else
		echo "ERROR at test_bad4 (expected)"
	fi
	cd ..
}

echo "===== START ====="
echo "=== vvv SHOULD WORK vvv === 1"
test_good1
echo
echo "=== vvv SHOULD WORK vvv === 2"
test_good2
echo
echo "=== vvv SHOULD WORK vvv === 3"
test_good3
echo
echo "=== vvv SHOULD FAIL vvv === 1"
test_bad1
echo
echo "=== vvv SHOULD FAIL vvv === 2"
test_bad2
echo
echo "=== vvv SHOULD FAIL vvv === 3"
test_bad3
echo
echo "=== vvv SHOULD FAIL vvv === 4"
test_bad4
echo
echo
rm -rf "$REPO_DIR"
echo "===== SUCCESS ALL ====="
