#!/usr/bin/env bash
set -e
echo -e "\n==== TOOL INFO ===="
FULLNAME="$(python3 setup.py --fullname)"
echo "FULLNAME: $FULLNAME"

echo -e "\n---Installing Delivery Tool---"

pushd 'delivery_tool'
rm -f 'ansible.zip'
zip -r 'ansible.zip' 'ansible'
popd

rm -rf "$FULLNAME"
pip install -t "$FULLNAME" .

echo -e "\n---Build Delivery Tool python executable archive---"
python3 -m zipapp "$FULLNAME" --main 'delivery_tool.main:main' --python '/usr/bin/python3' --output "${FULLNAME}.pyz"
rm -rf "$FULLNAME"
