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



