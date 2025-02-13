# Smart Composer

**Smart Composer** is a GitHub Action that automatically **categorizes** and **organizes** Markdown files. When you push new `.md` files to a specified folder in your repository, Smart Composer will:

1. Analyze the content with AI.
2. Determine the best matching category from a predefined list.
3. Move the file into the appropriate subfolder (e.g., `docs/<Category>`).

## Key Features

- **Customizable categories**: Pass in your own list of categories as an input.
- **Flexible folder settings**: Configure both the source (“uploads”) and destination (“docs”) folders.
- **Automated file movement**: No more manual reorganizing of files.
- **AI-powered classification**: Let AI handle content analysis and categorization.
- **(Coming soon) Proofreading & Editing**: Automatically refine your Markdown content.

## Requirements

1. A GitHub repository where you have permissions to set up Actions.
2. An **OpenAI API Key** stored as a GitHub secret (e.g., `OPENAI_API_KEY`).
3. Python environment is automatically set up by the Action if you use a composite approach or a Docker-based setup.

## Usage

1. **Add the Action to Your Repository**  
   - If this is your own repository, include the Action files (e.g., `action.yml`, `main.py`) at the root of your project or in a dedicated folder (like `.github/actions/smart-composer`).

2. **Define a Workflow**  
   Create or edit a workflow YAML file in `.github/workflows/`. For example:

   ```yaml
   name: Auto Categorize Markdown
   on:
     push:
       paths:
         - "uploads/*.md"

   jobs:
     categorize:
       runs-on: ubuntu-latest
       steps:
         - name: Check out repository
           uses: actions/checkout@v3

         - name: Use Smart Composer
           uses: facerain/smart-composer@v1
           with:
             openai_api_key: ${{ secrets.OPENAI_API_KEY }}
             categories: "Python,JavaScript,DevOps,Database,Etc"
             uploads_dir: "uploads"
             docs_dir: "docs"
   ```

3. **Configure Your Inputs**  
   - `openai_api_key`: Your OpenAI API key, stored as a secret.  
   - `categories`: A comma-separated list of categories for AI to classify against.  
   - `uploads_dir`: Where your new `.md` files are initially placed.  
   - `docs_dir`: The destination folder where categorized files will be moved.

4. **Add Your Files**  
   - Whenever you push `.md` files into your designated uploads directory (e.g., `uploads/`), this workflow will trigger automatically and organize them into the `docs/<Category>` folders.

5. **Check the Results**  
   - After the workflow runs, open your repository’s `docs/` folder. You should see subfolders matching the categories you specified, each containing the relevant Markdown files.

## Secrets Configuration

1. Go to **Settings > Secrets and variables > Actions** in your repository.
2. Click **New repository secret**.
3. Name it `OPENAI_API_KEY` (or any name you prefer, but make sure it matches the workflow input).
4. Paste your OpenAI API key as the secret’s value and save.

## Example Project Structure

```
my-repo/
├── .github/
│   └── workflows/
│       └── auto-categorize.yml
├── docs/
│   ├── Python/
│   ├── JavaScript/
│   ├── DevOps/
│   ├── Database/
│   └── Etc/
├── uploads/
│   └── example.md
└── README.md
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

1. Fork the project
2. Create a feature branch
3. Submit a Pull Request