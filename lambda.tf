resource "aws_lambda_function" "trigger_glue_job" {
  function_name = "trigger-glue-job-on-upload"
  handler       = "glue_trigger.lambda_handler"
  runtime       = "python3.9"
  role          = aws_iam_role.lambda_glue_trigger_role.arn
  filename      = "${path.module}/lambda_script/glue_trigger.zip"
  source_code_hash = filebase64sha256("${path.module}/lambda_script/glue_trigger.zip")
  timeout       = 30
  memory_size   = 128

  environment {
    variables = {
      GLUE_JOB_NAME = aws_glue_job.bank_csv_to_parquet.name
    }
  }
}

resource "aws_lambda_permission" "allow_s3_trigger" {
  statement_id  = "AllowExecutionFromS3"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.trigger_glue_job.function_name
  principal     = "s3.amazonaws.com"
  source_arn    = aws_s3_bucket.raw_csv_bucket.arn
}
