#!/usr/bin/env bash
echo "Terraform Apply"

cd ../terra

terraform get 

terraform apply -var-file=variables.tfvars -var-file=packer_build_vars.tfvars -auto-approve=false
