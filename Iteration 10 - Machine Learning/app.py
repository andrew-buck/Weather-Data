import flask
import flask_sqlalchemy
from sqlalchemy import create_engine, text
import weather_data as wd
import io
import base64
import matplotlib.pyplot as plt
from models.multivariate_forecaster import MultivariateForecaster

# Initialize Flask app
app = flask.Flask(__name__)

# Configure SQLite database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = flask_sqlalchemy.SQLAlchemy(app)

# Create WeatherData instance
weather = None

def get_weather_data():
    """
    Lazy initialization of the weather data instance
    """
    global weather
    if weather is None:
        try:
            # Create weather data
            weather = wd.WeatherData(None)
            # Update from database
            weather.update_from_database()
        except Exception as e:
            print(f"Error initializing weather data: {e}")
    return weather

@app.route('/')
def index():
    """
    The main page of the web application.
    """
    return flask.render_template('index.html')

@app.route('/visualizer')
def visualizer():
    """
    Page for visualizing weather data with charts.
    """
    # Get locations from database
    locations = []
    try:
        # Use SQLAlchemy to query distinct locations
        engine = create_engine('sqlite:///weather.db')
        with engine.connect() as conn:
            # Wrap SQL in text() to make it executable
            result = conn.execute(text("SELECT DISTINCT location FROM weather ORDER BY location"))
            locations = [row[0] for row in result]
    except Exception as e:
        print(f"Error fetching locations: {e}")
    
    return flask.render_template('visualizer.html', locations=locations)

@app.route('/generate-chart', methods=['POST'])
def generate_chart():
    """Generate a chart based on form data"""
    try:
        # Get form data
        location = flask.request.form.get('location')
        chart_type = flask.request.form.get('chart_type')
        
        if not location or not chart_type:
            return flask.jsonify({'error': 'Missing parameters'})
            
        # Initialize weather data if needed
        weather_data = get_weather_data()
        weather_data.update_from_database()
        # Generate the appropriate chart
        fig = None
        if chart_type == 'daily_rain':
            fig = weather_data.daily_rain(location)
        elif chart_type == 'weekly_rain':
            fig = weather_data.weekly_rain(location)
        elif chart_type == 'humidity':
            fig = weather_data.daily_humidity(location)
        elif chart_type == 'temperature':
            fig = weather_data.daily_temperature(location)
        elif chart_type == 'windy_days':
            fig = weather_data.windy_days(location)
        # Convert matplotlib figure to base64 image
        if fig:
            img_data = io.BytesIO()
            fig.savefig(img_data, format='png', bbox_inches='tight')
            img_data.seek(0)
            img_base64 = base64.b64encode(img_data.getvalue()).decode('utf-8')
            plt.close(fig)  # Close the figure to free memory
            
            return flask.jsonify({
                'success': True,
                'image': f'data:image/png;base64,{img_base64}'
            })
        
        return flask.jsonify({'error': 'Could not generate chart'})
        
    except Exception as e:
        print(f"Error generating chart: {e}")
        return flask.jsonify({'error': str(e)})

@app.route('/forecast')
def forecast_page():
    """
    Page for displaying weather forecasts using the multivariate forecaster model.
    """
    # Get locations from database
    locations = []
    try:
        # Initialize the forecaster
        forecaster = MultivariateForecaster()
        # Get available locations from forecaster
        locations = forecaster.get_available_locations()
        locations.sort()  # Sort locations alphabetically
    except Exception as e:
        print(f"Error fetching forecast locations: {e}")
    
    return flask.render_template('forecast.html', locations=locations)

@app.route('/generate-forecast', methods=['POST'])
def generate_forecast():
    """Generate a forecast based on form data"""
    try:
        # Get form data
        location = flask.request.form.get('location')
        days = int(flask.request.form.get('days', 7))
        
        if not location:
            return flask.jsonify({'error': 'Missing location parameter'})
            
        # Initialize forecaster
        forecaster = MultivariateForecaster()
        
        # Limit days to valid values (1, 3, or 7)
        if days not in [1, 3, 7]:
            days = 7
            
        # Generate forecast for the location
        forecast_data = forecaster.forecast(location, days)
        
        return flask.jsonify({
            'success': True,
            'forecast': forecast_data
        })
        
    except Exception as e:
        print(f"Error generating forecast: {e}")
        return flask.jsonify({'error': str(e)})

@app.route('/data-interface')
def data_interface():
    """
    Page for viewing weather data from the database.
    """
    max_id = 0
    locations = []
    try:
        engine = create_engine('sqlite:///weather.db')
        with engine.connect() as conn:
            # Get max ID
            query = text("SELECT MAX(id) as max_id FROM weather")
            result = conn.execute(query).fetchone()
            max_id = result[0] if result and result[0] else 0
            
            # Get distinct locations
            loc_query = text("SELECT DISTINCT location FROM weather ORDER BY location")
            loc_result = conn.execute(loc_query)
            locations = [row[0] for row in loc_result]
    except Exception as e:
        print(f"Error fetching data for interface: {e}")
    
    return flask.render_template('data-interface.html', max_id=max_id, locations=locations)

@app.route('/get-data')
def get_data():
    """
    API endpoint to fetch weather data based on ID range and optional location.
    """
    min_id = flask.request.args.get('min_id', '1')
    max_id = flask.request.args.get('max_id', '999999')
    location = flask.request.args.get('location', '')
    
    # Convert to integers with defaults
    try:
        min_id = int(min_id) if min_id else 1
        max_id = int(max_id) if max_id else 999999
    except ValueError:
        return flask.jsonify({
            'success': False,
            'error': 'Invalid ID values'
        })
    
    try:
        engine = create_engine('sqlite:///weather.db')
        with engine.connect() as conn:
            # Build query based on ID range and optional location
            query_text = "SELECT * FROM weather WHERE id >= :min_id AND id <= :max_id"
            params = {"min_id": min_id, "max_id": max_id}
            
            # Add location filter if provided
            if location:
                query_text += " AND location = :location"
                params["location"] = location
                
            query_text += " ORDER BY id"
            query = text(query_text)
            
            # Execute query with parameters
            result = conn.execute(query, params)
            
            # Convert RMKeyView to list so it can be serialized to JSON
            columns = list(result.keys())
            
            # Get all rows
            rows = [list(row) for row in result]
            
            return flask.jsonify({
                'success': True,
                'columns': columns,
                'rows': rows
            })
    except Exception as e:
        print(f"Error fetching data: {e}")
        return flask.jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/delete-data', methods=['POST'])
def delete_data():
    """
    API endpoint to delete weather data within an ID range.
    """
    try:
        # Get data from request
        data = flask.request.json
        min_id = data.get('min_id')
        max_id = data.get('max_id')
                        
        if not min_id or not max_id:
            return flask.jsonify({
                'success': False,
                'error': 'Missing ID parameters'
            })
            
        # Convert to integers
        try:
            min_id = int(min_id)
            max_id = int(max_id)
        except ValueError:
            return flask.jsonify({
                'success': False,
                'error': 'Invalid ID values'
            })
        
        # Connect to database
        engine = create_engine('sqlite:///weather.db')
        with engine.connect() as conn:
            # Begin transaction
            with conn.begin():
                # Delete records in range
                query = text("DELETE FROM weather WHERE id >= :min_id AND id <= :max_id")
                result = conn.execute(query, {"min_id": min_id, "max_id": max_id})
                
                # Get new max ID after deletion
                max_query = text("SELECT MAX(id) as max_id FROM weather")
                max_result = conn.execute(max_query).fetchone()
                new_max_id = max_result[0] if max_result and max_result[0] else 0
                
                # Get count of deleted rows
                rows_deleted = result.rowcount
            # Update pandas dataframe
            global weather
            weather = get_weather_data()
            weather.update_from_database()
            return flask.jsonify({
                'success': True,
                'message': f'Successfully deleted {rows_deleted} record(s)',
                'new_max_id': new_max_id
            })
            
    except Exception as e:
        print(f"Error deleting data: {e}")
        return flask.jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/data-insertion')
def data_insertion():
    """
    Page for inserting new weather data records.
    """
    return flask.render_template('data-insertion.html')

@app.route('/insert-data', methods=['POST'])
def insert_data():
    """
    API endpoint to insert a new weather data record.
    """
    try:
        # Get JSON data from request
        data = flask.request.json
        
        # Validate required fields
        required_fields = ['location']
        for field in required_fields:
            if field not in data or not data[field]:
                return flask.jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                })
        
        # Connect to database
        engine = create_engine('sqlite:///weather.db')
        
        # First, inspect the table schema to get column names (in a separate connection)
        db_columns = []
        with engine.connect() as inspect_conn:
            inspect_query = text("PRAGMA table_info(weather)")
            columns_info = inspect_conn.execute(inspect_query).fetchall()
            db_columns = [col[1] for col in columns_info]
            print(f"Database columns: {db_columns}")
        
        # Map form fields to database columns
        field_mapping = {
            'row_id': 'row_id',
            'location': 'location',
            'mintemp': 'min_temp',         
            'maxtemp': 'max_temp',         
            'rainfall': 'rainfall',
            'evaporation': 'evaporation',
            'sunshine': 'sunshine',
            'windgustdir': 'wind_gust_dir', 
            'windgustspeed': 'wind_gust_speed', 
            'winddir9am': 'wind_dir_9am',  
            'winddir3pm': 'wind_dir_3pm',  
            'windspeed9am': 'wind_speed_9am', 
            'windspeed3pm': 'wind_speed_3pm', 
            'humidity9am': 'humidity_9am',   
            'humidity3pm': 'humidity_3pm',   
            'pressure9am': 'pressure_9am',   
            'pressure3pm': 'pressure_3pm',   
            'cloud9am': 'cloud_9am',         
            'cloud3pm': 'cloud_3pm',         
            'temp9am': 'temp_9am',           
            'temp3pm': 'temp_3pm',           
            'raintoday': 'rain_today'        
        }
        
        # Dynamically adjust mapping based on actual database columns
        adjusted_mapping = {}
        for form_field, mapped_field in field_mapping.items():
            if mapped_field in db_columns:
                # If the mapping is correct, use it
                adjusted_mapping[form_field] = mapped_field
            elif form_field in db_columns:
                # If the form field name matches a column, use that
                adjusted_mapping[form_field] = form_field
            else:
                # Try lowercase version for compatibility
                lowercase_field = form_field.lower()
                if lowercase_field in db_columns:
                    adjusted_mapping[form_field] = lowercase_field
        
        # Build INSERT query with verified columns
        columns = []
        values = []
        params = {}
        
        for form_field, db_field in adjusted_mapping.items():
            if form_field in data and data[form_field] != '' and form_field != 'row_id' and db_field in db_columns:
                columns.append(db_field)
                values.append(f":{db_field}")
                params[db_field] = data[form_field]
        
        if not columns:
            return flask.jsonify({
                'success': False,
                'error': 'No valid columns to insert'
            })
        
        # Now perform the actual insertion in a new connection with transaction
        with engine.connect() as conn:
            with conn.begin():
                # Execute INSERT query
                query = text(f"INSERT INTO weather ({', '.join(columns)}) VALUES ({', '.join(values)})")
                result = conn.execute(query, params)
                
                # Get ID of inserted record
                id_query = text("SELECT last_insert_rowid()")
                inserted_id = conn.execute(id_query).scalar()
        
        # Update pandas dataframe
        global weather
        weather = get_weather_data()
        weather.update_from_database()
        # Return success response
        return flask.jsonify({
            'success': True,
            'message': f'Successfully inserted record with ID {inserted_id}',
            'id': inserted_id
        })
            
    except Exception as e:
        print(f"Error inserting data: {e}")
        return flask.jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(threaded = False, debug = False)