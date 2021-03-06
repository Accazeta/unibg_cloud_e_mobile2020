###### TEDx-Load-Aggregate-Model
######

import sys
import json
import pyspark
from pyspark.sql.functions import col, collect_list, array_join

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

##### FROM FILES
tedx_dataset_path = "s3://unibg-tedx-data-bucket/tedx_dataset.csv"

###### READ PARAMETERS
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

##### START JOB CONTEXT AND JOB
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session #la sessione di spark viene presa da glue
job = Job(glueContext)
job.init(args['JOB_NAME'], args)


#### READ INPUT FILES TO CREATE AN INPUT DATASET
tedx_dataset = spark.read.option("header","true").option("quote", "\"").option("escape", "\"").csv(tedx_dataset_path) 
    
    #se un json devo mettere .csv#devo dire che il testo all'interno le virgolette devo considerarlo come contenuto unico.
    
tedx_dataset.printSchema()


#### FILTER ITEMS WITH NULL POSTING KEY
count_items = tedx_dataset.count()
count_items_null = tedx_dataset.filter("idx is not null").count() #filtra i dati e togle i valori nulli

print(f"Number of items from RAW DATA {count_items}")
print(f"Number of items from RAW DATA with NOT NULL KEY {count_items_null}")



## READ TAGS DATASET
tags_dataset_path = "s3://unibg-tedx-data-bucket/tags_dataset.csv"
tags_dataset = spark.read.option("header","true").csv(tags_dataset_path)

# CREATE THE AGGREGATE MODEL, ADD TAGS TO TEDX_DATASET
tags_dataset_agg = tags_dataset.groupBy(col("idx").alias("idx_ref")).agg(collect_list("tag").alias("tags"))
tags_dataset_agg.printSchema()
tedx_dataset_agg = tedx_dataset.join(tags_dataset_agg, tedx_dataset.idx == tags_dataset_agg.idx_ref, "left").drop("idx_ref").select(col("idx").alias("_id"), col("*")).drop("idx")
    #left join perchè può essere che qualche talk non abbia tag
 #non voglio portarmi dietro il campo idx_ref
  #cambio idx in _id => cosi mongo db non mette il suo id ma mette quello che ho io
tedx_dataset_agg.printSchema()

#PRIMO HOMEWORK:
#ADD WATCHNEXT:
watchnext_dataset_path = "s3://unibg-tedx-data-bucket/watch_next_dataset.csv"
watchnext_dataset = spark.read.option("header","true").option("quote","\"").option("escape","\"").csv(watchnext_dataset_path)
#ADD WATCHNEXT TO THE MODEL
watchnext_dataset_agg = watchnext_dataset.groupBy(col("idx").alias("idx_ref")).agg(collect_list("watch_next_idx").alias("watch_next"))
watchnext_dataset_agg.printSchema()
tedx_dataset_agg = tedx_dataset_agg.join(watchnext_dataset_agg, tedx_dataset_agg._id == watchnext_dataset_agg.idx_ref, "left").drop("idx_ref").select(col("watch_next"),col("*"))
tedx_dataset_agg.printSchema()

#READ TEDUPLOADER:
teduploader_dataset_path = "s3://unibg-tedx-data-bucket/tedUploader.csv"
teduploader_dataset = spark.read.option("header","true").csv(teduploader_dataset_path)

teduploader_dataset.printSchema()
#ADD TEDUPLOADERTOMODEL:
#tedx_dataset_agg = tedx_dataset_agg.join(teduploader_dataset, tedx_dataset_agg._id == teduploader_dataset.idxVideo, "left").drop("idxVideo").select(col("email"),col("*"))
#teduploader_dataset_agg = tedx_dataset_agg.join(teduploader_dataset, tedx_dataset_agg._id == teduploader_dataset.idxVideo, "left").drop("_id").select(col("email"),col("main_speaker"))
teduploader_dataset_agg = teduploader_dataset.join(tedx_dataset, teduploader_dataset.idxVideo == tedx_dataset.idx, "left").select(col("idxUser").alias("_id"),"email","main_speaker","idxVideo")
teduploader_dataset.printSchema()
teduploader_dataset_agg = teduploader_dataset_agg.groupBy("_id","email","main_speaker").agg(collect_list("idxVideo").alias("idxVideo"))
teduploader_dataset.printSchema()


mongo_uri = "mongodb://mycluster-shard-00-00-6zdcg.mongodb.net:27017,mycluster-shard-00-01-6zdcg.mongodb.net:27017,mycluster-shard-00-02-6zdcg.mongodb.net:27017"

write_mongo_options = { 
    "uri": mongo_uri,
    "database": "unibg_tedx",
    "collection": "tedx_data",
    "username": "admin",
    "password": "66lc8tjOLtKZDBfl",
    "ssl": "true",
    "ssl.domain_match": "false"}#vado ad impostare le opzioni di configurazione
from awsglue.dynamicframe import DynamicFrame
tedx_dataset_dynamic_frame = DynamicFrame.fromDF(tedx_dataset_agg, glueContext, "nested")
glueContext.write_dynamic_frame.from_options(tedx_dataset_dynamic_frame, connection_type="mongodb", connection_options=write_mongo_options)
#WRITE THE NEW COLLECTION:
write_mongo_options["collection"] = "tedx_uploader_email"
teduploader_dataset_dynamic_frame = DynamicFrame.fromDF(teduploader_dataset_agg, glueContext, "nested")
glueContext.write_dynamic_frame.from_options(teduploader_dataset_dynamic_frame, connection_type="mongodb", connection_options=write_mongo_options)
