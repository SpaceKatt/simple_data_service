#!/usr/bin/env bash
cd ../packer

packer build build.json | tee ../logs/packout_out.txt

cat ../logs/packout_out.txt | tail -n 2 \
    | sed '$ d' \
    | sed "s/us-west-2: /simple-data-service-ami = \"/" \
    | sed -e 's/[[:space:]]*$/\"/' > ../terra/packer_build_vars.tfvars

cat ../terra/packer_build_vars.tfvars
