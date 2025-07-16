resource "aws_glue_catalog_database" "curated" {
  name        = var.glue_database_name
  description = "Curated zone for transformed bank marketing data"
}

resource "aws_glue_catalog_table" "bank_data_parquet" {
  name          = "bank_data_parquet"
  database_name = aws_glue_catalog_database.curated.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://${aws_s3_bucket.curated_csv_bucket.bucket}/curated_data/"
    input_format  = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat"
    compressed    = false
    number_of_buckets = -1

    ser_de_info {
      name                  = "parquet"
      serialization_library = "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"
    }

    stored_as_sub_directories = false

    columns {
      name = "age"
      type = "int"
    }
    columns {
      name = "job"
      type = "string"
    }
    columns {
      name = "marital"
      type = "string"
    }
    columns {
      name = "education"
      type = "string"
    }
    columns {
      name = "default"
      type = "int"
    }
    columns {
      name = "balance"
      type = "int"
    }
    columns {
      name = "housing"
      type = "int"
    }
    columns {
      name = "loan"
      type = "int"
    }
    columns {
      name = "contact"
      type = "string"
    }
    columns {
      name = "day"
      type = "int"
    }
    columns {
      name = "duration"
      type = "int"
    }
    columns {
      name = "campaign"
      type = "int"
    }
    columns {
      name = "pdays"
      type = "int"
    }
    columns {
      name = "previous"
      type = "int"
    }
    columns {
      name = "poutcome"
      type = "string"
    }
    columns {
      name = "y"
      type = "string"
    }
  }
  columns {
      name = "avg_balance"
      type = "int"
    }

columns {
      name = "avg_duration"
      type = "int"
    }

  partition_keys {
    name = "month"
    type = "string"
  }
}


resource "aws_glue_catalog_table" "bank_raw_table" {
  name          = "bank_raw_data"
  database_name = aws_glue_catalog_database.curated.name
  table_type    = "EXTERNAL_TABLE"

  storage_descriptor {
    location      = "s3://finco-dev-raw-csv-data-us-east-1-001/"
    input_format  = "org.apache.hadoop.mapred.TextInputFormat"
    output_format = "org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat"

    ser_de_info {
      name                  = "OpenCSVSerde"
      serialization_library = "org.apache.hadoop.hive.serde2.OpenCSVSerde"

      parameters = {
        "separatorChar" = ";"
        "quoteChar"     = "\""
        "escapeChar"    = "\\"
      }
    }

    columns {
      name = "age"
      type = "int"
    }
    columns {
      name = "job"
      type = "string"
    }
    columns {
      name = "marital"
      type = "string"
    }
    columns {
      name = "education"
      type = "string"
    }
    columns {
      name = "default"
      type = "string"
    }
    columns {
      name = "balance"
      type = "int"
    }
    columns {
      name = "housing"
      type = "string"
    }
    columns {
      name = "loan"
      type = "string"
    }
    columns {
      name = "contact"
      type = "string"
    }
    columns {
      name = "day"
      type = "int"
    }
    columns {
      name = "month"
      type = "string"
    }
    columns {
      name = "duration"
      type = "int"
    }
    columns {
      name = "campaign"
      type = "int"
    }
    columns {
      name = "pdays"
      type = "int"
    }
    columns {
      name = "previous"
      type = "int"
    }
    columns {
      name = "poutcome"
      type = "string"
    }
    columns {
      name = "y"
      type = "string"
    }
  }

  parameters = {
    "classification"         = "csv"
    "skip.header.line.count" = "1"
    "compressionType"        = "none"
    "typeOfData"             = "file"
  }
}
