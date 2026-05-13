from openai import OpenAI


def generate_sql(user_question, api_key):

    """
    Convert natural language question into SQL query
    """

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    schema = """

    You are an expert SQL generator.

    Database name: business_sales.db

    Table name: sales

    Columns:
    - order_id
    - order_date
    - region
    - product
    - category
    - sales
    - profit
    - quantity

    Rules:
    - Generate only SQLite-compatible SQL queries
    - SQLite does NOT support EXTRACT()
    - Use strftime() for date operations
    - Return only SQL query
    - Do not explain anything
    - Use table name: sales
    - Use LIMIT when appropriate

    Examples:

    Monthly sales trend:
    SELECT
        strftime('%Y-%m', order_date) AS month,
        SUM(sales) AS total_sales
    FROM sales
    GROUP BY month
    ORDER BY month;

    Top products by profit:
    SELECT
        product,
        SUM(profit) AS total_profit
    FROM sales
    GROUP BY product
    ORDER BY total_profit DESC
    LIMIT 5;
        """

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "system",
                "content": schema
            },
            {
                "role": "user",
                "content": user_question
            }
        ],

        temperature=0
    )

    return response.choices[0].message.content

def clean_sql_query(query):

    """
    Clean markdown formatting
    from generated SQL
    """

    query = query.replace("```sql", "")

    query = query.replace("```", "")

    return query.strip()


def generate_business_insight(
    user_question,
    query_result,
    api_key
):

    """
    Generate business insights
    from SQL query results
    """

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    # Convert dataframe to text
    result_text = query_result.to_string(index=False)

    prompt = f"""

    You are a senior business analyst.

    A user asked:
    "{user_question}"

    SQL query result:

    {result_text}

    Generate:
    - concise business insights
    - important trends
    - business interpretation

    Keep response professional and simple.

    """

    response = client.chat.completions.create(

        model="llama-3.1-8b-instant",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.3
    )

    return response.choices[0].message.content