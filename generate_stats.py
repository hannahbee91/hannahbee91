import os
import requests
import json
from pathlib import Path
from datetime import datetime

USERNAME = "hannahbee91"
TOKEN = os.getenv("GITHUB_TOKEN")

# Lavender and Honey Theme
BG_COLOR = "#1e1e2e"          # Dark base
TEXT_COLOR = "#E6E6FA"        # Lavender
ACCENT_COLOR = "#FFC300"      # Honey/Gold
BORDER_COLOR = "#E6E6FA"      # Lavender

def get_stats():
    """Fetch GitHub stats using GraphQL API, fallback to mock data if no token."""
    if not TOKEN:
        print("No GITHUB_TOKEN found, using mock data for generation.")
        return {
            "stars": 128,
            "commits": 1452,
            "contributions": 842,
            "popular_repo": "awesome-devops-tools",
            "languages": [
                {"name": "Python", "percent": 45.2, "color": "#3572A5"},
                {"name": "Terraform", "percent": 25.4, "color": "#7B42BC"},
                {"name": "Bash", "percent": 15.1, "color": "#89e051"},
                {"name": "Node.js", "percent": 14.3, "color": "#3178c6"}
            ]
        }

    headers = {"Authorization": f"Bearer {TOKEN}"}
    
    # We use a mix of GraphQL and REST. GraphQL is great for contributions.
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
          totalCommitContributions
        }
        repositories(first: 100, ownerAffiliations: OWNER, orderBy: {field: STARGAZERS, direction: DESC}) {
          nodes {
            name
            stargazerCount
            languages(first: 5, orderBy: {field: SIZE, direction: DESC}) {
              edges {
                size
                node {
                  name
                  color
                }
              }
            }
          }
        }
      }
    }
    """
    
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"login": USERNAME}},
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Error fetching data: {response.text}")
        # fallback to mock
        return get_stats_mock()
        
    data = response.json()
    if "errors" in data:
        print(f"GraphQL errors: {data['errors']}")
        return get_stats_mock()
        
    user_data = data["data"]["user"]
    
    # Calculate stats
    contributions = user_data["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    commits = user_data["contributionsCollection"]["totalCommitContributions"]
    
    repos = user_data["repositories"]["nodes"]
    
    total_stars = sum(repo["stargazerCount"] for repo in repos)
    popular_repo = repos[0]["name"] if repos else "None"
    
    # Calculate top languages
    lang_sizes = {}
    lang_colors = {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            lang_name = edge["node"]["name"]
            lang_size = edge["size"]
            lang_color = edge["node"]["color"] or "#cccccc"
            
            lang_sizes[lang_name] = lang_sizes.get(lang_name, 0) + lang_size
            lang_colors[lang_name] = lang_color
            
    total_size = sum(lang_sizes.values())
    
    # Sort and calculate percentages
    sorted_langs = sorted(lang_sizes.items(), key=lambda x: x[1], reverse=True)[:5]
    languages = []
    
    if total_size > 0:
        for name, size in sorted_langs:
            percent = (size / total_size) * 100
            languages.append({
                "name": name,
                "percent": round(percent, 1),
                "color": lang_colors[name]
            })
            
    return {
        "stars": total_stars,
        "commits": commits,
        "contributions": contributions,
        "popular_repo": popular_repo,
        "languages": languages
    }

def get_stats_mock():
    return {
        "stars": 128,
        "commits": 1452,
        "contributions": 842,
        "popular_repo": "awesome-devops-tools",
        "languages": [
            {"name": "Python", "percent": 45.2, "color": "#3572A5"},
            {"name": "Terraform", "percent": 25.4, "color": "#7B42BC"},
            {"name": "Bash", "percent": 15.1, "color": "#89e051"},
            {"name": "Node.js", "percent": 14.3, "color": "#3178c6"}
        ]
    }

def generate_svg(stats, output_path):
    # Base Layout
    svg_width = 480
    svg_height = 280
    
    # Generate Language Bar
    lang_bar = ""
    current_x = 0
    total_width = 400
    
    lang_legends = ""
    legend_x = 0
    legend_y = 0
    
    for i, lang in enumerate(stats["languages"]):
        width = (lang["percent"] / 100) * total_width
        lang_bar += f'<rect x="{current_x}" y="0" width="{width}" height="10" fill="{lang["color"]}" />\n'
        current_x += width
        
        # Legend row wrapping
        lx = (i % 2) * 180
        ly = (i // 2) * 25
        
        lang_legends += f'''
        <g transform="translate({lx}, {ly})">
            <circle cx="5" cy="5" r="5" fill="{lang["color"]}" />
            <text x="15" y="9" font-family="Arial" font-size="12" fill="{TEXT_COLOR}">{lang["name"]} {lang["percent"]}%</text>
        </g>
        '''
        
    svg_template = f'''<svg width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" fill="none" xmlns="http://www.w3.org/2000/svg">
    <style>
        .title {{ font: 600 18px 'Segoe UI', Ubuntu, Sans-Serif; fill: {ACCENT_COLOR}; }}
        .stat {{ font: 400 14px 'Segoe UI', Ubuntu, Sans-Serif; fill: {TEXT_COLOR}; }}
        .bold {{ font-weight: 700; }}
        .icon {{ fill: {ACCENT_COLOR}; }}
    </style>
    
    <rect width="{svg_width-2}" height="{svg_height-2}" x="1" y="1" rx="8" fill="{BG_COLOR}" stroke="{BORDER_COLOR}" stroke-width="1.5"/>
    
    <text x="25" y="35" class="title">✨ GitHub Stats for @{USERNAME}</text>
    
    <!-- Stats Column 1 -->
    <g transform="translate(25, 65)">
        <svg x="0" y="0" width="16" height="16" viewBox="0 0 16 16" class="icon"><path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.751.751 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"></path></svg>
        <text x="25" y="12" class="stat">Total Stars: <tspan class="bold">{stats["stars"]}</tspan></text>
    </g>
    
    <g transform="translate(25, 95)">
        <svg x="0" y="0" width="16" height="16" viewBox="0 0 16 16" class="icon"><path d="M10.5 7.75a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Zm1.43.75a4.002 4.002 0 0 1-7.86 0H.75a.75.75 0 1 1 0-1.5h3.32a4.001 4.001 0 0 1 7.86 0h3.32a.75.75 0 1 1 0 1.5h-3.32Z"></path></svg>
        <text x="25" y="12" class="stat">Total Commits: <tspan class="bold">{stats["commits"]}</tspan></text>
    </g>
    
    <!-- Stats Column 2 -->
    <g transform="translate(225, 65)">
        <svg x="0" y="0" width="16" height="16" viewBox="0 0 16 16" class="icon"><path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1v7.5h-8a2.5 2.5 0 0 1-2.5-2.5V2.5a1 1 0 0 1 1-1h8.5Zm-5 6a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Z"></path></svg>
        <text x="25" y="12" class="stat">Popular Repo: <tspan class="bold">{stats["popular_repo"]}</tspan></text>
    </g>
    
    <g transform="translate(225, 95)">
        <svg x="0" y="0" width="16" height="16" viewBox="0 0 16 16" class="icon"><path d="M8 1a7 7 0 1 1 0 14A7 7 0 0 1 8 1Zm0 1.5a5.5 5.5 0 1 0 0 11 5.5 5.5 0 0 0 0-11ZM8 4a.75.75 0 0 1 .75.75v3.5l2.25 1.25a.75.75 0 1 1-.75 1.3l-2.5-1.39A.75.75 0 0 1 7.25 8V4.75A.75.75 0 0 1 8 4Z"></path></svg>
        <text x="25" y="12" class="stat">Contributions: <tspan class="bold">{stats["contributions"]}</tspan></text>
    </g>

    <!-- Divider -->
    <line x1="25" y1="130" x2="455" y2="130" stroke="{BORDER_COLOR}" stroke-width="0.5" stroke-opacity="0.5"/>
    
    <!-- Languages -->
    <text x="25" y="155" class="stat bold">Top Languages</text>
    
    <g transform="translate(25, 170)">
        <mask id="bar-mask">
            <rect x="0" y="0" width="{total_width}" height="10" rx="5" fill="white" />
        </mask>
        <g mask="url(#bar-mask)">
            {lang_bar}
        </g>
    </g>
    
    <g transform="translate(25, 195)">
        {lang_legends}
    </g>
</svg>'''
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(svg_template)
    print(f"Generated SVG at {output_path}")

if __name__ == "__main__":
    stats = get_stats()
    generate_svg(stats, "assets/github-stats.svg")
