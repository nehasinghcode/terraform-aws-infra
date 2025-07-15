terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

terraform {
  backend "s3" {
    bucket         = "finco-dev-tfstate-bucket"       # Create this S3 bucket manually
    key            = "terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"                 # Optional for locking
  }
}


provider "aws" {
  region = "us-east-1"
}
