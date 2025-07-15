resource "aws_glue_catalog_database" "curated" {
  name        = var.glue_database_name
  description = "Curated zone for transformed bank marketing data"
}
