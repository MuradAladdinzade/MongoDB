'''Module for serving API requests'''

from app import app
from bson.json_util import dumps, loads
from flask import request, jsonify
import json
import ast # helper library for parsing data from string
from importlib.machinery import SourceFileLoader
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import re

# 1. Connect to the client 
client = MongoClient("mongodb://root:examplepassword@mongodb:27017/", 27017)

# Import the utils module
utils = SourceFileLoader('*', './app/utils.py').load_module()

# 2. Select the database
db = client.careerhub
# Select the collection
detailed_collection = db.jobs_detailed
important_collection = db.jobs_important 


# route decorator that defines which routes should be navigated to this function
@app.route("/") # '/' for directing all default traffic to this function get_initial_response()
def get_initial_response():

    # Message to the user
    message = {
        
        'message': 'Welcome to my website, by Murad'
    }
    resp = jsonify(message)
    # Returning the object
    return resp

# http://localhost:5000/create/jobPost 
@app.route("/create/jobPost", methods=['POST']) # 'http://localhost:5000/create/jobPost ' for directing all default traffic to this function create_post()
def create_post():
    '''
       Function to create a job post and insert into two collections
    '''
    try:
        # Parse the request body
        
        data = request.get_json()
        if not data:
            return "", 400
        
        data = request.json

        # Required fields for validation
        required_fields = ["title", "description", "years_of_experience", "name", "industry_name", "average_salary", "location", "id"]

        # Check for required fields
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field, missing field name is : {field}"}), 400

        # Prepare data for `detailed_collection` (using nested structure)
        detailed_data = {
            "id": data.get("id"),  # Ensure the id is included
            "title": data.get("title"),
            "description": data.get("description"),
            "years_of_experience": data.get("years_of_experience"),
            "detailed_description": data.get("detailed_description"),
            "responsibilities": data.get("responsibilities"),
            "requirements": data.get("requirements"),
            "experience_level": data.get("experience_level"),
            "company_info": {
                "name": data.get("name"),  # Flat field from request mapped into nested structure
                "size": data.get("size"),  # Additional flat field
                "type": data.get("type"),  # Additional flat field
                "location": data.get("location"),  # Direct mapping from location field
                "website": data.get("website"),
                "description": data.get("company_description"),  # Renaming field if needed
                "hr_contact": data.get("hr_contact")
            },
            "industry_info": {
                "industry_name": data.get("industry_name"),  # Flat field mapped to nested structure
                "growth_rate": data.get("growth_rate"),
                "industry_skills": data.get("industry_skills"),
                "top_companies": data.get("top_companies"),
                "trends": data.get("trends")
            },
            "education_and_skills": {
                "required_education": data.get("required_education"),
                "preferred_skills": data.get("preferred_skills")
            },
            "employment_details": {
                "employment_type": data.get("employment_type"),
                "average_salary": data.get("average_salary"),
                "benefits": data.get("benefits"),
                "remote": data.get("remote"),
                "job_posting_url": data.get("job_posting_url"),
                "posting_date": data.get("posting_date"),
                "closing_date": data.get("closing_date")
            }
        }

        # Prepare data for `important_collection` 
        important_data = {
            "id": data.get("id"),  # Ensure the id is included here too
            "title": data.get("title"),
            "description": data.get("description"),
            "years_of_experience": data.get("years_of_experience"),
            "company_info": {
                "name": data.get("name"),  # Flat field mapped into nested structure
                "location": data.get("location")  # Flat field mapped into nested structure
            },
            "industry_info": {
                "industry_name": data.get("industry_name")  # Flat field mapped into nested structure
            },
            "average_salary": data.get("average_salary")
        }

        # Insert into both collections
        detailed_inserted_id = detailed_collection.insert_one(detailed_data).inserted_id
        important_inserted_id = important_collection.insert_one(important_data).inserted_id

        return jsonify({
            "message": "Job post created successfully",
            "detailed_pov_id": str(detailed_inserted_id),
            "important_pov_id": str(important_inserted_id)
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# http://localhost:5000/search_by_job_id/<int:job_id>
@app.route("/search_by_job_id/<int:job_id>", methods=['GET'])
def search_by_job_id(job_id):
    '''
    Function to search and display job details by job_id (using "id" field in the collection)
    '''
    try:
        # Query MongoDB to find the job by the "id" field (an integer)
        job = detailed_collection.find_one({"id": int(job_id)})
        
            
        if not job:
            return jsonify({"error": "Job not found"}), 404
        
        # Convert ObjectId to string
        if "_id" in job:
            job["_id"] = str(job["_id"])

        # Return the whole job document (excluding MongoDB ObjectId if you want)
        return jsonify(job), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# http://localhost:5000/update_by_job_title
@app.route("/update_by_job_title", methods=['POST'])
def update_by_job_id_and_title():
    '''
    Update job details by job ID and job title in both detailed_collection and important_collection.
    Allows updates to description, average_salary, and location.
    '''
    try:
        # Get the job ID and title from the request body
        data = request.get_json()

        if not data or 'id' not in data or 'title' not in data:
            return jsonify({"error": "Both job ID and job title are required"}), 400

        job_id = data.get("id")
        job_title = data.get("title")

        # Search for the job in both collections by job ID and title
        detailed_job = detailed_collection.find_one({"id": job_id, "title": job_title})
        important_job = important_collection.find_one({"id": job_id, "title": job_title})

        if not detailed_job or not important_job:
            return jsonify({"error": "Job not found in one or both collections"}), 404

        # Display current job details from detailed_collection
        current_job_details = {
            "description": detailed_job.get("description"),
            "average_salary": detailed_job.get("average_salary"),
            "location": detailed_job.get("company_info", {}).get("location")
        }

        # New fields to update (if provided)
        updated_description = data.get("description", current_job_details["description"])
        updated_salary = data.get("average_salary", current_job_details["average_salary"])
        updated_location = data.get("location", current_job_details["location"])

        # Validate the new values (add your validation logic if necessary)
        if updated_salary and not isinstance(updated_salary, (int, float)):
            return jsonify({"error": "Average salary must be a number"}), 400

        # Update the job document in detailed_collection
        detailed_update_fields = {
            "description": updated_description,
            "average_salary": updated_salary,
            "company_info.location": updated_location  # Nested update for location
        }

        detailed_result = detailed_collection.update_one(
            {"id": job_id, "title": job_title},
            {"$set": detailed_update_fields}
        )

        # Update the job document in important_collection (only relevant fields)
        important_update_fields = {
            "average_salary": updated_salary,
            "company_info.location": updated_location  # Update location if needed in important_collection
        }

        important_result = important_collection.update_one(
            {"id": job_id, "title": job_title},
            {"$set": important_update_fields}
        )

        # Check if either collection was updated
        if detailed_result.modified_count > 0 or important_result.modified_count > 0:
            return jsonify({
                "message": "Job updated successfully in both collections",
                "updated_fields": {
                    "detailed_collection": detailed_update_fields,
                    "important_collection": important_update_fields
                }
            }), 200
        else:
            return jsonify({"message": "No changes were made"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500




# http://localhost:5000/delete_by_job_title
@app.route("/delete_by_job_title", methods=['DELETE'])
def delete_by_job_title_and_id():
    '''
    Delete a job listing by job title and custom id.
    '''
    try:
        # Get the job title and custom id from the request body
        data = request.get_json()

        if not data or 'title' not in data or 'id' not in data:
            return jsonify({"error": "Both job title and id are required"}), 400

        job_title = data.get("title")
        job_id = data.get("id")  # This is the custom id field, not ObjectId

        # Search for the job in both collections by title and custom id
        detailed_job = detailed_collection.find_one({"title": job_title, "id": job_id})
        important_job = important_collection.find_one({"title": job_title, "id": job_id})

        if not detailed_job or not important_job:
            return jsonify({"error": "Job not found in one or both collections"}), 404

        # Proceed to delete from both collections
        detailed_result = detailed_collection.delete_one({"title": job_title, "id": job_id})
        important_result = important_collection.delete_one({"title": job_title, "id": job_id})

        # Check if the deletion was successful in both collections
        if detailed_result.deleted_count > 0 and important_result.deleted_count > 0:
            return jsonify({
                "message": "Job deleted successfully from both collections",
                "deleted_job_title": job_title,
                "deleted_job_id": job_id
            }), 200
        else:
            return jsonify({"error": "Failed to delete the job"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500



# http://localhost:5000/query_salary_range
@app.route("/query_salary_range", methods=['GET'])
def query_salary_range():
    '''
    Query jobs based on a salary range (min_salary and max_salary).
    Returns the full job document for each job in the salary range.
    '''
    try:
        # Get the min_salary and max_salary from query parameters
        min_salary = request.args.get('min_salary')
        max_salary = request.args.get('max_salary')

        # Validate that both min_salary and max_salary are provided and are numbers
        if min_salary is None or max_salary is None:
            return jsonify({"error": "Both min_salary and max_salary are required"}), 400
        
        try:
            min_salary = float(min_salary)
            max_salary = float(max_salary)
        except ValueError:
            return jsonify({"error": "min_salary and max_salary must be valid numbers"}), 400

        # Query MongoDB for jobs where average_salary falls within the given range
        jobs = important_collection.find({
            "average_salary": {
                "$gte": min_salary,
                "$lte": max_salary
            }
        })

        # Format the result
        job_list = []
        for job in jobs:
            job["_id"] = str(job["_id"])  # Convert ObjectId to string for JSON serialization
            job_list.append(job)

        if not job_list:
            return jsonify({"message": "No jobs found within the given salary range"}), 404

        # Return the list of full job documents
        return jsonify(job_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500





# http://localhost:5000/query_experience_level
@app.route("/query_experience_level", methods=['GET'])
def query_experience_level():
    '''
    Query jobs based on experience level (e.g., 'Entry Level', 'Mid Level', 'Senior Level').
    '''
    try:
        # Get the experience_level from query parameters
        experience_level = request.args.get('experience_level')

        # Validate that experience_level is provided
        if not experience_level:
            return jsonify({"error": "experience_level parameter is required"}), 400

        # Query MongoDB for jobs where experience_level matches the query parameter, 
        # the regular expression makes it case insensetive
        # 
        jobs = detailed_collection.find({
            "experience_level": re.compile(f"^{experience_level}$", re.IGNORECASE)
        })

        # Format the result
        job_list = []
        for job in jobs:
            job["_id"] = str(job["_id"])  # Convert ObjectId to string for JSON serialization
            job_list.append(job)

        if not job_list:
            return jsonify({"message": f"No jobs found for experience level: {experience_level}"}), 404

        # Return the list of jobs
        return jsonify(job_list), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# http://localhost:5000/top_companies_in_industry
@app.route("/top_companies_in_industry", methods=['GET'])
def top_companies_in_industry():
    '''
    Fetch top companies in a given industry based on the number of job listings.
    '''
    try:
        # Get the industry from query parameters
        industry = request.args.get('industry')

        # Validate that the industry parameter is provided
        if not industry:
            return jsonify({"error": "industry query parameter is required"}), 400

        # Query MongoDB for jobs in the given industry and group them by company
        pipeline = [
            {"$match": {"industry_info.industry_name": industry}},
            {"$group": {"_id": "$company_info.name", "job_count": {"$sum": 1}}},
            {"$sort": {"job_count": -1}}  # Sort by the number of job listings in descending order
        ]

        top_companies = list(detailed_collection.aggregate(pipeline))

        # If no companies are found, return a 404
        if not top_companies:
            return jsonify({"message": f"No companies found in industry: {industry}"}), 404

        # Format the response
        response = [{"company": company["_id"], "job_count": company["job_count"]} for company in top_companies]

        # Return the list of top companies
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.errorhandler(404)
def page_not_found(e):
    '''Send message to the user if route is not defined.'''

    message = {
        "err":
            {
                "msg": "This route is currently not supported."
            }
    }

    resp = jsonify(message)
    # Sending 404 (not found) response
    resp.status_code = 404
    # Returning the object
    return resp