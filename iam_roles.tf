resource "aws_iam_role" "lambda_glue_trigger_role" {
  name = "lambda-glue-trigger-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      },
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_policy_attachment" "lambda_basic_execution" {
  name       = "lambda-basic-execution"
  roles      = [aws_iam_role.lambda_glue_trigger_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_policy" "glue_start_policy" {
  name = "lambda-start-glue-job"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "glue:StartJobRun"
        ],
        Effect   = "Allow",
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_policy_attachment" "lambda_start_glue" {
  name       = "lambda-start-glue-job-attachment"
  roles      = [aws_iam_role.lambda_glue_trigger_role.name]
  policy_arn = aws_iam_policy.glue_start_policy.arn
}
