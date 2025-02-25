#!/usr/bin/env python
import os
import shutil
import argparse
import re

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_docs_list(docs_dir: str) -> str:
    """
    Traverse the docs_dir and generate a markdown list of categorized files.
    Each category is rendered as a header with a list of Markdown file links.
    """
    content_lines = []
    if not os.path.exists(docs_dir):
        return ""
    for category in sorted(os.listdir(docs_dir)):
        category_path = os.path.join(docs_dir, category)
        if os.path.isdir(category_path):
            content_lines.append(f"### {category}\n")
            for filename in sorted(os.listdir(category_path)):
                if filename.lower().endswith(".md"):
                    file_path = os.path.join(docs_dir, category, filename)
                    # Use relative path for GitHub rendering
                    content_lines.append(f"- [{filename}]({file_path})")
            content_lines.append("")  # Empty line for spacing
    return "\n".join(content_lines)

def update_readme(new_content: str, readme_path: str = "README.md"):
    """
    Update the README.md file by replacing content between
    <!-- START DOCS LIST --> and <!-- END DOCS LIST --> with new_content.
    If the tags do not exist, append them at the end of the file.
    """
    if not os.path.exists(readme_path):
        print(f"[Warn] {readme_path} not found. Skipping README update.")
        return

    with open(readme_path, "r", encoding="utf-8") as f:
        readme_text = f.read()
    
    pattern = re.compile(r"(<!-- START DOCS LIST -->)(.*?)(<!-- END DOCS LIST -->)", re.DOTALL)
    replacement = f"\\1\n{new_content}\n\\3"
    
    if pattern.search(readme_text):
        updated_text = pattern.sub(replacement, readme_text)
    else:
        # If tags are missing, append them at the end of the file.
        updated_text = readme_text + f"\n<!-- START DOCS LIST -->\n{new_content}\n<!-- END DOCS LIST -->\n"
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated_text)
    print(f"[Info] {readme_path} has been updated with the latest docs list.")

def main():
    parser = argparse.ArgumentParser(description="Classify and copy changed MD files.")
    parser.add_argument("--changed-files", type=str, required=True,
                        help="List of changed MD files (comma or newline-separated)")
    parser.add_argument("--categories", type=str, default="Python,JavaScript,DevOps,Database,Etc",
                        help="Comma-separated list of categories.")
    parser.add_argument("--docs-dir", type=str, default="docs",
                        help="Destination folder for categorized files.")
    parser.add_argument("--rewrite", type=bool, default=False,
                        help="Rewrite the content of the changed files.")
    parser.add_argument("--update-readme", type=bool, default=True,
                        help="Update the main README.md with the docs list.")
    parser.add_argument("--make-copy", type=bool, default=False,
                        help="Make a copy of the changed files in the docs directory when same file exists.")
    args = parser.parse_args()

    # categories
    category_list = [cat.strip() for cat in args.categories.split(",")]

    # parse changed files (split on spaces or newlines)
    changed_files = [f.strip() for f in args.changed_files.replace(",", "\n").splitlines() if f.strip()]

    for file_path in changed_files:
        if not file_path or not file_path.endswith(".md"):
            continue  # skip empty lines or non-md files

        if not os.path.exists(file_path):
            print(f"[Warn] {file_path} no longer exists.")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        category = categorize_content(content, category_list)

        category_dir = os.path.join(args.docs_dir, category)
        os.makedirs(category_dir, exist_ok=True)

        base_name = os.path.basename(file_path)
        new_path = os.path.join(category_dir, base_name)

        if args.make_copy:
            new_path = handle_duplicate(new_path)

        shutil.copy2(file_path, new_path)
        print(f"[Info] Copied '{file_path}' → '{new_path}'")

        if args.rewrite:
            new_content = rewrite_content(content)
            with open(new_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"[Info] Rewritten '{file_path}' → '{new_path}'")
    
    if args.update_readme:
        # After processing changed files, update the main README.md with the docs list.
        docs_list = generate_docs_list(args.docs_dir)
        update_readme(docs_list)

def categorize_content(content: str, categories: list) -> str:
    prompt = f"""
    Please read the following Markdown content and choose exactly one of the categories below:
    Categories: {", ".join(categories)}

    Content:
    ---
    {content}
    ---

    If the content does not fit any category, choose 'Etc'.
    Return only the category name, nothing else.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that categorizes content."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
        max_tokens=50
    )
    result = response.choices[0].message.content
    if result is not None:
        result = result.strip()
    else:
        result = ""
    if result not in categories:
        return "Etc"
    return result

def rewrite_content(content: str) -> str:
    prompt = f"""
Please rewrite the following markdown document based on the instructions below.

Instructions:
1. **Title**: Create a concise title that captures the theme of the original document.
2. **Keywords**: Right below the title, list the main keywords in hashtag format (e.g., #keyword1, #keyword2).
3. **Summary**: Provide a brief summary of the core content in one or two sentences. Place the summary right after the keywords.
4. **Content**: Rewrite the original content neatly and logically.
5. **Key Points**: List the most important points from the body.
6. **Follow-up Questions / Discussion Points**: Offer 3 to 5 questions or discussion points based on the content.

Additional Notes:
- Do not alter the original meaning or key information; only rephrase and reorganize as needed.
- The instructions are provided in English, but the rewriting should follow the language of the provided document.
- Please follow the language of the original document. If the original is in Korean, keep the rewrite in Korean.
- If image urls are present, ensure they are still accessible after rewriting. You just using the same image urls.

Here is the document:

{content}
"""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that rewrites content."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0,
    )
    content = (response.choices[0].message.content or "").strip()
    return content

def handle_duplicate(destination_path: str) -> str:
    """If destination_path exists, append '_X' to avoid overwrite."""
    if not os.path.exists(destination_path):
        return destination_path
    base, ext = os.path.splitext(destination_path)
    i = 1
    while True:
        alt = f"{base}_{i}{ext}"
        if not os.path.exists(alt):
            return alt
        i += 1

if __name__ == "__main__":
    main()
