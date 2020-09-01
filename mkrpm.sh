#!/bin/bash
spectool -g -R tsm-exporter-el7.spec
rpmbuild --define "dist .el7" -ba tsm-exporter-el7.spec
