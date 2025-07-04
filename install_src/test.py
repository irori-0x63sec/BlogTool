import requests

token = "20f57019-7a8d-4b0c-9bd9-37a0f13eb3e1"

query = """
query {
  me {
    publications(first: 1) {
      edges {
        node {
          id
          title
        }
      }
    }
  }
}
"""

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

res = requests.post(
    "https://gql.hashnode.com/",
    json={"query": query},
    headers=headers
)

print(res.status_code)
print(res.json())
