#!/bin/bash
sudo echo 3 > /proc/sys/vm/drop_caches
sudo swapoff -a
sudo swapon -a
