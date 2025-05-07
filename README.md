# Restaurant Data Analytics Project

A modern data engineering project for analyzing Restaurant food delivery data, built with Python, Mage AI, Google Cloud Platform, BigQuery, and Looker Studio.

## Project Overview

This project creates an end-to-end data pipeline for analyzing food delivery data, simulating a real-world restaurant analytics system. It follows the complete data engineering workflow:

1. **Data Generation** - Creating realistic food delivery datasets
2. **ETL Pipeline** - Extracting, transforming, and loading data
3. **Data Warehousing** - Storing processed data in BigQuery
4. **Data Analysis** - SQL analytics on the prepared data
5. **Data Visualization** - Interactive dashboards in Looker Studio

## Technology Stack

- **Python** - For data generation and transformation
- **Google Cloud Storage** - For storing raw data
- **Google Compute Engine** - For hosting Mage AI
- **Mage AI** - For data pipeline orchestration
- **BigQuery** - For data warehousing and analysis
- **Looker Studio** - For data visualization

## Data Model

The project uses a star schema with the following tables:

- **Dimension Tables**:
  - `datetime_dim` - Time-related attributes
  - `customer_dim` - Customer information
  - `restaurant_dim` - Restaurant details
  - `driver_dim` - Driver information
  - `menu_item_dim` - Menu item details

- **Fact Tables**:
  - `fact_table` - Order transactions
  - `order_items_fact` - Order item details

## How to Run the Project

### Prerequisites

- Python 3.7+ installed
- Google Cloud Platform account (optional for cloud deployment)
- Git installed

### Local Setup

1. **Clone the repository**
git clone https://github.com/yourusername/Restaurant-analytics.git
cd Restaurant-analytics

2. **Create a virtual environment**
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

3. **Install dependencies**
pip install -r requirements.txt

4. **Generate sample data**
python data_generator.py

5. **Set up the database**
python database_setup.py

6. **Run the ETL pipeline**
python etl_pipeline.py

7. **Run SQL analysis**
python sql_analysis.py

8. **Run data visualization**
python data_visualization.py

9. **Launch the dashboard**
streamlit run streamlit_dashboard.py

Alternatively, run the entire pipeline with one command:
python run_project.py

### Cloud Deployment (GCP)

1. **Set up GCP environment**

Create a GCP project
gcloud projects create Restaurant-analytics-project
gcloud config set project Restaurant-analytics-project
Enable required APIs
gcloud services enable compute.googleapis.com storage.googleapis.com bigquery.googleapis.com
Create a Cloud Storage bucket
gsutil mb -l us-central1 gs://Restaurant-analytics-project/

2. **Upload data to Cloud Storage**
gsutil -m cp data/*.csv gs://Restaurant-analytics-project/

3. **Set up Compute Engine and Mage AI**
Create VM
gcloud compute instances create mage-data-pipeline 
--zone=us-central1-a 
--machine-type=e2-standard-4 
--image-family=ubuntu-2004-lts 
--image-project=ubuntu-os-cloud
SSH into VM and install Mage
gcloud compute ssh mage-data-pipeline

4. **Install Mage AI and set up the pipeline**
sudo apt-get update
sudo pip3 install mage-ai
mage start Restaurant_pipeline

5. **Create BigQuery dataset and run the analytics query**
Create dataset
bq mk Restaurant_data
Run analytics query
bq query --use_legacy_sql=false < sql/analytics_query.sql

6. **Set up Looker Studio dashboard** by connecting to the BigQuery table

## Key Analytics

This project enables analysis of:

1. **Order Patterns**
- Peak order hours and days
- Popular meal times
- Seasonal trends

2. **Restaurant Performance**
- Top-performing restaurants
- Popular cuisines
- Price range analysis

3. **Delivery Metrics**
- Average delivery times by area
- Driver performance by vehicle type
- On-time delivery rates

4. **Customer Insights**
- Customer segmentation
- DashPass subscription impact
- Ordering frequency patterns

## Future Enhancements

- Real-time data processing with Kafka
- Machine learning for delivery time prediction
- Advanced geospatial analysis
- Customer churn prediction models

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

