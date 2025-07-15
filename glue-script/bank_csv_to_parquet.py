import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from pyspark.context import SparkContext
from pyspark.sql.functions import col, avg, count
from awsglue.dynamicframe import DynamicFrame

# Initialize Spark and Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Get path passed from Lambda
args = getResolvedOptions(sys.argv, ['raw_s3_path'])
raw_s3_path = args['raw_s3_path']

# Read CSV
df = spark.read.option("header", "true") \
               .option("inferSchema", "true") \
               .option("quote", "\"") \
               .option("multiLine", "true") \
               .option("escape", "\"") \
               .csv(raw_s3_path)

# Clean column names
df = df.toDF(*[c.strip().lower() for c in df.columns])

# Filter
df_filtered = df.filter((col('age') > 30) & (col('balance') > 0))

# Aggregate
df_agg = df_filtered.groupBy('job', 'marital') \
    .agg(
        avg('balance').alias('avg_balance'),
        count('*').alias('record_count')
    )

# Convert to DynamicFrame
dyf = DynamicFrame.fromDF(df_agg, glueContext, "dyf")

# Output details
output_path = "s3://finco-dev-curated-csv-data-us-east-1-001/cleaned_data/"
database_name = "bank_marketing_curated"
table_name = "bank_data_cleaned"

# Write to S3 and register in Glue Catalog
glueContext.write_dynamic_frame.from_options(
    frame=dyf,
    connection_type="s3",
    connection_options={
        "path": output_path,
        "partitionKeys": ["job", "marital"]
    },
    format="parquet"
)

# Register in Glue Catalog
glueContext.catalog_client.create_table(
    DatabaseName=database_name,
    TableInput={
        'Name': table_name,
        'StorageDescriptor': {
            'Columns': [
                {'Name': 'avg_balance', 'Type': 'double'},
                {'Name': 'record_count', 'Type': 'bigint'}
            ],
            'Location': output_path,
            'InputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat',
            'OutputFormat': 'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat',
            'SerdeInfo': {
                'SerializationLibrary': 'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe',
                'Parameters': {'serialization.format': '1'}
            }
        },
        'PartitionKeys': [
            {'Name': 'job', 'Type': 'string'},
            {'Name': 'marital', 'Type': 'string'}
        ],
        'TableType': 'EXTERNAL_TABLE',
        'Parameters': {'classification': 'parquet'}
    }
)
