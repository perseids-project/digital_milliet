#!/bin/sh

mv digital_milliet/config.cfg digital_milliet/config.cfg.bak
cat digital_milliet/config.cfg.bak digital_milliet/docker-config.cfg > digital_milliet/config.cfg
