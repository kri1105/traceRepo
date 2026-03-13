from src.ml.llm_interface import LLMInterface
from src.core.parser import RepositoryParser

class RepositoryAnalyzer:
    def __init__(self):
        # Initialize our AI interface
        self.llm = LLMInterface()

    def analyze_repository(self, files_data):
        """
        Combines static analysis (imports) and LLM reasoning to 
        explain the project workflow and visualize it.
        """
        # 1. Prepare Data Containers
        file_structure = ""
        all_content = ""
        dependency_map = {}
        
        # We need a temporary parser instance to use its extract_imports method
        temp_parser = RepositoryParser("") 

        # 2. Process each file
        for file in files_data:
            path = file['path']
            file_structure += f"- {path}\n"
            
            # Add snippet for AI to read (first 1000 chars)
            all_content += f"\n--- FILE: {path} ---\n{file['content'][:1000]}\n"

            # 3. Build Dependency Map for Python files
            if path.endswith('.py'):
                imports = temp_parser.extract_imports(file['content'])
                if imports:
                    dependency_map[path] = imports

        # Create a string version of the dependency map
        map_str = "\n".join([f"{k} -> {v}" for k, v in dependency_map.items()])

        # 4. Craft the Ultimate Master Prompt with Kroki Safety Rules
        prompt = f"""
        Analyze this GitHub repository based on the provided file list, imports, and code.

        FILE LIST:
        {file_structure}

        DEPENDENCY MAP:
        {map_str}

        CODE SNIPPETS:
        {all_content}

        YOUR TASK:
        1. Explain the 'Workflow': How does data or logic move through this project?
        2. Identify the 'Entry Point': Which file should a developer run or read first?
        3. Visual Graph: Provide a Mermaid.js 'graph TD' diagram. 
           
           STRICT RULES FOR THE GRAPH:
           - Use 'graph TD' (Top Down).
           - Use [Square Brackets] for file names, e.g., A[app.py].
           - Use simple arrows: A --> B or A -->|label| B.
           - !!! DANGER: Do NOT use symbols like '>', '(', ')', or '[]' inside labels. 
           - Example: Use A -->|initializes| B instead of A -->|init()|> B.

           !!! IMPORTANT: You MUST wrap the diagram code in triple backticks:
           ```mermaid
           graph TD
           ...
           ```
        4. Identify the 'Hub': Which file is the most critical to the system?

        Be technical but concise.
        """

        print("🧠 AI is analyzing the workflow and mapping dependencies...")
        analysis = self.llm.ask_llm(prompt)
        return analysis