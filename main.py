#!/usr/bin/env python
import os
import shutil
import argparse

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
    parser = argparse.ArgumentParser(description="Classify and copy changed MD files.")
    parser.add_argument("--changed-files", type=str, required=True,
                        help="List of changed MD files (comma or newline-separated)")
    parser.add_argument("--categories", type=str, default="Python,JavaScript,DevOps,Database,Etc",
                        help="Comma-separated list of categories.")
    parser.add_argument("--docs-dir", type=str, default="docs",
                        help="Destination folder for categorized files.")
    args = parser.parse_args()

    # categories
    category_list = [cat.strip() for cat in args.categories.split(",")]

    # parse changed files
    changed_files = args.changed_files.split(" ")

    for file_path in changed_files:
        file_path = file_path.strip()
        if not file_path or not file_path.endswith(".md"):
            continue  # skip empty lines or non-md

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

        new_path = handle_duplicate(new_path)

        shutil.copy2(file_path, new_path)
        print(f"[Info] Copied '{file_path}' → '{new_path}'")

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
    result = response.choices[0].message.content.strip()
    if result not in categories:
        return "Etc"
    return result

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
