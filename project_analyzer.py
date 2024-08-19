#!/usr/bin/env python3

import os
import sys
import json
import argparse
from collections import defaultdict
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# List of ignored directories
IGNORED_DIRS = {'.git', '.terraform', '__pycache__', 'node_modules', '.venv', '.idea', '.vscode'}
# List of ignored files
IGNORED_FILES = {'.DS_Store', 'Thumbs.db'}

def is_binary(file_path):
    """Check if a file is binary."""
    try:
        with open(file_path, 'rb') as file:
            chunk = file.read(8192)
            return b'\0' in chunk
    except IOError:
        logging.warning(f"Unable to read file: {file_path}")
        return True

def get_file_extension(file_path):
    """Get the file extension."""
    return os.path.splitext(file_path)[1].lower()

def read_file(file_path):
    """Read a file with proper encoding."""
    encodings = ['utf-8', 'latin-1', 'ascii']
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                logging.info(f"Successfully read file: {file_path} with encoding: {encoding}")
                return content
        except UnicodeDecodeError:
            continue
    logging.warning(f"Unable to decode file: {file_path}")
    return None

def analyze_dependencies(file_path, content):
    """Analyze file dependencies."""
    dependencies = set()
    file_extension = get_file_extension(file_path)
    
    if file_extension == '.json' and 'package.json' in file_path:
        try:
            package_data = json.loads(content)
            dependencies.update(package_data.get('dependencies', {}).keys())
            dependencies.update(package_data.get('devDependencies', {}).keys())
        except json.JSONDecodeError:
            logging.warning(f"Unable to parse JSON in file: {file_path}")
    elif file_extension == '.txt' and 'requirements.txt' in file_path:
        dependencies.update(line.strip().split('==')[0] for line in content.splitlines() if line.strip())
    elif file_extension in ['.py', '.js', '.java', '.tf', '.sh']:
        if file_extension == '.py':
            dependencies.update(re.findall(r'^\s*(?:from|import)\s+(\w+)', content, re.MULTILINE))
        elif file_extension == '.js':
            dependencies.update(re.findall(r'(?:import|require)\s*\(\s*[\'"](.+?)[\'"]', content))
        elif file_extension == '.java':
            dependencies.update(re.findall(r'import\s+([\w.]+)', content))
        elif file_extension == '.tf':
            dependencies.update(re.findall(r'source\s*=\s*[\'"](.+?)[\'"]', content))
        elif file_extension == '.sh':
            dependencies.update(re.findall(r'(?:apt-get install|yum install)\s+(.+?)(?:\s|$)', content))
    
    logging.info(f"Found {len(dependencies)} dependencies in file: {file_path}")
    return dependencies

def analyze_project(base_dir, max_depth=None, script_name=None, output_file=None):
    """Analyze the project structure and file contents."""
    project_structure = {}
    all_dependencies = set()
    file_count = 0
    dir_count = 0
    language_stats = defaultdict(int)
    
    for root, dirs, files in os.walk(base_dir):
        if max_depth is not None:
            current_depth = root[len(base_dir):].count(os.path.sep)
            if current_depth > max_depth:
                logging.info(f"Reached max depth at {root}, skipping further subdirectories")
                dirs[:] = []
                continue
        
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith('.')]
        dir_count += len(dirs)
        
        relative_path = os.path.relpath(root, base_dir)
        if relative_path == '.':
            relative_path = os.path.basename(base_dir)
        
        current_level = project_structure
        for part in relative_path.split(os.path.sep):
            if part not in current_level:
                current_level[part] = {'dirs': [], 'files': {}}
            current_level = current_level[part]
        
        current_level['dirs'] = dirs
        
        for file in files:
            if file in IGNORED_FILES or file == script_name or file == output_file:
                logging.info(f"Skipping ignored file: {file}")
                continue
            file_count += 1
            file_path = os.path.join(root, file)
            file_extension = get_file_extension(file_path)
            
            language_stats[file_extension] += 1
            
            if is_binary(file_path):
                logging.info(f"Skipping binary file: {file_path}")
                current_level['files'][file] = "File skipped (binary file)"
                continue
            
            content = read_file(file_path)
            if content is not None:
                current_level['files'][file] = content
                file_dependencies = analyze_dependencies(file_path, content)
                all_dependencies.update(file_dependencies)
            else:
                current_level['files'][file] = "Error reading file: Unable to decode"

    logging.info(f"Analyzed {file_count} files in {dir_count} directories")
    return project_structure, all_dependencies, file_count, dir_count, language_stats

def generate_tree_string(structure, prefix="", is_last=True):
    """Generate a string representation of the project tree."""
    tree = []
    if not isinstance(structure, dict):
        return [f"{prefix}{'└── ' if is_last else '├── '}{structure}"]
    
    items = list(structure.items())
    for i, (name, content) in enumerate(items):
        is_last_item = i == len(items) - 1
        if name in ['dirs', 'files']:
            continue
        tree.append(f"{prefix}{'└── ' if is_last_item else '├── '}{name}/")
        extension = "    " if is_last_item else "│   "
        
        if 'dirs' in content:
            for j, d in enumerate(content['dirs']):
                is_last_dir = j == len(content['dirs']) - 1
                if d in content:
                    tree.extend(generate_tree_string(content[d], prefix + extension, is_last_dir))
                else:
                    tree.append(f"{prefix}{extension}{'└── ' if is_last_dir else '├── '}{d}/")
        
        if 'files' in content:
            files = list(content['files'].keys())
            for j, f in enumerate(files):
                tree.append(f"{prefix}{extension}{'└── ' if j == len(files) - 1 else '├── '}{f}")
    
    return tree

def generate_ai_prompt(project_name, file_count, dir_count, language_stats, dependencies, project_structure):
    """Generate a detailed AI prompt describing the project."""
    top_languages = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    language_summary = ", ".join(f"{ext[1:]} ({count} files)" for ext, count in top_languages if ext != '.')
    
    tree_structure = "\n".join(generate_tree_string(project_structure))

    prompt = f"""Analyze the following project in depth:

PROJECT OVERVIEW:
Project Name: {project_name}
Total Files: {file_count}
Total Directories: {dir_count}
Main Languages/File Types: {language_summary}
Key Dependencies: {', '.join(sorted(dependencies)[:20])}

DETAILED ANALYSIS INSTRUCTIONS:
You are an AI assistant specializing in code analysis and software architecture. Your task is to provide a comprehensive analysis of this project based on the information provided. Please consider the following aspects in your analysis:

1. Project Architecture:
   - Identify the overall architectural pattern (e.g., microservices, monolithic, serverless)
   - Analyze the project structure and how it reflects the architecture
   - Evaluate the separation of concerns and modularity

2. Technology Stack:
   - List the main technologies, frameworks, and languages used
   - Assess the choice of technologies and their suitability for the project

3. Infrastructure and Deployment:
   - Identify any infrastructure-as-code elements (e.g., Terraform files)
   - Analyze the deployment strategy and environment setup

4. Security Considerations:
   - Highlight any security measures implemented in the code
   - Identify potential security risks or areas for improvement

5. Scalability and Performance:
   - Evaluate how well the project is designed to scale
   - Identify any performance optimization techniques used

6. Code Quality and Best Practices:
   - Assess adherence to coding standards and best practices
   - Identify areas where code quality could be improved

7. Testing and Quality Assurance:
   - Analyze the testing approach (unit tests, integration tests, etc.)
   - Suggest improvements in the testing strategy if necessary

8. Documentation:
   - Evaluate the quality and completeness of documentation
   - Suggest areas where documentation could be improved

9. Dependencies and Third-party Integrations:
   - Analyze the use of external dependencies and their management
   - Identify any potential risks associated with third-party integrations

10. Unique Features or Patterns:
    - Highlight any unique or interesting code patterns or architectural decisions
    - Discuss their potential benefits or drawbacks

PROJECT STRUCTURE OVERVIEW:
{tree_structure}

Based on this information, please provide:
1. A comprehensive analysis of the project's architecture and codebase
2. Identification of the main functionalities and purpose of the project
3. Potential areas for improvement or optimization
4. Any security concerns or best practices that should be implemented
5. Suggestions for scaling this project
6. Overall strengths and weaknesses of the project

Your analysis should be detailed, insightful, and provide actionable recommendations for improving the project.
"""
    return prompt

def write_project_analysis(project_structure, dependencies, output_file, project_name, file_count, dir_count, language_stats):
    """Write the project analysis to a file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as out_file:
            ai_prompt = generate_ai_prompt(project_name, file_count, dir_count, language_stats, dependencies, project_structure)
            out_file.write(ai_prompt)
            
            out_file.write("\n\nDETAILED PROJECT STRUCTURE:\n\n")
            write_structure(project_structure, out_file)
            
            out_file.write("\nPROJECT DEPENDENCIES:\n")
            for dep in sorted(dependencies):
                out_file.write(f"  {dep}\n")
        
        logging.info(f"Successfully wrote project analysis to {output_file}")
    except Exception as e:
        logging.error(f"Error writing project analysis: {str(e)}")

def write_structure(structure, file, indent=""):
    for name, content in structure.items():
        if name in ['dirs', 'files']:
            continue
        file.write(f"{indent}{name}/\n")
        if 'dirs' in content:
            for d in content['dirs']:
                if d in content:
                    write_structure({d: content[d]}, file, indent + "  ")
                else:
                    file.write(f"{indent}  {d}/\n")
        if 'files' in content:
            for f, f_content in content['files'].items():
                file.write(f"{indent}  {f}\n")
                if not f_content.startswith("File skipped") and not f_content.startswith("Error reading file"):
                    file.write(f"{indent}    File contents:\n")
                    file.write(f"{f_content}\n")
                    file.write(f"{'-'*40}\n")
                else:
                    file.write(f"{indent}    {f_content}\n")

def main():
    parser = argparse.ArgumentParser(description="Project Structure and Dependency Analyzer")
    parser.add_argument("project_dir", nargs="?", default=".", help="Project directory to analyze (default: current directory)")
    parser.add_argument("-o", "--output", help="Output file name (default: project_name_analysis.txt)")
    parser.add_argument("-d", "--depth", type=int, help="Maximum depth for directory analysis")
    args = parser.parse_args()

    base_directory = os.path.abspath(args.project_dir)
    project_name = os.path.basename(base_directory)
    
    if args.output:
        output_filename = args.output
    else:
        output_filename = f"{project_name}_analysis.txt"
    
    script_name = os.path.basename(__file__)
    
    try:
        logging.info(f"Starting analysis of project: {base_directory}")
        project_structure, dependencies, file_count, dir_count, language_stats = analyze_project(base_directory, args.depth, script_name, output_filename)
        write_project_analysis(project_structure, dependencies, output_filename, project_name, file_count, dir_count, language_stats)
        logging.info(f"Project analysis has been written to: {output_filename}")
        logging.info(f"Total files analyzed: {file_count}")
        logging.info(f"Total directories analyzed: {dir_count}")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        logging.info("The script will attempt to save partial results.")
        try:
            write_project_analysis(project_structure, dependencies, output_filename, project_name, file_count, dir_count, language_stats)
            logging.info(f"Partial analysis has been written to: {output_filename}")
        except Exception as write_error:
            logging.error(f"Failed to write partial results: {str(write_error)}")

if __name__ == "__main__":
    main()
