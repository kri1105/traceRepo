from src.ml.llm_interface import LLMInterface
from src.core.parser import RepositoryParser

class RepositoryAnalyzer:
    def __init__(self):
        self.llm = LLMInterface()

    def analyze_repository(self, files_data):
        file_structure = ""
        all_content = ""
        dependency_map = {}
        
        # Helper parser for import extraction
        temp_parser = RepositoryParser("") 

        for file in files_data:
            path = file['path']
            file_structure += f"- {path}\n"
            
            # Snippet for AI context
            all_content += f"\n--- FILE: {path} ---\n{file['content'][:1000]}\n"

            if path.endswith('.py'):
                imports = temp_parser.extract_imports(file['content'])
                if imports:
                    dependency_map[path] = imports

        map_str = "\n".join([f"{k} -> {v}" for k, v in dependency_map.items()])

        # --- UPDATED PROMPT ---
        prompt = f"""
        Analyze this GitHub repository based on the provided file list, imports, and code.

        FILE LIST:
        {file_structure}

        DEPENDENCY MAP:
        {map_str}

        CODE SNIPPETS:
        {all_content}

        YOUR TASK:
        1. Explain the 'Workflow' of this project.
        2. Identify the 'Entry Point'.
        3. Visual Graph: Provide a Mermaid.js 'graph TD' diagram. 
           !!! IMPORTANT: You MUST wrap the diagram code in triple backticks and the word mermaid, like this:
           ```mermaid
           graph TD
           ...
           ```
        4. Identify the 'Hub' file.

        Be technical but concise.
        """

        print("🧠 AI is analyzing the workflow...")
        analysis = self.llm.ask_llm(prompt)
        return analysis