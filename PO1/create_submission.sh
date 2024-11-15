#!/usr/bin/env bash

if [ "$(uname)" == "Darwin" ]; then
    if command -v gtar &> /dev/null; then
        TAR="gtar"
    else
        echo "On macOS GNU tar is needed, since the default tar does not support transform"
        echo "Install using \`brew install gnu-tar\`"
        exit 1
    fi
else
    TAR="tar"
fi

echo "$TAR --create --gz --verbose --file PO1.tar.gz --transform \"s,^,PO1/,\" FA.py lexer.py traces.txt verify.py"
$TAR --create --gz --verbose --file PO1.tar.gz --transform "s,^,PO1/," FA.py lexer.py traces.txt verify.py
