import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Get parameters
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'raw_s3_path'])

raw_s3_path = args['raw_s3_path']
output_path = "s3://finco-dev-curated-csv-data-us-east-1-001/bank_data_parquet/"

# Initialize Glue and Spark
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# ✅ Read CSV with semicolon delimiter
df = spark.read.option("header", True)\
               .option("delimiter", ";")\
               .option("quote", "\"")\
               .csv(raw_s3_path)

# ✅ Basic cleaning: Remove rows with null age and cast types
df_cleaned = df.dropna(subset=["age"])\
    .withColumn("age", df["age"].cast("int"))\
    .withColumn("balance", df["balance"].cast("int"))\
    .withColumn("duration", df["duration"].cast("int"))

# ✅ Example aggregation: average balance by job and marital status
df_agg = df_cleaned.groupBy("job", "marital")\
                   .avg("balance")\
                   .withColumnRenamed("avg(balance)", "avg_balance")

# ✅ Join aggregated data back for reporting
df_final = df_cleaned.join(df_agg, on=["job", "marital"], how="left")

# ✅ Write to Parquet and partition by job
df_final.write.mode("overwrite")\
    .partitionBy("job")\
    .parquet(output_path)

# ✅ Register in Glue Catalog
glueContext.create_dynamic_frame_from_options(
    connection_type="s3",
    connection_options={"paths": [output_path]},
    format="parquet"
).toDF().createOrReplaceTempView("bank_view")

# ✅ Create or update Glue Catalog Table
datasink = glueContext.write_dynamic_frame.from_options(
    frame=glueContext.create_dynamic_frame.from_catalog(
        database="bank_marketing_curated",
        table_name="bank_data_parquet",
        transformation_ctx="datasource0"
    ),
    connection_type="s3",
    connection_options={
        "path": output_path,
        "partitionKeys": ["job"]
    },
    format="parquet",
    transformation_ctx="datasink"
)

job.commit()
