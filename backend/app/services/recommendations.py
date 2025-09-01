import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get values from environment
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")
RAPIDAPI_URL = os.getenv("RAPIDAPI_URL")

HEADERS = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
    "Content-Type": "application/json"
}

def post_to_rapidapi(reviews):
    # url = "https://open-ai21.p.rapidapi.com/conversationllama"
    content = (
        f"Based on the following reviews:\n\n{reviews}\n\n"
        "Provide actionable recommendations in JSON format as follows:\n\n"
        "{\n"
        "  \"title\": \"A summary title\",\n"
        "  \"overall_aspect\": \"A summary of overall insights and improvements\",\n"
        "  \"for_owners\": [\n"
        "    {\n"
        "      \"title\": \"Title of the recommendation for owners\",\n"
        "      \"recommendation\": \"The specific recommendation for improvement\",\n"
        "      \"priority\": \"High/Medium/Low\"\n"
        "    }\n"
        "  ],\n"
        "  \"for_customers\": [\n"
        "    {\n"
        "      \"title\": \"Title of the insight for customers\",\n"
        "      \"insights\": \"The specific insight for customers\"\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "Ensure the response strictly follows this JSON structure."
    )
    payload = {
        "messages": [{"role": "user", "content": content}],
        "web_access": False
    }
 
    print("content:", content)

    try:
        response = requests.post(RAPIDAPI_URL, json=payload, headers=HEADERS)
        print("Status Code:", response.status_code)
        print("Response Headers:", response.headers)
        print("Raw Text Response:", response.text)

        try:
            response_data = response.json()
        except json.JSONDecodeError as e:
            print(f"JSON decoding error: {e}")
            return {
                "title": "Invalid JSON response",
                "overall_aspect": "N/A",
                "for_owners": [],
                "for_customers": []
            }

        if response_data.get("status") and "result" in response_data:
            raw_result = response_data["result"]
            if isinstance(raw_result, str):
                try:
                    raw_result_cleaned = raw_result.strip("`").strip()
                    if raw_result_cleaned.startswith("json\n"):
                        raw_result_cleaned = raw_result_cleaned[5:].strip()
                    parsed_result = json.loads(raw_result_cleaned)
                    return parsed_result
                except json.JSONDecodeError as e:
                    print(f"JSON decoding error: {e}")
                    print("Raw result for debugging:", raw_result)
                    return {
                        "title": "Invalid JSON response",
                        "overall_aspect": "N/A",
                        "for_owners": [],
                        "for_customers": []
                    }
            else:
                return raw_result
        else:
            print("API responded but 'status' is False or 'result' key is missing.")
            return {
                "title": "Failed to fetch recommendations",
                "overall_aspect": "N/A",
                "for_owners": [],
                "for_customers": []
            }

    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        return {
            "title": "Request failed",
            "overall_aspect": "N/A",
            "for_owners": [],
            "for_customers": []
        }


def post_comparison_to_rapidapi(reviews1, reviews2, location_name1, location_name2):
    # url = "https://open-ai21.p.rapidapi.com/conversationllama"
    content = (
        f"Compare the following reviews for two businesses:\n\n"
        f"Business 1: {location_name1}\n"
        f"Reviews:\n{reviews1}\n\n"
        f"Business 2: {location_name2}\n"
        f"Reviews:\n{reviews2}\n\n"
        "Provide a detailed comparison and actionable recommendations in JSON format. "
        "Use the actual business names ('Business 1' as the name of the first business and 'Business 2' as the name of the second business) "
        "in the summaries and comparisons, but in the recommendations section, use the keys 'for_business1' and 'for_business2' only — "
        "**do NOT use business names as keys inside the 'recommendations' object**.\n\n"
        "Format the response as follows:\n\n"
        "{\n"
        "  \"comparison\": {\n"
        "    \"overall_sentiment\": {\n"
        "      \"business1\": \"Summary of overall sentiment for Business 1\",\n"
        "      \"business2\": \"Summary of overall sentiment for Business 2\",\n"
        "      \"better_business\": \"Better Business Name (e.g., Business 1 - {location_name1})\"\n"
        "    },\n"
        "    \"aspect_comparison\": [\n"
        "      {\n"
        "        \"aspect\": \"Aspect name (e.g., Service, Cleanliness, Pricing, etc.)\",\n"
        f"        \"business1_score\": \"Score for {location_name1}\",\n"
        f"        \"business2_score\": \"Score for {location_name2}\",\n"
        "        \"better_business\": \"Better Business Name (e.g., {location_name2})\"\n"
        "      },\n"
        "      ...\n"
        "    ]\n"
        "  },\n"
        "  \"recommendations\": {\n"
        "    \"for_business1\": [\n"
        "      {\n"
        "        \"title\": \"Recommendation Title\",\n"
        "        \"recommendation\": \"Specific recommendation for the first business\",\n"
        "        \"priority\": \"High/Medium/Low\"\n"
        "      },\n"
        "      ...\n"
        "    ],\n"
        "    \"for_business2\": [\n"
        "      {\n"
        "        \"title\": \"Recommendation Title\",\n"
        "        \"recommendation\": \"Specific recommendation for the second business\",\n"
        "        \"priority\": \"High/Medium/Low\"\n"
        "      },\n"
        "      ...\n"
        "    ]\n"
        "  }\n"
        "}\n\n"
        "Ensure that the response strictly follows the provided JSON structure and uses the actual business names in the summaries and comparisons, "
        "but keeps only the 'for_business1' and 'for_business2' keys in the recommendations section."
    )

    payload = {
        "messages": [{"role": "user", "content": content}],
        "web_access": False
    }
    # headers = {
    #     "x-rapidapi-key": "82892ec185msh9a4a5f132dfc5bdp1605abjsn56ac682951c6",
    #     "x-rapidapi-host": "open-ai21.p.rapidapi.com",
    #     "Content-Type": "application/json"
    # }

    try:
        response = requests.post(RAPIDAPI_URL, json=payload, headers=HEADERS)
        response_data = response.json()

        if response_data.get("status") and "result" in response_data:
            raw_result = response_data["result"]
            if isinstance(raw_result, str):
                try:
                    # Clean up the raw result
                    raw_result_cleaned = raw_result.strip("`").strip()
                    if raw_result_cleaned.startswith("json\n"):
                        raw_result_cleaned = raw_result_cleaned[5:].strip()

                    # Parse the cleaned JSON string
                    parsed_result = json.loads(raw_result_cleaned)
                    return parsed_result
                except json.JSONDecodeError as e:
                    print(f"JSON decoding error: {e}")
                    print("Raw result for debugging:", raw_result)
                    return {
                        "comparison": {
                            "overall_sentiment": {
                                "business1": "N/A",
                                "business2": "N/A",
                                "better_business": "N/A"
                            },
                            "aspect_comparison": []
                        },
                        "recommendations": {
                            "for_business1": [],
                            "for_business2": []
                        }
                    }
            else:
                # If raw_result is already a parsed object
                return raw_result
        else:
            print("API responded but status is False or 'result' key is missing.")
            return {
                "comparison": {
                    "overall_sentiment": {
                        "business1": "N/A",
                        "business2": "N/A",
                        "better_business": "N/A"
                    },
                    "aspect_comparison": []
                },
                "recommendations": {
                    "for_business1": [],
                    "for_business2": []
                }
            }

    except Exception as e:
        print(f"Error posting to RapidAPI: {e}")
        return {
            "comparison": {
                "overall_sentiment": {
                    "business1": "N/A",
                    "business2": "N/A",
                    "better_business": "N/A"
                },
                "aspect_comparison": []
            },
            "recommendations": {
                "for_business1": [],
                "for_business2": []
            }
        }