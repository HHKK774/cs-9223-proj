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
# schemaRecipe.printSchema()

indexed_schemaRecipe = schemaRecipe.withColumn('index1', F.monotonically_increasing_id())
indexed_schemaRecipe.createOrReplaceTempView("indexed_schemaRecipe")
query = """
select row_number() over (order by index1) as index, name, ingredient
from indexed_schemaRecipe
"""
indexed_schemaRecipe = spark.sql(query)
indexed_schemaRecipe = indexed_schemaRecipe.withColumn('index', F.col('index')-1)
lines1 = indexed_schemaRecipe.rdd
lines1 = lines1.map(lambda x: (str(x[0]), str(x[1]), str(x[2])))
lines1 = lines1.map(lambda x: (x[0], (x[1], x[2])))

lines2 = sc.textFile('recipe_final.csv').mapPartitions(lambda x: reader(x))
lines2 = lines2.mapPartitionsWithIndex(lambda idx, it: islice(it, 1, None) if idx == 0 else it)
lines2 = lines2.map(lambda x: (x[0], (x[1], x[4], x[6], x[7], x[12], x[13])))

lines3 = lines2.join(lines1)
lines3 = lines3.map(lambda x: (x[0], x[1][0], x[1][1]))

def int_index(line):
    index = int(line[0])
    return (index, line[1], line[2])

lines3 = lines3.map(int_index)

lines3 = lines3.map(lambda x: Row(index=x[0], name=x[2][0], ingredient=x[2][1], course_cuisine=x[1][0], flavor=x[1][1], small_image=x[1][2], rating=x[1][3], big_image=x[1][4], ingredient_amount=x[1][5]))

inner_join = sqlContext.createDataFrame(lines3)
inner_join = inner_join.na.drop(subset=["name", "ingredient", "index", "course_cuisine", "flavor", "small_image", "rating", "big_image", "ingredient_amount"])
inner_join1 = inner_join.filter("flavor != ''")
inner_join1.count()

inner_join2 = inner_join1.filter("small_image != ''")
inner_join2.count()

inner_join2 = inner_join2.sort('index')
inner_join2.createOrReplaceTempView("inner_join2")
query = """
select row_number() over (order by index) as index, name, ingredient, course_cuisine, flavor, small_image, rating, big_image, ingredient_amount
from inner_join2
"""
inner_join2 = spark.sql(query)
inner_join2  = inner_join2 .withColumn('index', F.col('index')-1)
inner_join2.count()

inner_join2.select("*").write.save("inner_join_201912142215", format="csv")