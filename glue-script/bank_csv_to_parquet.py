import sys
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame

# Initialize contexts
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# Parse arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'raw_s3_path'])
raw_s3_path = args['raw_s3_path']

# Read CSV file from raw S3 path passed by Lambda
df = spark.read.csv(raw_s3_path, header=True, inferSchema=True)

# Data cleaning: drop rows with nulls
df_cleaned = df.dropna()

# Transformation: filter age > 30 and balance > 0
df_transformed = df_cleaned.filter((df_cleaned['age'] > 30) & (df_cleaned['balance'] > 0))

# Aggregation: average balance by job
agg_df = df_transformed.groupBy("job").agg({"balance": "avg"}).withColumnRenamed("avg(balance)", "avg_balance")

# Output location
output_path = "s3://finco-dev-curated-csv-data-us-east-1-001/bank_data_parquet/"

# Write as Parquet, partitioned by job
agg_df.write.mode("overwrite").partitionBy("job").parquet(output_path)

# Convert to DynamicFrame for Glue Catalog
dyf = DynamicFrame.fromDF(agg_df, glueContext, "dyf")

# Write to Glue Data Catalog
glueContext.write_dynamic_frame.from_options(
    frame=dyf,
    connection_type="s3",
    format="parquet",
    connection_options={
        "path": output_path,
        "partitionKeys": ["job"]
    },
    transformation_ctx="write_to_catalog"
)
