# Test suite for imediff and git-ime

## imediff


### test imediff


```
    $ reset; test_imediff.sh
```

This will compare `*.new` created by `make_new_ref.sh` to `*.ref` in here.

* `./_diff23.py >z_diff23.new` -- test with files (file_a, file_b file_c)
* `./_imediff.py  -C BOGUS -n file_a file_b -o z_imediff2.new` -- test diff2
* `./_imediff.py -C BOGUS -n file_a file_b file_c -o z_imediff3.new` -- test diff3
* `./_initialize.py  > z_initialize.new` -- test initialization
* `./_macrotrans.py -C alternative_imediff.conf -n file_a file_b file_c > z_macrotrans.new` -- test key bindings

If `-c` option is given, test continues even if ERROR

### test diff library

* `python3 test_diff23lib.py` -- test without file access

### Tested module

To test local scripts and module files, set `$PYTHONPATH`:

``
 $ export PYTHONPATH=../src
``

otherwise system installed module

## git-ime

* If $GIT_IME is set to a local one, use it as git-ime
```
    $ reset; GIT_IME=$(realpath ../bin/git-ime) ./test_git_ime.sh
```
* If $GIT_IME is not set, use the system one as git-ime
```
    $ reset; test_git_ime.sh
```

## Note on updating reference files

If you change configuration file format, you need to update data in this
directory.

  * update reference template z_initialize.ref
  * update alternative_imediff.conf to get z_macrotrans.ref to match (except
    new parameters)

Baseline template file for alternative_imediff.conf can be generated by running
the following command start from this directory.


 $ cd ../src/imediff
 $ export PYTHONPATH=../; ./config.py
 $ mv TEMPLATE.imediff ../../test/alternative_imediff.conf.new

You need to make the same kind of key swappings in this
`alternative_imediff.conf` .

For Debian package building, dh_auto_test isn't run from here.  It looks like a
copy of test/ directory as test and a copy of src/imediff directory as imediff
is created at .pybuild/cpython3_3.9/ where the current directory is moved to.

Notable thing is that when test/ directories are copied, symlinks are copied as files.
