resource "aws_sns_topic" "glue_job_notifications" {
  name = "glue-job-notifications"
}

resource "aws_sns_topic_subscription" "email_subscription" {
  topic_arn = aws_sns_topic.glue_job_notifications.arn
  protocol  = "email"
  endpoint  = "nehasingh.bansal@gmail.com"
}
