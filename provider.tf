terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "finco-dev-tfstate-bucket"       # Make sure this bucket exists
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"                 # Optional but recommended
  }
}

provider "aws" {
  region = "us-east-1"
}
