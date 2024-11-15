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

echo "$TAR --create --gz --verbose --file PO3.tar.gz --transform \"s,^,PO3/,\" TM.py reverse.py traces.txt traces_tokenized.txt"
$TAR --create --gz --verbose --file PO3.tar.gz --transform "s,^,PO3/," TM.py reverse.py traces.txt traces_tokenized.txt
