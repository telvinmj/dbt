import os

def check_projects(projects_dir):
    """Check if dbt projects are properly detected and if their files exist."""
    print(f"Projects directory path: {os.path.abspath(projects_dir)}")
    
    # List all directories in the projects directory
    all_dirs = [d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))]
    print(f"All directories in projects dir: {all_dirs}")
    
    # Get all dbt project directories (must have dbt_project.yml)
    project_dirs = [d for d in os.listdir(projects_dir) 
                   if os.path.isdir(os.path.join(projects_dir, d)) 
                   and os.path.exists(os.path.join(projects_dir, d, "dbt_project.yml"))
                   and not d.startswith('.')]
    
    print(f"Found {len(project_dirs)} dbt projects: {', '.join(project_dirs)}")
    
    for project in project_dirs:
        manifest_path = os.path.join(projects_dir, project, "target", "manifest.json")
        catalog_path = os.path.join(projects_dir, project, "target", "catalog.json")
        
        print(f"\nProject: {project}")
        print(f"  dbt_project.yml exists: {os.path.exists(os.path.join(projects_dir, project, 'dbt_project.yml'))}")
        print(f"  target directory exists: {os.path.exists(os.path.join(projects_dir, project, 'target'))}")
        print(f"  manifest.json exists: {os.path.exists(manifest_path)}")
        print(f"  manifest path: {manifest_path}")
        print(f"  catalog.json exists: {os.path.exists(catalog_path)}")
        print(f"  catalog path: {catalog_path}")
        
        # List files in target directory
        target_dir = os.path.join(projects_dir, project, "target")
        if os.path.exists(target_dir):
            target_files = os.listdir(target_dir)
            print(f"  Files in target directory: {target_files}")
        else:
            print("  Target directory not found")

if __name__ == "__main__":
    check_projects("../dbt_project_3") 