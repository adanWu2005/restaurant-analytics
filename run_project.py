import os
import time
import subprocess

def run_command(command, description):
    """Run a shell command and print status"""
    print(f"\n\n{'='*80}")
    print(f" Running: {description}")
    print(f"{'='*80}\n")
    
    start_time = time.time()
    result = subprocess.run(command, shell=True)
    duration = time.time() - start_time
    
    if result.returncode == 0:
        print(f"\n✅ {description} completed successfully in {duration:.2f} seconds!")
    else:
        print(f"\n❌ {description} failed with exit code {result.returncode}")
        exit(1)

def main():
    """Run the full Restaurant Data Analytics pipeline"""
    # Create necessary directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('visualizations', exist_ok=True)
    
    # Step 1: Generate sample data
    run_command("python data_generator.py", "Data Generation")
    
    # Step 2: Create database
    run_command("python database_setup.py", "Database Setup")
    
    # Step 3: Run ETL pipeline
    run_command("python etl_pipeline.py", "ETL Pipeline")
    
    # Step 4: Run SQL analysis
    run_command("python sql_analysis.py", "SQL Analysis")
    
    # Step 5: Create visualizations
    run_command("python data_visualization.py", "Data Visualization")
    
    # Step 6: Generate insights
    run_command("python insights.py", "Business Insights")
    
    # Step 7: Launch Streamlit dashboard
    print(f"\n\n{'='*80}")
    print(" Launching Streamlit Dashboard")
    print(f"{'='*80}\n")
    print("Starting Streamlit dashboard. Access it at http://localhost:8501")
    print("Press Ctrl+C to stop the dashboard when finished.")
    
    try:
        subprocess.run("streamlit run streamlit_dashboard.py", shell=True)
    except KeyboardInterrupt:
        print("\nDashboard stopped by user.")
    
    print(f"\n\n{'='*80}")
    print(" Restaurant Data Analytics Project Completed Successfully!")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()