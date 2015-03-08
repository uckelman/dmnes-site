#!/bin/bash

(echo -ne '\n\0' ; (cat ../site/templates/*.html ; (find ../site/dmnes/bib ../site/dmnes/CNFs ../site/dmnes/VNFs -type f -print0 | xargs -0 -- xsltproc strip.xsl )) | tr -d '\n' | sed -e 's/./&\x00/g') | LC_COLLATE=C sort -zu | tr -d '\0' >char
