#!/bin/sh
echo begin backup
/bin/cp -r /opt/hybrid /opt/hybrid-`date +%Y%m%d-%H%M%S`
echo begin cp files
rsync -avc --filter="- *.pyc" /opt/hybrid-upload/ /opt/hybrid/
echo begin restart port: 8101
supervisorctl restart hb-8101
echo begin sync to web2
rsync -a -v -e ssh -c --filter="- *.pyc" /opt/hybrid/ web2:/opt/hybrid/
ssh web2 "supervisorctl restart hb-8101"

echo done!