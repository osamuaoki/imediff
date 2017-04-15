# The generated distribution and temporary source tree in the parent directory

PACKAGE := imediff2
VERSION := $(shell grep "^VERSION" imediff2 | sed "s/[^0-9]*$$//;s/^[^0-9]*//")
DISTFILE := $(PACKAGE)-$(VERSION).tar.gz
DSRCFILE := $(PACKAGE)_$(VERSION).orig.tar.gz
PACKAGE_PATH := $(PACKAGE)-$(VERSION)

all: imediff2.1

imediff2.1:  imediff2-docbook.xml
	xsltproc --novalid /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl $?

# dh calls distclean/realclean unless forced to call clean.
distclean: clean
	rm -rf ../$(PACKAGE_PATH)/
	rm -f $(PACKAGE).1
	rm -f ../$(DISTFILE) ../$(DSRCFILE)

clean:

../$(DISTFILE):
	if [ -d ../$(PACKAGE_PATH) ] ; then echo -e "\n\nRun \"make realclean\" first to remove ../$(PACKAGE_PATH)/\n\n" ; false ; fi
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
