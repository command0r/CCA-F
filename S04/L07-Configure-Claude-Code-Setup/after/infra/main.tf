terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

variable "environment" {
  type        = string
  description = "Deployment environment (dev, staging, prod)."
}

resource "aws_s3_bucket" "avatars" {
  bucket = "${var.environment}-usersapi-avatars"

  tags = {
    Environment = var.environment
    Service     = "users-api"
    ManagedBy   = "terraform"
  }
}

resource "aws_s3_bucket_public_access_block" "avatars" {
  bucket = aws_s3_bucket.avatars.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

output "avatars_bucket_name" {
  value       = aws_s3_bucket.avatars.id
  description = "S3 bucket holding user-uploaded avatar images."
}
