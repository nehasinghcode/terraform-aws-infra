resource "aws_glue_job" "bank_csv_to_parquet_job" {
  name     = "bank_csv_to_parquet_job"
  role_arn = aws_iam_role.glue_service_role.arn
  glue_version      = "4.0"
  max_capacity      = 2
  number_of_workers = 2
  worker_type       = "G.1X"
  timeout           = 10

  command {
    name            = "glueetl"
    script_location = "s3://${aws_s3_bucket.curated_csv_bucket.bucket}/scripts/bank_csv_to_parquet.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language"        = "python"
    "--TempDir"             = "s3://${aws_s3_bucket.curated_csv_bucket.bucket}/temp/"
    "--enable-metrics"      = "true"
    "--enable-continuous-cloudwatch-log" = "true"
  }

  tags = {
    "Name"        = "BankCSVToParquetJob"
    "Environment" = "Dev"
  }
}
