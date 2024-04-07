from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
import json
import requests

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Database initialization
conn = sqlite3.connect('farm_renting_system.db')
c = conn.cursor()

# Create necessary tables
c.execute('''CREATE TABLE IF NOT EXISTS farms
             (id INTEGER PRIMARY KEY, owner_id INTEGER, name TEXT, location TEXT, size INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS new_users
             (id INTEGER PRIMARY KEY, username TEXT, password TEXT, type TEXT, full_name TEXT, email TEXT, contact_number INTEGER, address TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS markers
             (id INTEGER PRIMARY KEY, farm_id INTEGER, latitude FLOAT, longitude FLOAT)''')
c.execute('''CREATE TABLE IF NOT EXISTS registered_lands
            (id INTEGER PRIMARY KEY, owner_id INTEGER, farm_id INTEGER)''')  # Table to track registered lands

# Insert dummy data for previously registered lands
c.execute("INSERT INTO farms (owner_id, name, location, size) VALUES (1, 'Farm 1', 'Location 1, Maharashtra', 10)")
c.execute("INSERT INTO farms (owner_id, name, location, size) VALUES (1, 'Farm 2', 'Location 2, Maharashtra', 15)")
c.execute("INSERT INTO farms (owner_id, name, location, size) VALUES (1, 'Farm 3', 'Location 3, Maharashtra', 20)")
c.execute("INSERT INTO farms (owner_id, name, location, size) VALUES (1, 'Farm 4', 'Location 4, Maharashtra', 25)")

# Insert dummy data for available land locations
c.execute("INSERT INTO farms (owner_id, name, location, size) VALUES (NULL, 'Farm A', 'Location A, Pune', 10)")
c.execute("INSERT INTO farms (owner_id, name, location, size) VALUES (NULL, 'Farm B', 'Location B, Pune', 15)")
c.execute("INSERT INTO farms (owner_id, name, location, size) VALUES (NULL, 'Farm C', 'Location C, Pune', 20)")

conn.commit()
conn.close()

# Landing Page
@app.route('/')
def landing_page():
    return render_template('landing.html')

# Owner Registration Page
@app.route('/farm_owner_registration', methods=['GET', 'POST'])
def farm_owner_registration():
    if request.method == 'POST':
        full_name = request.form['name']
        username = request.form['uname']
        email = request.form['email']
        password = request.form['password']
        contact_number = request.form['number']  

        # Insert owner information into new_users table
        conn = sqlite3.connect('farm_renting_system.db')
        c = conn.cursor()
        c.execute("INSERT INTO new_users (username, password, type, full_name, email, contact_number) VALUES (?, ?, ?, ?, ?, ?)", (username, password, 'owner', full_name, email, contact_number))
        owner_id = c.lastrowid  # Retrieve the ID of the inserted row
        conn.commit()
        conn.close()
        return redirect(url_for('farm_owner_registration_success'))
    return render_template('farm_owner_registration.html')

# Farmer Registration Page
@app.route('/farmer_registration', methods=['GET', 'POST'])
def farmer_registration():
    if request.method == 'POST':
        full_name = request.form['name']
        username = request.form['uname']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['cpassword']  
        contact_number = request.form['number']  
        home_address = request.form['land']
        conn = sqlite3.connect('farm_renting_system.db')
        c = conn.cursor()
        c.execute("INSERT INTO new_users (username, password, type, email, full_name, contact_number, address) VALUES (?, ?, ?, ?, ?, ?, ?)", (username, password, 'farmer', email, full_name, contact_number, home_address))
        conn.commit()
        conn.close()
        return redirect(url_for('farmer_registration_success'))
    return render_template('farmer_registration.html')


# Farm Owner Registration Success Page
@app.route('/farm_owner_registration_success')
def farm_owner_registration_success():
    return render_template('owner_registration_success.html')

# Farmer Registration Success Page
@app.route('/farmer_registration_success')
def farmer_registration_success():
    return render_template('farmer_registration_success.html')

# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['uname']
        password = request.form['password']
        
        conn = sqlite3.connect('farm_renting_system.db')
        c = conn.cursor()
        c.execute("SELECT * FROM new_users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]  # Store the user's ID in the session
            user_type = user[3]
            return redirect(url_for(f"{user_type}_profile"))
        else:
            return redirect(url_for('login'))  # Redirect back to login page if authentication fails
    
    return render_template('login.html')

# Farmer profile page
@app.route('/farmer_profile')
def farmer_profile():
    conn = sqlite3.connect('farm_renting_system.db')
    c = conn.cursor()
    c.execute("SELECT * FROM farms WHERE owner_id IS NULL")
    registered_lands = c.fetchall()
    # c.execute("SELECT * FROM farms WHERE owner_id IS NOT NULL")
    # lands_on_rent = c.fetchall()
    conn.close()
    return render_template('farmer_profile.html', registered_lands=registered_lands)


def get_coordinates(location):
    url = f'https://nominatim.openstreetmap.org/search?format=json&q={location}'
    response = requests.get(url)
    try:
        data = response.json()
        if data and 'lat' in data[0] and 'lon' in data[0]:
            latitude = float(data[0]['lat'])
            longitude = float(data[0]['lon'])
            return latitude, longitude
        else:
            return None, None
    except Exception as e:
        print(f"Error occurred while fetching coordinates: {e}")
        return None, None

# Register Land Route
@app.route('/register_land', methods=['POST'])
def register_land():
    if 'user_id' in session:  # Check if user is logged in
        location = request.form['location']
        size = request.form['size']
        owner_name = request.form['owner_name']
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        # Fetch the current user's ID from the session
        user_id = session['user_id']

        # Insert registered land information into farms table
        conn = sqlite3.connect('farm_renting_system.db')
        c = conn.cursor()
        try:
            c.execute('''INSERT INTO farms (owner_id, location, size, name, latitude, longitude) VALUES (?, ?, ?, ?, ?, ?)''', (user_id, location, size, owner_name, latitude, longitude))
            farm_id = c.lastrowid  # Get the ID of the inserted farm

            # Insert marker data into the markers table
            c.execute('''INSERT INTO markers (farm_id, latitude, longitude) VALUES (?, ?, ?)''', (farm_id, latitude, longitude))
            c.execute('''INSERT INTO markers (farm_id, latitude, longitude) VALUES (?, ?, ?)''', (farm_id, 18.4961, 73.8384))
            c.execute('''INSERT INTO markers (farm_id, latitude, longitude) VALUES (?, ?, ?)''', (farm_id, 18.5074, 73.8077))
            c.execute('''INSERT INTO markers (farm_id, latitude, longitude) VALUES (?, ?, ?)''', (farm_id, 18.5089, 73.9259))
            conn.commit()
            conn.close()

            return 'OK', 200  # Return success response
        except Exception as e:
            print(f"Error inserting land information into database: {e}")
            conn.rollback()
            conn.close()
            return 'Error', 500  # Return error response
    else:
        return 'Unauthorized', 401  # Return unauthorized response if user is not logged in
    
    
# Owner Profile page
@app.route('/owner_profile', methods=['GET', 'POST'])
def owner_profile():
    if 'user_id' in session:  # Check if user is logged in
        if request.method == 'POST':
            # This part is removed as it's causing redundant insertion of land information
            pass

        # Fetch all lands registered by the owner including marker coordinates
        conn = sqlite3.connect('farm_renting_system.db')
        c = conn.cursor()
        user_id = session['user_id']  # Fetch the current user's ID from the session
        c.execute("SELECT farms.*, markers.latitude, markers.longitude FROM farms LEFT JOIN markers ON farms.id = markers.farm_id WHERE farms.owner_id = ?", (user_id,))
        registered_lands = c.fetchall()

        if registered_lands:
            # Serialize registered_lands to JSON
            registered_lands_json = json.dumps(registered_lands)

            # Fetch only the marker coordinates
            marker_coordinates = [[land[2], land[3]] for land in registered_lands if land[2] is not None and land[3] is not None]
        else:
            registered_lands_json = []  # Set default value if no registered lands found
            marker_coordinates = []

        conn.close()

        return render_template('owner_profile.html', registered_lands_json=registered_lands_json, marker_coordinates=marker_coordinates)
    else:
        return redirect(url_for('login'))

# To see the previously registered lands
@app.route('/previously_registered_lands')
def previously_registered_lands():
    if 'user_id' in session:  # Check if user is logged in
        user_id = session['user_id']
        conn = sqlite3.connect('farm_renting_system.db')
        c = conn.cursor()
        c.execute("SELECT farms.*, markers.latitude, markers.longitude FROM farms LEFT JOIN markers ON farms.id = markers.farm_id WHERE farms.owner_id = ? AND farms.id NOT IN (SELECT id FROM farms WHERE owner_id IS NULL)", (user_id,))
        previously_registered_lands = c.fetchall()
        conn.close()
        return jsonify(previously_registered_lands)
    else:
        return redirect(url_for('login'))

# Route to fetch available land locations
@app.route('/available_land_locations')
def available_land_locations():
    conn = sqlite3.connect('farm_renting_system.db')
    c = conn.cursor()
    c.execute("SELECT latitude, longitude FROM farms")
    available_land_locations = c.fetchall()
    conn.close()
    return jsonify(available_land_locations)


# Logout Page
@app.route('/logout', methods=['POST'])
def logout():
    # Remove the user's ID from the session
    session.pop('user_id', None)
    # Redirect to the landing page
    return redirect(url_for('landing_page'))

if __name__ == '__main__':
    app.run(debug=True, port=5005)
