PACKAGE := imediff2-$(shell grep "^VERSION" imediff2 | sed "s/[^0-9]*$$//;s/^[^0-9]*//")
DISTFILE := $(PACKAGE).tar.gz

all: imediff2.1

imediff2.1:  imediff2-docbook.xml
	xsltproc --novalid /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl $?

mostlyclean:
	rm -rf $(PACKAGE)/
	rm -f $(DISTFILE)*

distclean: mostlyclean

clean: mostlyclean

$(PACKAGE).tar.gz: distclean
	mkdir $(PACKAGE)/
	-cp * $(PACKAGE)/
	-cp -r debian $(PACKAGE)/
	sync
	find $(PACKAGE)/ -name '.svn' -o -name '.cvs'
	rm -rf `find $(PACKAGE)/ -name '.svn' -o -name '.cvs'`
	tar cvfz $(DISTFILE) $(PACKAGE)/
	rm -rf $(PACKAGE)/

dist: $(DISTFILE)

sign: $(DISTFILE)
	gpg --detach-sign --armor $?
