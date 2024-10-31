# README - Flask APP

## Starting the Docker Container

To start the application using Docker, follow these steps:

### 1. Bring up the Docker container:
First, run the following command to start the container using Docker Compose and then run the following commands:
```bash
docker-compose up

# from different cli
docker exec -it slim-python bash

pip install -r requirements.txt

python data_transformation.py

```

Running data_transformation.py creates json objects from csv files, and then saves both of the 
json objects, and finally, it creates a careerhub db. Then imports 2 jsons into respective collections,
jobs_detailed and jobs_important. 

Then, run `python run-app-docker.py`. 

This will launch the flask app:

Following routes are supported:


## Route: `/` (Home)

**Description**:  
This route is the default route that handles all incoming traffic directed to the root of the website. It returns a welcome message.

**Method**:  
`GET`

**Response**:  
Returns a JSON object with a welcome message.


**Summary**:  
- This route requires no parameters and is used to display a default message to the user visiting the website.




## Route: `/create/jobPost` (Create Job Post)

**Description**:  
This endpoint allows users to create a new job post, which is inserted into two collections: `detailed_collection` and `important_collection`. It accepts job details in JSON format, validates the required fields, and stores the provided data.

**Method**:  
`POST`

**Response**:  
Returns a JSON object with a success message, along with the inserted document IDs from both collections (`detailed_collection` and `important_collection`).

**Parameters**:  
- **Mandatory**:
  - `id`: Custom job ID (string or int)
  - `title`: Title of the job (string)
  - `description`: Description of the job (string)
  - `years_of_experience`: Number of years of experience required for the job (int)
  - `name`: Name of the company (string)
  - `industry_name`: Name of the industry (string)
  - `average_salary`: Average salary for the job (float)
  - `location`: Job location (string)

- **Optional**:
  - `detailed_description`: A more detailed description of the job (string)
  - `responsibilities`: List of job responsibilities (string)
  - `requirements`: Job requirements (string)
  - `experience_level`: Level of experience required (e.g., "Entry Level", "Mid Level", "Senior Level") (string)
  - `size`: Size of the company (string)
  - `type`: Type of the company (string)
  - `website`: Company website (string)
  - `company_description`: Company description (string)
  - `hr_contact`: HR contact information (string)
  - `growth_rate`: Industry growth rate (float)
  - `industry_skills`: Key skills required in the industry (string)
  - `top_companies`: Top companies in the industry (string)
  - `trends`: Industry trends (string)
  - `required_education`: Minimum required education level (string)
  - `preferred_skills`: Preferred skills for the job (string)
  - `employment_type`: Type of employment (e.g., Full-time, Part-time) (string)
  - `benefits`: Job benefits (string)
  - `remote`: Whether the job is remote or not (boolean)
  - `job_posting_url`: URL of the job posting (string)
  - `posting_date`: Date when the job was posted (string)
  - `closing_date`: Date when the job posting closes (string)  **(flat field, not inside `employment_details`)**

**Summary**:  
- This route creates a new job post with the provided details. The data is inserted into two collections: `detailed_collection` and `important_collection`. Both collections require the `id`, `title`, `description`, `years_of_experience`, `name`, `industry_name`, `average_salary`, and `location` fields as mandatory.


## Route: `/search_by_job_id/<int:job_id>` (Search Job by ID)

**Description**:  
This endpoint allows users to search for and display job details by providing the `job_id`. It retrieves the job from the `detailed_collection` based on the `id` field (which is an integer).

**Method**:  
`GET`

**Path Parameter**:  
- **job_id**: The custom job ID (integer) that identifies the job in the `detailed_collection`.

**Response**:  
- If the job is found, it returns the full job document as a JSON object.
- If the job is not found, it returns a `404 Not Found` error with a message.

**Error Handling**:  
- If the job with the provided `job_id` does not exist, a `404` error is returned with the message `"Job not found"`.
- If an internal error occurs during the request, a `500` status is returned with the error message.

**Parameters**:  
- **Mandatory**:
  - `job_id` (integer): This is a path parameter and must be provided in the URL to identify the specific job in the collection.

**Summary**:  
- This route retrieves the job document based on the provided `job_id` from the `detailed_collection`. It returns the full job document as a JSON object.
- If the job is not found, a `404` error is returned. If there’s any other error, it returns a `500` error with a message.



## Route: `/update_by_job_title` (Update Job by Title and ID)

**Description**:  
This endpoint allows users to update the details of a job in both `detailed_collection` and `important_collection` using the `job_id` and `title` fields. It supports updates to the `description`, `average_salary`, and `location` fields.

**Method**:  
`POST`

**Request Body Parameters**:  
- **Mandatory**:
  - `id`: The custom job ID (string or int) used to uniquely identify the job.
  - `title`: The title of the job (string) used in conjunction with `id` to identify the job.

- **Optional** (can be included in the request to update the job):
  - `description`: New job description (string).
  - `average_salary`: Updated average salary for the job (int or float).
  - `location`: Updated job location (string).

**Response**:  
- If the update is successful, a JSON object is returned showing the updated fields in both `detailed_collection` and `important_collection`.
- If no changes were made (i.e., the provided values are the same as the current values), a `200 OK` response is returned with the message `"No changes were made"`.
- If the job is not found in either collection, a `404 Not Found` error is returned.

**Error Handling**:  
- If there is a type mismatch in the `average_salary` field (i.e., it is not a number), a `400` error is returned.
- If an internal error occurs during the update process, a `500` error is returned.

**Parameters**:  
- **Mandatory**:
  - `id`: The custom job ID (int or string).
  - `title`: The job title (string).

- **Optional**:
  - `description`: The updated job description (string).
  - `average_salary`: The updated average salary (float or int).
  - `location`: The updated job location (string).

**Summary**:  
- This route allows users to update the `description`, `average_salary`, and `location` fields of a job in both `detailed_collection` and `important_collection` using the `id` and `title` as identifiers.


## Route: `/delete_by_job_title` (Delete Job by Title and ID)

**Description**:  
This endpoint allows users to delete a job listing from both `detailed_collection` and `important_collection` by providing the `job_id` and `title`. It ensures that the job is deleted from both collections based on these two identifiers.

**Method**:  
`DELETE`

**Request Body Parameters**:  
- **Mandatory**:
  - `id`: The custom job ID (string or int) used to uniquely identify the job.
  - `title`: The title of the job (string) used in conjunction with `id` to identify the job.

**Response**:  
- If the deletion is successful, a JSON object is returned with a success message, including the deleted `title` and `id`.
- If the job is not found in either collection, a `404 Not Found` error is returned with a message.
- If the deletion fails, a `500 Internal Server Error` is returned with an error message.


**Parameters**:  
- **Mandatory**:
  - `id`: The custom job ID (int or string).
  - `title`: The job title (string).

**Summary**:  
- This route allows users to delete a job listing by providing both the `id` and `title`. The job is deleted from both `detailed_collection` and `important_collection` if found. If the job is not found in one or both collections, a `404 Not Found` response is returned. If the deletion fails for some reason, a `500 Internal Server Error` is returned.


## Route: `/query_salary_range` (Query Jobs by Salary Range)

**Description**:  
This endpoint allows users to query job listings based on a salary range by providing `min_salary` and `max_salary`. It searches the `important_collection` for jobs where the `average_salary` falls within the specified range and returns the full job document for each matching job.

**Method**:  
`GET`

**Query Parameters**:  
- **Mandatory**:
  - `min_salary`: The minimum salary value (float or int).
  - `max_salary`: The maximum salary value (float or int).

**Response**:  
- If jobs are found within the specified salary range, a JSON array of the full job documents is returned.
- If no jobs are found, a `404 Not Found` message is returned.
- If there is an error in the query (such as missing or invalid parameters), a `400 Bad Request` message is returned.
- If an internal error occurs, a `500 Internal Server Error` message is returned.

**Error Handling**:  
- If `min_salary` and `max_salary` are not provided, a `400 Bad Request` is returned.
- If `min_salary` and `max_salary` cannot be converted to valid numbers, a `400 Bad Request` is returned.
- If no jobs are found within the specified range, a `404 Not Found` message is returned.
- If an internal error occurs, a `500 Internal Server Error` is returned.

**Parameters**:  
- **Mandatory**:
  - `min_salary`: The minimum salary (float or int).
  - `max_salary`: The maximum salary (float or int).

**Summary**:  
- This route allows users to query job listings based on a salary range using the `min_salary` and `max_salary` query parameters. It returns all job documents where the `average_salary` falls within the specified range.
- If the query fails due to missing parameters or invalid data, appropriate error messages are returned.



## Route: `/query_experience_level` (Query Jobs by Experience Level)

**Description**:  
This endpoint allows users to query job listings based on experience level by providing the `experience_level` query parameter (e.g., 'Entry Level', 'Mid Level', 'Senior Level'). It performs a case-insensitive search in the `detailed_collection` and returns all matching jobs.

**Method**:  
`GET`

**Query Parameters**:  
- **Mandatory**:
  - `experience_level`: The experience level to filter jobs (string). Accepted values include levels like 'Entry Level', 'Mid Level', 'Senior Level', etc.

**Response**:  
- If jobs matching the provided experience level are found, a JSON array of the full job documents is returned.
- If no jobs are found matching the experience level, a `404 Not Found` message is returned.
- If there is an error in the query (such as a missing parameter), a `400 Bad Request` message is returned.
- If an internal error occurs, a `500 Internal Server Error` message is returned.

**Error Handling**:  
- If the `experience_level` query parameter is not provided, a `400 Bad Request` is returned.
- If no jobs are found matching the given experience level, a `404 Not Found` message is returned.
- If an internal error occurs, a `500 Internal Server Error` is returned.

**Parameters**:  
- **Mandatory**:
  - `experience_level`: The experience level of the job (string).

**Summary**:  
- This route allows users to query job listings by experience level. It performs a case-insensitive search and returns all jobs with a matching `experience_level` from the `detailed_collection`.
- If no jobs are found or the query fails due to missing parameters, appropriate error messages are returned.


## Route: `/top_companies_in_industry` (Top Companies in Industry by Job Listings)

**Description**:  
This endpoint allows users to fetch the top companies in a given industry based on the number of job listings. The user provides the `industry` query parameter, and the API returns a list of companies ranked by the number of job listings they have.

**Method**:  
`GET`

**Query Parameters**:  
- **Mandatory**:
  - `industry`: The industry name to filter companies (string).

**Response**:  
- If companies with job listings in the specified industry are found, a JSON array of companies ranked by the number of job listings is returned.
  - Each item in the array contains the `company` name and `job_count`.
- If no companies are found for the specified industry, a `404 Not Found` message is returned.
- If there is an error in the query (such as a missing parameter), a `400 Bad Request` message is returned.
- If an internal error occurs, a `500 Internal Server Error` message is returned.

**Error Handling**:  
- If the `industry` query parameter is not provided, a `400 Bad Request` is returned.
- If no companies are found in the specified industry, a `404 Not Found` message is returned.
- If an internal error occurs, a `500 Internal Server Error` is returned.

**Parameters**:  
- **Mandatory**:
  - `industry`: The industry name (string) to fetch top companies.

**Summary**:  
- This route returns the top companies in a specified industry based on the number of job listings they have. It aggregates job listings from the `detailed_collection` and returns the companies ranked in descending order of the number of listings.



## Error Handling: `404 Not Found` (Unsupported Route)

**Description**:  
This error handler sends a custom response when the user attempts to access a route that is not defined or supported by the API.

**Method**:  
Automatic for any undefined routes (`GET`, `POST`, `DELETE`, etc.).

**Response**:  
- A `404 Not Found` error is returned with a message indicating that the route is not supported.

**Error Message**:  
The response is returned as a JSON object:
```json
{
    "err": {
        "msg": "This route is currently not supported."
    }
}

```
