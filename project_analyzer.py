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
    project_structure = defaultdict(lambda: {"dirs": [], "files": {}})
    all_dependencies = set()
    file_count = 0
    dir_count = 0
    language_stats = defaultdict(int)
    
    for root, dirs, files in os.walk(base_dir):
        if max_depth is not None:
            current_depth = root[len(base_dir):].count(os.path.sep)
            if current_depth > max_depth:
                logging.info(f"Reached max depth at {root}, skipping further subdirectories")
                del dirs[:]
                continue
        
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith('.')]
        dir_count += len(dirs)
        
        relative_path = os.path.relpath(root, base_dir)
        if relative_path == '.':
            relative_path = os.path.basename(base_dir)
        
        project_structure[relative_path]["dirs"] = dirs
        
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
                project_structure[relative_path]["files"][file] = "File skipped (binary file)"
                continue
            
            content = read_file(file_path)
            if content is not None:
                project_structure[relative_path]["files"][file] = content
                file_dependencies = analyze_dependencies(file_path, content)
                all_dependencies.update(file_dependencies)
            else:
                project_structure[relative_path]["files"][file] = "Error reading file: Unable to decode"

    logging.info(f"Analyzed {file_count} files in {dir_count} directories")
    return project_structure, all_dependencies, file_count, dir_count, language_stats

def generate_tree(structure, prefix=""):
    """Generate a tree-like structure of the project."""
    tree = []
    items = list(structure.items())
    for i, (path, content) in enumerate(items):
        is_last = i == len(items) - 1
        tree.append(f"{prefix}{'└── ' if is_last else '├── '}{os.path.basename(path)}/")
        if content['dirs'] or content['files']:
            extension = "    " if is_last else "│   "
            if content['dirs']:
                tree.extend(generate_tree({d: structure[os.path.join(path, d)] for d in content['dirs']}, prefix + extension))
            for j, file in enumerate(content['files']):
                is_last_file = j == len(content['files']) - 1 and not content['dirs']
                tree.append(f"{prefix}{extension}{'└── ' if is_last_file else '├── '}{file}")
    return tree

def generate_ai_prompt(project_name, file_count, dir_count, language_stats, dependencies):
    """Generate an AI prompt describing the project."""
    top_languages = sorted(language_stats.items(), key=lambda x: x[1], reverse=True)[:5]
    language_summary = ", ".join(f"{ext[1:]} ({count} files)" for ext, count in top_languages if ext != '.')
    
    prompt = f"""Analyze the following project:

Project Name: {project_name}
Total Files: {file_count}
Total Directories: {dir_count}
Main Languages/File Types: {language_summary}
Key Dependencies: {', '.join(list(dependencies)[:10])}

This project appears to be a {project_name} with a focus on {top_languages[0][0][1:] if top_languages else 'unknown'} development. 
Based on the structure and dependencies, it seems to be a {project_name} that likely involves {top_languages[0][0][1:] if top_languages else 'unknown'} programming.

Please analyze the project structure and contents provided below, and give insights on:
1. The overall architecture of the project
2. Main functionalities or purpose of the project
3. Potential areas for improvement or optimization
4. Any security concerns or best practices that should be implemented
5. Suggestions for scaling this project if needed

Project structure and contents follow:

"""
    return prompt

def write_project_analysis(project_structure, dependencies, output_file, project_name, file_count, dir_count, language_stats):
    """Write the project analysis to a file."""
    try:
        with open(output_file, 'w', encoding='utf-8') as out_file:
            ai_prompt = generate_ai_prompt(project_name, file_count, dir_count, language_stats, dependencies)
            out_file.write(ai_prompt)
            
            out_file.write("\nPROJECT TREE:\n\n")
            tree = generate_tree(project_structure)
            out_file.write("\n".join(tree))
            
            out_file.write("\n\nDETAILED PROJECT STRUCTURE:\n\n")
            for path, content in project_structure.items():
                out_file.write(f"\nDirectory: {path}\n")
                if content['dirs']:
                    out_file.write("  Subdirectories:\n")
                    for d in content['dirs']:
                        out_file.write(f"    {d}\n")
                if content['files']:
                    out_file.write("  Files:\n")
                    for file, file_content in content['files'].items():
                        out_file.write(f"    {file}\n")
                        if not file_content.startswith("File skipped") and not file_content.startswith("Error reading file"):
                            out_file.write(f"      File contents of {file}:\n")
                            out_file.write(f"{file_content}\n")
                            out_file.write(f"{'-'*40}\n")
                        else:
                            out_file.write(f"      {file_content}\n")
            
            out_file.write("\nPROJECT DEPENDENCIES:\n")
            for dep in sorted(dependencies):
                out_file.write(f"  {dep}\n")
        
        logging.info(f"Successfully wrote project analysis to {output_file}")
    except IOError as e:
        logging.error(f"Error writing to output file: {e}")

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
    
    logging.info(f"Starting analysis of project: {base_directory}")
    project_structure, dependencies, file_count, dir_count, language_stats = analyze_project(base_directory, args.depth, script_name, output_filename)
    write_project_analysis(project_structure, dependencies, output_filename, project_name, file_count, dir_count, language_stats)
    logging.info(f"Project analysis has been written to: {output_filename}")
    logging.info(f"Total files analyzed: {file_count}")
    logging.info(f"Total directories analyzed: {dir_count}")

if __name__ == "__main__":
    main()