#!/bin/sh -e
# vim: set sw=2 et sw=2 sts=2:
# working toss-away repo location
BASEDIR="${0%/*}"
REPO_DIR="${BASEDIR}/repo"
OPTQ="--quiet"
#OPTQ=""
# If $GIT_IME is not set, use system one
if [ -z "$GIT_IME" ]; then
  if which git-ime; then
    GIT_IME="$(which git-ime)"
  else
    # shellcheck disable=SC2016
    echo 'Install git-ime in your $PATH or set $GIT_IME' >&2
    exit 1
  fi
else
  GIT_IME="$(realpath "${GIT_IME}")"
fi

if [ "$1" = "-c" ]; then
  rm -rf "$REPO_DIR"
  exit
fi

create_repo () {
  git init $OPTQ
  git add .
  git commit $OPTQ -m "initial"
}
commit_data () {
  git add -A .
  git commit $OPTQ -m "data changed"
}
base_data () {
  for i in $(seq 10 29); do
    echo "CONTENT $i" > "FILE_$i"
  done
}
base_file () {
  : > "FILE"
  for i in $(seq 10 29); do
    echo "CONTENT $i" >> "FILE"
  done
}
change_data () {
  for i in $(seq 10 29); do
    sed -i 's/^/THIS /' "FILE_$i"
  done
}
change_file () {
  for i in $(seq 10 4 29); do
    sed -i "s/$i/___XXX_CHANGED_XXX___/" "FILE"
  done
}
move_file () {
  mv FILE_10 FILE_99
}
drop_data () {
  for i in $(seq 10 2 29); do
    rm "FILE_$i"
  done
}
add_data () {
  for i in $(seq 30 39); do
    echo "CONTENT $i" > "FILE_$i"
  done
}
junk1_data () {
  for i in $(seq 10 2 19); do
    echo "CONTENT $i" > "FILE_$i"
  done
}
junk2_data () {
  for i in $(seq 11 2 19); do
    sed -i 's/^/RANDOM /' "FILE_$i"
  done
}

test_good1 () {
  echo "--- split a commit of a single file with multiple changes in it by chunk"
  rm -rf "$REPO_DIR"
  test -d "$REPO_DIR" || mkdir -p "$REPO_DIR"
  cd "$REPO_DIR"
  base_file
  create_repo
  change_file
  commit_data
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  # shellcheck disable=SC2086
  $GIT_IME -a $OPTQ
  N_CHANGED="$(git log --pretty=oneline | wc -l)"
  echo "I: >>> changed $N_CHANGED"
  if [ "$N_CHANGED" = "6" ]; then
    echo "NO_ERROR at test_good1 (expected)"
  else
    echo "ERROR at test_good1"
    false
  fi
  cd ..
}

test_good2 () {
  echo "--- split a commit with multiple files with changes by file"
  rm -rf "$REPO_DIR"
  test -d "$REPO_DIR" || mkdir -p "$REPO_DIR"
  cd "$REPO_DIR"
  base_data
  create_repo
  change_data
  drop_data
  add_data
  commit_data
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  $GIT_IME $OPTQ
  N_CHANGED="$(git log --pretty=oneline | wc -l)"
  echo "I: >>> changed $N_CHANGED" # 31 = 30 (changes)+ 1(initial)
  if [ "$N_CHANGED" = "31" ]; then
    echo "NO_ERROR at test_good2 (expected)"
  else
    echo "ERROR at test_good2"
    false
  fi
  cd ..
}

test_good3 () {
  echo "--- split a commit with a moved file"
  rm -rf "$REPO_DIR"
  test -d "$REPO_DIR" || mkdir -p "$REPO_DIR"
  cd "$REPO_DIR"
  base_data
  create_repo
  move_file
  commit_data
  echo ">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
  $GIT_IME $OPTQ
  git log --pretty=oneline
  N_CHANGED="$(git log --pretty=oneline | wc -l)"
  echo "I: >>> changed $N_CHANGED" # 3 = 2 (changes)+ 1(initial)
  if [ "$N_CHANGED" = "3" ]; then
    echo "NO_ERROR at test_good3 (expected)"
  else
    echo "ERROR at test_good3"
    false
  fi
  cd ..
  rm -rf "$REPO_DIR"
}


test_bad1 () {
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
  if $GIT_IME $OPTQ ; then
    echo "NO_ERROR at test_bad1"
    false
  else
    echo "ERROR at test_bad1 (expected)"
  fi
  cd ..
}

test_bad2 () {
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
  if $GIT_IME $OPTQ ; then
    echo "NO_ERROR at test_bad1"
    false
  else
    echo "ERROR at test_bad1 (expected)"
  fi
  cd ..
}

test_bad3 () {
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
  if $GIT_IME $OPTQ ; then
    echo "NO_ERROR at test_bad1"
    false
  else
    echo "ERROR at test_bad1 (expected)"
  fi
  cd ..
}


test_bad4 () {
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
  if $GIT_IME $OPTQ ; then
    echo "NO_ERROR at test_bad1"
    false
  else
    echo "ERROR at test_bad1 (expected)"
  fi
  cd ..
}


echo "===== START ====="
echo "=== vvv SHOULD WORK vvv === 1"
test_good1
echo "=== vvv SHOULD WORK vvv === 2"
test_good2
echo "=== vvv SHOULD WORK vvv === 3"
test_good3
echo "=== vvv SHOULD FAIL vvv === 1"
test_bad1
echo "=== vvv SHOULD FAIL vvv === 2"
test_bad2
echo "=== vvv SHOULD FAIL vvv === 3"
test_bad3
echo "=== vvv SHOULD FAIL vvv === 4"
test_bad4
echo "===== SUCCESS ALL ====="
rm -rf "$REPO_DIR"
