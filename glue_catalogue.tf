resource "aws_glue_catalog_database" "curated" {
  name        = var.glue_database_name
  description = "Curated zone for transformed bank marketing data"
}

resource "aws_glue_catalog_table" "bank_data_parquet" {
  name          = "bank_data_parquet"
  database_name = aws_glue_catalog_database.curated.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.curated_csv_bucket.bucket}/bank_data_parquet/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"
    compressed    = false
    number_of_buckets = -1

    ser_de_info {
      name                  = "parquet"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    columns = [
      { name = "age",        type = "int" },
      { name = "job",        type = "string" },
      { name = "marital",    type = "string" },
      { name = "education",  type = "string" },
      { name = "default",    type = "string" },
      { name = "balance",    type = "int" },
      { name = "housing",    type = "string" },
      { name = "loan",       type = "string" },
      { name = "contact",    type = "string" },
      { name = "day",        type = "int" },
      { name = "month",      type = "string" },
      { name = "duration",   type = "int" },
      { name = "campaign",   type = "int" },
      { name = "pdays",      type = "int" },
      { name = "previous",   type = "int" },
      { name = "poutcome",   type = "string" },
      { name = "y",          type = "string" }
    ]

    stored_as_sub_directories = false
  }

  partition_keys = [
    {
      name = "job"
      type = "string"
    }
  ]
}

