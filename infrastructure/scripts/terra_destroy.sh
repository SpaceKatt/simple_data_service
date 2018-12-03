cd ../terra

terraform destroy -var-file=variables.tfvars -var-file=packer_build_vars.tfvars
