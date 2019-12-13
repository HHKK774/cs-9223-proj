from pyspark import SparkConf, SparkContext
from pyspark import SQLContext
from pyspark.sql import Row
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StringType
from itertools import islice
from pyspark.sql.functions import col
from pyspark.sql import functions as F
from csv import reader

def merge_ingredients(line):
    name = line[0]
    ingredients = []
    for i in range(1, len(line)):
        ingredients.append(line[i])
    return [name, ingredients]

lines1 = sc.textFile('csvData_beforeClean.csv')
lines1 = lines1.mapPartitions(lambda x: reader(x))
lines1 = lines1.map(merge_ingredients)
recipe = lines1.map(lambda x: Row(name=x[0], ingredient=str(x[1])))
schemaRecipe = sqlContext.createDataFrame(recipe)
schemaRecipe.printSchema()

indexed_schemaRecipe = schemaRecipe.withColumn('index1', F.monotonically_increasing_id())
indexed_schemaRecipe.createOrReplaceTempView("indexed_schemaRecipe")
query = """
select row_number() over (order by index1) as index, name, ingredient
from indexed_schemaRecipe
"""
indexed_schemaRecipe = spark.sql(query)

schemaRecipes = sqlContext.read.csv("recipe_final.csv", header = True, inferSchema = True)
columns_to_drop = ['id', 'course', 'cuisine', 'another_small_image', 'provider', 'time', 'serving_number', 'nutrition','hie_label','dbscan_label', 'name']
schemaRecipes = schemaRecipes.drop(*columns_to_drop)

inner_join = indexed_schemaRecipe.join(schemaRecipes, 'index', 'inner')
inner_join = inner_join.na.drop(subset=["name", "ingredient", "index", "course_cuisine", "flavor", "small_image", "rating", "big_image", "ingredient_amount"])
inner_join.createOrReplaceTempView("inner_join")
query = """
select row_number() over (order by index) as index, name, ingredient, course_cuisine, flavor, small_image, rating, big_image, ingredient_amount
from inner_join
"""
inner_join = spark.sql(query)
inner_join.select("*").write.save("inner_join_201912131529", format="csv")