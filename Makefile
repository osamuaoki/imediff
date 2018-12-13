#  Run "make" to generate required files first

prefix = /usr
#prefix = /usr/local

PACKAGE := imediff
VERSION := $(shell grep "^VERSION" imediff/config.py | sed 's/" *$$//;s/^VERSION *= *"//')
DISTFILE := $(PACKAGE)-$(VERSION).tar.gz
DSRCFILE := $(PACKAGE)_$(VERSION).orig.tar.gz
PACKAGE_PATH := $(PACKAGE)-$(VERSION)
PYSOURCE := $(wildcard imediff/*.py)
POSOURCE := $(wildcard po/*.po)
MOSOURCE := $(wildcard po/*/LC_MESSAGES/imediff.mo)
GITMERGEPATH := $(DESTDIR)/$(prefix)/lib/git-core/mergetools
LOCALEPATH := $(DESTDIR)/$(prefix)/share/locale

all: man mo
	echo "Build PO and manpages"

man:
	$(MAKE) -C doc all

po/imediff.pot: $(PYSOURCE)
	xgettext -o po/imediff.pot $(PYSOURCE)

po/%.po: po/imediff.pot
	msgmerge --update --previous $@ $<

po/%/LC_MESSAGES/imediff.mo: po/%.po
	mkdir -p $$(dirname $@)
	msgfmt $< -o $@

po: $(POSOURCE)

mo: $(patsubst po/%.po, po/%/LC_MESSAGES/imediff.mo, $(POSOURCE))

# dh calls distclean/realclean unless forced to call clean.
distclean: clean
clean:
	$(MAKE) -C doc clean
	@-rm -f $(MOSOURCE) po/*.po~  2>/dev/null  || true
	@-rm -rf imediff/__pycache__ 2>/dev/null  || true

install-%: po/%/LC_MESSAGES/imediff.mo
	mkdir -p $(LOCALEPATH)/$*/LC_MESSAGES
	cp po/$*/LC_MESSAGES/imediff.mo $(LOCALEPATH)/$*/LC_MESSAGES/imediff.mo

install: $(patsubst po/%.po, install-%, $(POSOURCE))
	mkdir -p $(GITMERGEPATH)
	cp mergetools/imediff $(GITMERGEPATH)
	chown 0:0 $(GITMERGEPATH)/imediff
	chmod 755 $(GITMERGEPATH)/imediff

###############################################################################
# DEBIAN SOURCE PACKAGE GENERATION SCRIPT
###############################################################################

realclean: clean
	rm -rf ../$(PACKAGE_PATH)/
	rm -f ../$(DISTFILE) ../$(DSRCFILE)

../$(DISTFILE):
	if [ -d ../$(PACKAGE_PATH) ] ; then \
	echo -e "\n\nRun \"make realclean\" first to remove ../$(PACKAGE_PATH)/\n\n" ; \
	false ; \
	fi
	mkdir ../$(PACKAGE_PATH)/
	-cp * ../$(PACKAGE_PATH)/ # skip subdir and . files
	if [ -d debian ]; then cp -r debian ../$(PACKAGE_PATH)/ ; fi
	if [ -d debian ]; then \
		cd .. ; tar --exclude=$(PACKAGE_PATH)/debian -cvzf $(DISTFILE) $(PACKAGE_PATH)/ ;\
	else \
		cd .. ; tar -cvzf $(DISTFILE) $(PACKAGE_PATH)/ ;\
	fi
	if [ -d debian ]; then cd .. ; ln -sf $(DISTFILE) $(DSRCFILE) ; fi 

dist: ../$(DISTFILE)

sign: ../$(DISTFILE)
	gpg --detach-sign --armor $?
