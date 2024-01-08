#!/usr/bin/env bash

IPV4_ADDRESS_CHECKER=${IPV4_ADDRESS_CHECKER:-"http://169.254.169.254/latest/meta-data/public-ipv4"}

echo ${IPV4_ADDRESS_CHECKER}
