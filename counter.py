from pymongo import MongoClient
from datetime import datetime
import streamlit as st


def get_database():
    """
    Connect to MongoDB and return the database object.
    Uses environment variable MONGODB_URI if available, otherwise uses a default local connection.
    """
    # Get MongoDB URI from environment variable or use default
    mongodb_uri = st.secrets["MONGODB_URI"]

    # Connect to MongoDB
    client = MongoClient(mongodb_uri)

    # Return database (create if it doesn't exist)
    return client["usage_tracker"]


def read_counter(counter_id="gemini_api"):
    """
    Read the current counter value from MongoDB.

    Args:
        counter_id (str): Identifier for the counter to read (default: "gemini_api")

    Returns:
        dict: Counter data including:
            - daily_count: Count for current day
            - monthly_count: Count for current month
            - daily_limit: Maximum daily count
            - monthly_limit: Maximum monthly count
            - daily_remaining: Remaining count for today
            - monthly_remaining: Remaining count for current month
    """
    db = get_database()
    counters = db["counters"]

    # Get current date information
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    current_month = now.strftime("%Y-%m")

    # Try to find the counter document
    counter_doc = counters.find_one({"_id": counter_id})

    # If counter doesn't exist or is for a different day/month, create/update it
    if counter_doc is None:
        # Initialize a new counter
        counter_doc = {
            "_id": counter_id,
            "daily": {"date": current_date, "count": 0},
            "monthly": {"month": current_month, "count": 0},
            "limits": {
                "daily": 10,  # Default daily limit
                "monthly": 300,  # Default monthly limit
            },
        }
        counters.insert_one(counter_doc)
    else:
        # Check if we need to reset daily counter (new day)
        if counter_doc["daily"]["date"] != current_date:
            counters.update_one(
                {"_id": counter_id},
                {"$set": {"daily.date": current_date, "daily.count": 0}},
            )
            counter_doc["daily"]["date"] = current_date
            counter_doc["daily"]["count"] = 0

        # Check if we need to reset monthly counter (new month)
        if counter_doc["monthly"]["month"] != current_month:
            counters.update_one(
                {"_id": counter_id},
                {"$set": {"monthly.month": current_month, "monthly.count": 0}},
            )
            counter_doc["monthly"]["month"] = current_month
            counter_doc["monthly"]["count"] = 0

    # Calculate remaining counts
    daily_limit = counter_doc["limits"]["daily"]
    monthly_limit = counter_doc["limits"]["monthly"]
    daily_count = counter_doc["daily"]["count"]
    monthly_count = counter_doc["monthly"]["count"]

    # Prepare response
    response = {
        "daily_count": daily_count,
        "monthly_count": monthly_count,
        "daily_limit": daily_limit,
        "monthly_limit": monthly_limit,
        "daily_remaining": max(0, daily_limit - daily_count),
        "monthly_remaining": max(0, monthly_limit - monthly_count),
        "can_make_request": (daily_count < daily_limit)
        and (monthly_count < monthly_limit),
    }

    return response


def update_counter(counter_id="gemini_api"):

    # First check current counter values
    current = read_counter(counter_id)

    # Check if we've reached limits
    if not current["can_make_request"]:
        return None

    # Get database references
    db = get_database()
    counters = db["counters"]

    # Update both daily and monthly counters
    counters.update_one(
        {"_id": counter_id}, {"$inc": {"daily.count": 1, "monthly.count": 1}}
    )

    # Record usage timestamp
    db["usage_log"].insert_one(
        {"counter_id": counter_id, "timestamp": datetime.now(), "type": "api_call"}
    )

    return
