def validate_sql_query(query):

    """
    Validate generated SQL query
    for security and safety
    """

    query_upper = query.upper()

    # Dangerous SQL keywords
    blocked_keywords = [
        "DROP",
        "DELETE",
        "UPDATE",
        "INSERT",
        "ALTER",
        "TRUNCATE",
        "CREATE",
        "REPLACE"
    ]

    # Check blocked operations
    for keyword in blocked_keywords:

        if keyword in query_upper:

            return False, (
                f"Blocked dangerous SQL keyword: {keyword}"
            )

    # Allow only SELECT queries
    if not query_upper.strip().startswith("SELECT"):

        return False, (
            "Only SELECT queries are allowed."
        )

    return True, "Query is safe."