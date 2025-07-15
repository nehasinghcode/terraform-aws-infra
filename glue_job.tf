resource "aws_glue_job" "bank_csv_to_parquet" {
  name     = "bank_csv_to_parquet_job"
  role_arn = aws_iam_role.glue_job_role.arn

  command {
    name            = "glueetl"
    script_location = "s3://finco-dev-glue-scripts-us-east-1-001/scripts/bank_csv_to_parquet.py"
    python_version  = "3"
  }

  max_retries      = 0
  timeout          = 10
  glue_version     = "4.0"
  number_of_workers = 2
  worker_type       = "G.1X"
}
