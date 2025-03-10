# Smart Composer

**Smart Composer** is a GitHub Action that automatically **categorizes** and **organizes** Markdown files. When you push new `.md` files to a specified folder in your repository, Smart Composer will:

1. Analyze the content with AI.
2. Determine the best matching category from a predefined list.
3. Move the file into the appropriate subfolder (e.g., docs/<Category>).
4. Automatically update the main README.md with a categorized list of your Markdown files.
5. (New) Rewrite the content for improved clarity, consistency, and presentation (Proofreading & Editing).

## Key Features

- **Customizable categories**: Pass in your own list of categories as an input.  
- **Automated file organization**: No more manual reorganizing of files.  
- **AI-powered classification**: Let AI handle content analysis and categorization.  
- **Proofreading & Editing**: Automatically refine your Markdown content *(now available!)*  
- **Dynamic README Update**: The Action updates your main `README.md` with a structured list of files sorted into categories.

## Requirements

1. A GitHub repository where you have permissions to set up Actions.  
2. An **OpenAI API Key** stored as a GitHub secret (e.g., `OPENAI_API_KEY`).  
3. Python environment is automatically set up by the Action if you use a composite approach or a Docker-based setup.  
4. **GITHUB_TOKEN Write Permission**:  
   - Go to your repository’s **Settings > Actions > General**.  
   - Scroll down to **Workflow permissions** and select **Read and write permissions**.  
   - Click **Save**.  
   - This ensures that GitHub Actions can push commits back to your repository.

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
       # Grant write permission for committing changes (or set in repo settings)
       permissions:
         contents: write
       steps:
         - name: Check out repository
           uses: actions/checkout@v3

         - name: Use Smart Composer
           uses: FacerAin/smart-composer@v0.1
           with:
             openai_api_key: ${{ secrets.OPENAI_API_KEY }}
             categories: "Python,JavaScript,DevOps,Database,Etc"
             uploads_pattern: "uploads/*.md"
             docs_dir: "docs"
             rewrite: true
             update-readme: true

         # Commit & push changes so the moves and README update are reflected in your repo
         - name: Commit changes
           run: |
             git config user.name "github-actions"
             git config user.email "github-actions@github.com"
             git add .
             git commit -m "Auto categorization and README update" || echo "No changes to commit"
             git push
           shell: bash
   ```

   - By default, all file modifications happen only in the temporary environment if you don’t commit and push.  
   - The `permissions: contents: write` setting (along with your repo’s “Read and write permissions” setting under **Actions > General**) allows GitHub Actions to push changes.

3. **Configure Your Inputs**  
   - `openai_api_key`: Your OpenAI API key, stored as a secret.  
   - `categories`: A comma-separated list of categories for AI to classify against.  
   - `uploads_pattern`: Where your new file patterns are initially placed.  
   - `docs_dir`: The destination folder where categorized files will be moved.  
   - `rewrite`: Set to `true` if you want the content of the Markdown files to be automatically rewritten (proofreading & editing).
   - `update-readme`: Set to `true` if you want the main `README.md` to be updated with the categorized list of files.

4. **Add Your Files**  
   - Whenever you push files into your designated uploads directory (e.g., `uploads/`), this workflow will trigger automatically, organize them into the `docs/<Category>` folders, and update your main `README.md` with a current list of documents.

5. **Check the Results**  
   - After the workflow runs, open your repository’s `docs/` folder to see the categorized Markdown files.  
   - Your main `README.md` will now include a dynamically updated section (between `<!-- START DOCS LIST -->` and `<!-- END DOCS LIST -->`) displaying the categorized file structure.

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

Within your `README.md`, you will see an auto-updated section like:

```markdown
<!-- START DOCS LIST -->
### Database

- [example.md](docs/Database/example.md)

### Etc

- [another-file.md](docs/Etc/another-file.md)

... etc.
<!-- END DOCS LIST -->
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contributing

1. Fork the project  
2. Create a feature branch  
3. Submit a Pull Request