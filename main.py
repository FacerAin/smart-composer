#!/usr/bin/env python

import os
import shutil
import argparse

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
    # 1) Parse CLI arguments
    parser = argparse.ArgumentParser(description="Classify and move MD files using GPT-based categorization.")
    parser.add_argument("--categories", type=str, default="Python,JavaScript,DevOps,Database,Etc",
                        help="Comma-separated list of categories.")
    parser.add_argument("--uploads-dir", type=str, default="uploads",
                        help="Source folder containing .md files.")
    parser.add_argument("--docs-dir", type=str, default="docs",
                        help="Destination folder for categorized files.")

    args = parser.parse_args()

    # 2) Process category list
    PREDEFINED_CATEGORIES = [cat.strip() for cat in args.categories.split(",")]

    uploads_dir = args.uploads_dir
    docs_dir = args.docs_dir

    # 3) If uploads_dir doesn't exist, create it
    if not os.path.exists(uploads_dir):
        print(f"[Info] '{uploads_dir}' directory does not exist; creating it.")
        os.makedirs(uploads_dir, exist_ok=True)

    # 4) Categorize and move .md files
    for file_name in os.listdir(uploads_dir):
        if file_name.endswith(".md"):
            file_path = os.path.join(uploads_dir, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Categorize using GPT
            category = categorize_content(content, PREDEFINED_CATEGORIES)

            # Create category folder under docs_dir
            category_dir = os.path.join(docs_dir, category)
            os.makedirs(category_dir, exist_ok=True)

            # Move the file
            new_path = os.path.join(category_dir, file_name)
            shutil.move(file_path, new_path)

            print(f"[Info] '{file_name}' → '{category_dir}'")

def categorize_content(content: str, category_list: list) -> str:
    """
    Uses GPT (client.chat.completions) to categorize the content into one of the given categories.
    If the content does not match any predefined category, returns 'Etc'.
    """
    prompt = f"""
    Please read the following Markdown content and choose exactly one of the categories below:
    Categories: {", ".join(category_list)}

    Content:
    ---
    {content}
    ---

    If the content does not fit any category, choose 'Etc'.
    Return only the category name, nothing else.
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that categorizes content into one of the specified categories."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.0,
        max_tokens=50
    )

    result = completion.choices[0].message.content.strip()
    if result not in category_list:
        return "Etc"
    return result

if __name__ == "__main__":
    main()
