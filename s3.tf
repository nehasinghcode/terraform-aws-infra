resource "aws_s3_bucket" "raw_csv_bucket" {
  bucket = "finco-dev-raw-csv-data-us-east-1-001"

  force_destroy = true  # useful for dev/test; use cautiously in prod

  tags = {
    Name        = "RawCSVData"
    Environment = "Production"
    Project     = "FinancialDataPipeline"
    Owner       = "DataEngineeringTeam"
  }
}

# Block all public access
resource "aws_s3_bucket_public_access_block" "public_block" {
  bucket = aws_s3_bucket.raw_csv_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Enable versioning
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.raw_csv_bucket.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Enable server-side encryption (SSE-S3)
resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.raw_csv_bucket.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Optional: Lifecycle rule to move older files to GLACIER or delete
resource "aws_s3_bucket_lifecycle_configuration" "lifecycle" {
  bucket = aws_s3_bucket.raw_csv_bucket.id

  rule {
    id     = "archive-csv-after-30-days"
    status = "Enabled"

    filter {
      prefix = ""
    }

    transition {
      days          = 30
      storage_class = "GLACIER"
    }
  }
}
