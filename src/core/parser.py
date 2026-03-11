import os
import ast 

class RepositoryParser:
    def __init__(self, repo_path):
        self.repo_path = repo_path
        # Define which file extensions you want to analyze
        self.supported_extensions = {'.py', '.js', '.ts', '.md', '.txt'} 

    def get_all_files(self):
        """
        Iterates through the repo and returns a list of dictionaries 
        containing the file path and its content.
        """
        code_data = []

        for root, dirs, files in os.walk(self.repo_path):
            if '.git' in dirs:
                dirs.remove('.git')

            for file in files:
                file_ext = os.path.splitext(file)[1]
                if file_ext in self.supported_extensions:
                    full_path = os.path.join(root, file)
                    
                    try:
                        with open(full_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            relative_path = os.path.relpath(full_path, self.repo_path)
                            code_data.append({
                                "path": relative_path,
                                "content": content
                            })
                    except Exception as e:
                        print(f"Could not read file {full_path}: {e}")

        return code_data
    
    def extract_imports(self, code_content):
        """
        Uses AST to find all local imports in a Python file.
        """
        imports = []
        try:
            # ast.parse converts the text into a tree that Python can "read"
            tree = ast.parse(code_content)
            for node in ast.walk(tree):
                # Handles 'import x'
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                # Handles 'from x import y'
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
        except Exception: 
            # We use a broad Exception here because non-Python files 
            # or Python files with different versions might crash the parser
            pass 
        return imports