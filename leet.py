import random
import asyncio
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

LEETCODE_GRAPHQL_URL = "https://leetcode.com/graphql"
PROBLEM_URL = "https://leetcode.com/problems/"

# Set your random seed here for reproducibility
RANDOM_SEED = 42

# Number of problems to fetch
NUM_GENERAL = 25
NUM_SQL = 10
NUM_SYSTEM_DESIGN = 5
SKIP = 0

# GraphQL query to fetch problems
PROBLEM_QUERY = gql("""
query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
  problemsetQuestionList: questionList(
    categorySlug: $categorySlug
    limit: $limit
    skip: $skip
    filters: $filters
  ) {
    total: totalNum
    questions: data {
      acRate
      difficulty
      freqBar
      frontendQuestionId: questionFrontendId
      isFavor
      paidOnly: isPaidOnly
      status
      title
      titleSlug
      topicTags {
        name
        id
        slug
      }
      hasSolution
      hasVideoSolution
    }
  }
}
""")

async def fetch_problems(client, filters, limit=1000):
    # LeetCode returns max 1000 at a time
    params = {
        "categorySlug": "",
        "limit": limit,
        "skip": SKIP,
        "filters": filters
    }
    result = await client.execute(PROBLEM_QUERY, variable_values=params)
    return result["problemsetQuestionList"]["questions"]

def filter_and_sample(problems, n, seed):
    random.Random(seed).shuffle(problems)
    return problems[:n]

def format_problem(problem):
    tags = [tag['name'] for tag in problem['topicTags']]
    return f"{problem['title']} | Tags: {', '.join(tags)} | {PROBLEM_URL}{problem['titleSlug']}"

async def main():
    random.seed(RANDOM_SEED)
    transport = AIOHTTPTransport(url=LEETCODE_GRAPHQL_URL, ssl=False)
    async with Client(transport=transport, fetch_schema_from_transport=False) as client:
        # Fetch all problems
        all_problems = await fetch_problems(client, filters={})
        # General problems (any difficulty)
        general_sample = filter_and_sample(all_problems, NUM_GENERAL, RANDOM_SEED)
        # SQL problems (medium/hard, with 'database' or 'sql' tags, and not 'Easy')
        sql_tag_slugs = {'sql', 'database', 'relational-database'}
        sql_problems = [
            p for p in all_problems
            if any(tag['slug'] in sql_tag_slugs for tag in p['topicTags'])
            and p['difficulty'] in ('Medium', 'Hard')
        ]
        sql_sample = filter_and_sample(sql_problems, NUM_SQL, RANDOM_SEED + 1)
        # System Design problems (medium/hard)
        sys_design_problems = [p for p in all_problems if any('system-design' in tag['slug'] or 'design' in tag['slug'] for tag in p['topicTags']) and p['difficulty'] in ('Medium', 'Hard')]
        sys_design_sample = filter_and_sample(sys_design_problems, NUM_SYSTEM_DESIGN, RANDOM_SEED + 2)

        output_lines = []
        output_lines.append("=== 25 Random LeetCode Problems ===")
        for p in general_sample:
            output_lines.append(format_problem(p))
        output_lines.append("\n=== 5-7 SQL (Medium/Hard) Problems ===")
        for p in sql_sample:
            output_lines.append(format_problem(p))
        output_lines.append("\n=== 5 System Design (Medium/Hard) Problems ===")
        for p in sys_design_sample:
            output_lines.append(format_problem(p))

        # Write to questions.txt
        with open("questions.txt", "w", encoding="utf-8") as f:
            for line in output_lines:
                f.write(line + "\n")

        # Also print to stdout as before
        for line in output_lines:
            print(line)

if __name__ == "__main__":
    asyncio.run(main())
