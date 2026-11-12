
terraform {
  backend "local" {
    path = ".terraform-state/terraform.tfstate"
  }

  required_version = ">= 1.17.0, < 2.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}
