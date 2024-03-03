from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('registration.html')

@app.route('/register', methods=['POST'])
def register():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')

    # Add your validation logic here (e.g., check if passwords match)

    # Assuming a simple success message for now
    return f'Registration successful! Welcome, {name}.'

if __name__ == '__main__':
    app.run(debug=True)
