resource "aws_glue_crawler" "bank_raw_crawler" {
  name          = "bank-raw-csv-crawler"
  role          = aws_iam_role.glue_service_role.arn
  database_name = aws_glue_catalog_database.curated.name
  table_prefix  = "bank_"

  s3_target {
    path = "s3://${aws_s3_bucket.raw_csv_bucket.bucket}/"
  }

  configuration = jsonencode({
    Version = 1.0
    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
    }
  })

  schedule = "cron(0 12 * * ? *)" # Optional: Daily at 12:00 UTC

  schema_change_policy {
    delete_behavior = "DEPRECATE_IN_DATABASE"
    update_behavior = "UPDATE_IN_DATABASE"
  }

  tags = {
    Name        = "BankRawCSVCrawler"
    Environment = "Dev"
  }
}
