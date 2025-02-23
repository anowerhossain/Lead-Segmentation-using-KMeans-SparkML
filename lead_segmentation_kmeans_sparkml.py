import warnings

def warn(*args, **kwargs):
    pass

# Suppress warnings generated by your code
warnings.warn = warn
warnings.filterwarnings('ignore')

# Initialize FindSpark to simplify using Apache Spark with Python
import findspark
findspark.init()

# Import necessary PySpark modules for clustering and feature engineering
from pyspark.ml.clustering import KMeans
from pyspark.ml.feature import VectorAssembler
from pyspark.sql import SparkSession

# Step 1: Create a SparkSession
# The SparkSession is the entry point to programming with Spark
spark = SparkSession.builder.appName("SaaS Lead Qualification Clustering").getOrCreate()

# Step 2: Load the dataset into a DataFrame
# Using spark.read.csv to load the data
# header=True indicates the CSV file has a header row
# inferSchema=True allows Spark to infer data types for columns
customer_data = spark.read.csv("saas_leads.csv", header=True, inferSchema=True)

# Step 3: Print the schema of the DataFrame
# This helps in understanding the structure and data types of the dataset
customer_data.printSchema()

# Step 4: Display the first 5 rows of the dataset
# Provides a quick preview of the data
customer_data.show(n=5, truncate=False)

# Step 5: Assemble the features into a single vector column
# Define the relevant features for identifying qualified leads
feature_cols = [
    'Page_Visits',           # Number of pages visited
    'Time_Spent',            # Total time spent on the platform (minutes)
    'Demo_Requested',        # Whether a demo was requested (1/0)
    'Trial_Signups',         # Number of trial signups
    'Emails_Clicked',        # Number of marketing emails clicked
    'Webinar_Attendance',    # Whether the lead attended a webinar (1/0)
    'Feature_Usage',         # Number of features used during trial
    'Support_Interactions',  # Number of interactions with support
    'Industry_Score',        # Score based on industry relevance
    'Company_Size',          # Size of the lead's company (number of employees)
    'Revenue_Potential',     # Estimated revenue potential
    'Account_Creation_Days', # Days since account creation
    'Bounce_Rate',           # Website bounce rate
    'Device_Type',           # Type of device used (1: Mobile, 2: Desktop)
    'Referrals',             # Number of referrals made by the lead
    'Login_Frequency',       # Number of times the lead logged in
    'Days_Active',           # Number of distinct days the lead was active
    'Onboarding_Completion', # Whether the onboarding process was completed (1/0)
    'Guided_Tour_Completion',# Whether the guided product tour was completed (1/0)
    'Integration_Attempts',  # Number of times the lead attempted integrations
    'Content_Engagement',    # Number of blogs, whitepapers, or resources accessed
    'Customizations_Made'    # Number of customizations made in the product settings
]
# Use VectorAssembler to combine these features into a single column
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")
customer_transformed_data = assembler.transform(customer_data)

# Step 6: Define the number of clusters for KMeans
# Here, we are setting the number of clusters to 2 (Qualified and Not Qualified)
number_of_clusters = 2

# Step 7: Create a KMeans model
# The KMeans model is initialized with the specified number of clusters
kmeans = KMeans(k=number_of_clusters, seed=1, featuresCol="features", predictionCol="prediction")

# Step 8: Train the KMeans model on the dataset
# The model is fitted to the transformed dataset with feature vectors
model = kmeans.fit(customer_transformed_data)

# Step 9: Make predictions using the trained model
# The predictions add a new column 'prediction' to the dataset
predictions = model.transform(customer_transformed_data)

# Step 10: Display the clustering results
# This shows the assigned cluster for each customer
predictions.select('Page_Visits', 'Time_Spent', 'Demo_Requested', 'prediction').show(500)

# Step 11: Display the number of customers in each cluster
# Group by the 'prediction' column and count the number of rows in each cluster
predictions.groupBy('prediction').count().show()

# Step 12: Save the clustering results to a CSV file for further analysis
# You can save the results to a file or database
predictions.select('Page_Visits', 'Time_Spent', 'Demo_Requested', 'prediction')\
    .write.csv("clustering_results.csv", header=True, mode="overwrite")

# Step 13: Stop the SparkSession
# This releases the resources held by the SparkSession
spark.stop()
