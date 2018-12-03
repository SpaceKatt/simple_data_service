#!/usr/bin/env bash
echo "Terraform Apply"

cd ../terra

terraform get 

terraform validate -var-file=variables.tfvars -var-file=packer_build_vars.tfvars
