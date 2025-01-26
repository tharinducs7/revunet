import requests
import json

def post_to_rapidapi(reviews):
    url = "https://chatgpt-42.p.rapidapi.com/gpt4"
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
        "    },\n"
        "    ...\n"
        "  ],\n"
        "  \"for_customers\": [\n"
        "    {\n"
        "      \"title\": \"Title of the insight for customers\",\n"
        "      \"insights\": \"The specific insight for customers\"\n"
        "    },\n"
        "    ...\n"
        "  ]\n"
        "}\n\n"
        "Make sure the response strictly follows this JSON structure."
    )
    payload = {
        "messages": [{"role": "user", "content": content}],
        "web_access": False
    }
    headers = {
        "x-rapidapi-key": "YOUR_RAPIDAPI_KEY",
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if response_data.get("status") and "result" in response_data:
            raw_result = response_data["result"]
            if isinstance(raw_result, str):
                try:
                    # Remove backticks and "json" tag if present
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
                        "title": "Invalid JSON response",
                        "overall_aspect": "N/A",
                        "for_owners": [],
                        "for_customers": []
                    }
            else:
                return raw_result  # Already parsed
        else:
            print("API responded but status is False or 'result' key is missing.")
            return {
                "title": "Failed to fetch recommendations",
                "overall_aspect": "N/A",
                "for_owners": [],
                "for_customers": []
            }
            
    except Exception as e:
        print(f"Error posting to RapidAPI: {e}")
    return {
        "title": "Failed to fetch recommendations",
        "overall_aspect": "N/A",
        "for_owners": [],
        "for_customers": []
    }

def post_comparison_to_rapidapi(reviews1, reviews2, location_name1, location_name2):
    url = "https://chatgpt-42.p.rapidapi.com/gpt4"
    content = (
        f"Compare the following reviews for two businesses:\n\n"
        f"Business 1: {location_name1}\n"
        f"Reviews:\n{reviews1}\n\n"
        f"Business 2: {location_name2}\n"
        f"Reviews:\n{reviews2}\n\n"
        "Provide a detailed comparison and actionable recommendations in JSON format. In the response, include the actual business names "
        "('Business 1' as the name of the first business and 'Business 2' as the name of the second business) "
        "instead of using generic terms like 'Business 1' and 'Business 2'. Format the response as follows:\n\n"
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
        "        \"business1_score\": \"Score for {location_name1}\",\n"
        "        \"business2_score\": \"Score for {location_name2}\",\n"
        "        \"better_business\": \"Better Business Name (e.g., {location_name2})\"\n"
        "      },\n"
        "      ...\n"
        "    ]\n"
        "  },\n"
        "  \"recommendations\": {\n"
        "    \"for_business1\": [\n"
        "      {\n"
        "        \"title\": \"Recommendation Title\",\n"
        "        \"recommendation\": \"Specific recommendation for Business 1\",\n"
        "        \"priority\": \"High/Medium/Low\"\n"
        "      },\n"
        "      ...\n"
        "    ],\n"
        "    \"for_business2\": [\n"
        "      {\n"
        "        \"title\": \"Recommendation Title\",\n"
        "        \"recommendation\": \"Specific recommendation for Business 2\",\n"
        "        \"priority\": \"High/Medium/Low\"\n"
        "      },\n"
        "      ...\n"
        "    ]\n"
        "  }\n"
        "}\n\n"
        "Ensure that the response strictly follows the provided JSON structure and uses the actual business names wherever possible."
    )

    payload = {
        "messages": [{"role": "user", "content": content}],
        "web_access": False
    }
    headers = {
        "x-rapidapi-key": "b36b632ea3mshfba10ef37270d8fp1afd04jsn9e5f5e25573e",
        "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
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