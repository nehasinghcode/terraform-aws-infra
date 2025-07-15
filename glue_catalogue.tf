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

    stored_as_sub_directories = false

    column {
      name = "age"
      type = "int"
    }
    column {
      name = "job"
      type = "string"
    }
    column {
      name = "marital"
      type = "string"
    }
    column {
      name = "education"
      type = "string"
    }
    column {
      name = "default"
      type = "string"
    }
    column {
      name = "balance"
      type = "int"
    }
    column {
      name = "housing"
      type = "string"
    }
    column {
      name = "loan"
      type = "string"
    }
    column {
      name = "contact"
      type = "string"
    }
    column {
      name = "day"
      type = "int"
    }
    column {
      name = "month"
      type = "string"
    }
    column {
      name = "duration"
      type = "int"
    }
    column {
      name = "campaign"
      type = "int"
    }
    column {
      name = "pdays"
      type = "int"
    }
    column {
      name = "previous"
      type = "int"
    }
    column {
      name = "poutcome"
      type = "string"
    }
    column {
      name = "y"
      type = "string"
    }
  }

  partition_keys {
    name = "job"
    type = "string"
  }
}

