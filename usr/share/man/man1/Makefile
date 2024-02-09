# vim:set noet ts=8
# All Linux/unix specific data installation by "make -C src/imediff/unix-data"

all: manpages 


# Generate manpage from DocBook XML
#
# Require xsltproc
#   For Debian, xsltproc binary package.
#   For others, xsltproc is available from the libxsl source which uses libxml2.
#   See http://xmlsoft.org/xslt/ for more.
#
# In order to have flexibility for the manpage, I commit generated manpage in advance.
# If you make eny manual touch up, please add "sed -i ..." script here etc.
#
# This approach should make build process more robust against some xslt upstream change etc.
#
MANPAGES = imediff.1 git-ime.1

%.1:  %.xml
	xsltproc --novalid /usr/share/sgml/docbook/stylesheet/xsl/nwalsh/manpages/docbook.xsl $?

# This is used by the upstream
manpages:  $(MANPAGES)

distclean: clean

clean:
	rm -f $(MANPAGES)

