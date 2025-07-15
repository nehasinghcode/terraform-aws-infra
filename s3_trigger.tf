# S3 Notification to trigger Lambda on object creation
resource "aws_s3_bucket_notification" "trigger_lambda_on_upload" {
  bucket = aws_s3_bucket.raw_csv_bucket.id

  lambda_function {
    lambda_function_arn = aws_lambda_function.trigger_glue_job.arn
    events              = ["s3:ObjectCreated:*"]
    filter_suffix       = ".csv"  # Only trigger for .csv files
  }

  depends_on = [
    aws_lambda_permission.allow_s3_trigger
  ]
}
