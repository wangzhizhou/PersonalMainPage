#!/usr/bin/env bash
#-*- utf-8 -*-

pkill -9 hugo
hugo -s Orz server -D &
sleep 2s
open http://localhost:1313

