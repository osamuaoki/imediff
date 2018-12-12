# Generate manpage from DocBook XML
#
# Require xsltproc
#   For Debian, xsltproc binary package.
#   For others, xsltproc is available from the libxsl source which uses libxml2.
#   See http://xmlsoft.org/xslt/ for more.

MANPAGES = imediff.1 git-ime.1

all: $(MANPAGES)

%.1:  %.xml
	xsltproc --novalid /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl $?


distclean: clean

clean:
	rm -f $(MANPAGES)

