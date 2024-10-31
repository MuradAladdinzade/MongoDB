# %%
import pandas as pd
import json
import json
from pymongo import MongoClient

# read csv files
companies= pd.read_csv("./mp2-data/companies.csv")
edu= pd.read_csv("./mp2-data/education_and_skills.csv")
employment= pd.read_csv("./mp2-data/employment_details.csv")
industry= pd.read_csv("./mp2-data/industry_info.csv")
jobs= pd.read_csv("./mp2-data/jobs.csv")
# Define function to categorize experience levels
def categorize_experience(years):
    if years < 2:
        return 'Entry Level'
    elif 2 <= years < 5:
        return 'Mid Level'
    else:
        return 'Senior Level'

# Apply the function to create a new column
jobs['experience_level'] = jobs['years_of_experience'].apply(categorize_experience)


# drop id columns as all mathning rows are relevant to particular job posting, so id should not be duplicated
for df in [companies, edu, employment]:
    df.drop(columns=['job_id', 'id'], inplace=True, errors='ignore')  # 'errors="ignore"' to skip if columns don't exist
    





# %%
# Convert the cleaned dataframe to a dictionary in JSON format
jobs_pov = jobs.to_dict(orient='records')
jobs_pov





# %%
#creating jobs_pov 
for i in range(len(jobs_pov)):
    # creating nested field
    jobs_pov[i]['company_info'] = companies.iloc[i].to_dict()
    # drop id from industry
    industry.drop(columns=['job_id', 'id'], inplace=True, errors='ignore')
    # creating nested fields
    jobs_pov[i]['industry_info'] = industry.iloc[i].to_dict()
    jobs_pov[i]['education_and_skills'] = edu.iloc[i].to_dict()
    jobs_pov[i]['employment_details'] = employment.iloc[i].to_dict()
    


# %%
# create array for job_important_pov
job_important_pov = []
# creating 2nd collection: job_important_pov
# getting important fields from the detailed collection
for i in range(len(jobs_pov)):
    # Create a dictionary for the important fields
    job_info = {
        'id': jobs_pov[i]['id'],
        'title': jobs_pov[i]['title'],
        'description': jobs_pov[i]['description'],
        'years_of_experience': jobs_pov[i]['years_of_experience'],
        'company_info': {
            'name': jobs_pov[i]['company_info']['name'],
            'location': jobs_pov[i]['company_info']['location']
        },
        'industry_info': {
            'industry_name': jobs_pov[i]['industry_info']['industry_name']
        },
        'average_salary': jobs_pov[i]['employment_details']['average_salary']
    }
    
    # Append the dictionary to the job_important_pov list
    job_important_pov.append(job_info)

# Now job_important_pov contains the desired dictionaries
job_important_pov[1]


# Save to a JSON files
with open('job_important_pov.json', 'w') as json_file:
    json.dump(job_important_pov, json_file, indent=4)

with open('job_detailed_pov.json', 'w') as json_file:
    json.dump(jobs_pov, json_file, indent=4)



## here it import data to mongodb

# Step 1: Establish a connection to MongoDB
client = MongoClient("mongodb://root:examplepassword@mongodb:27017/", 27017)

# Step 2: Select the 'careerhub' database
db = client['careerhub']

# Step 3: Select the two collections
detailed_collection = db['jobs_detailed']
important_collection = db['jobs_important']

# Step 4: Open the JSON file and load the data (assuming it's a valid JSON array)
with open('job_detailed_pov.json', 'r') as detailed_file, \
     open('job_important_pov.json', 'r') as important_file:
    
    detailed_data = json.load(detailed_file)  # Load JSON array for detailed collection
    important_data = json.load(important_file)  # Load JSON array for important collection

# Step 5: Insert the data into the respective collections
if isinstance(detailed_data, list):  # Check if the data is a list of documents
    detailed_collection.insert_many(detailed_data)  # Insert multiple documents into detailed collection
else:
    detailed_collection.insert_one(detailed_data)   # Insert a single document into detailed collection

if isinstance(important_data, list):  # Check if the data is a list of documents
    important_collection.insert_many(important_data)  # Insert multiple documents into important collection
else:
    important_collection.insert_one(important_data)   # Insert a single document into important collection

client.close()
print("Data has been successfully inserted into both collections.")
