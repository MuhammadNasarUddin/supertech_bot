from flask import Flask, render_template, request, redirect, url_for, flash, session
from bot import supertec_bot

supertec = supertec_bot()

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Set a secret key for session management
message_history = []

@app.route('/')
def index():
    if 'logged_in' not in session or not session['logged_in']:
        return redirect(url_for('login'))
    return render_template('index.html', messages=message_history)

@app.route('/chat', methods=['POST'])
def chat():
    if request.method == 'POST':
        user_input = request.form['user_input']
        try:
            answer = supertec.user_chat(user_input)
        except Exception as e:
            # Handle the exception, you might want to log the error or take other actions
            error_message = f"Error: {e}"
            # For simplicity, let's display an error message instead of the bot's response
            answer = "Apologies, there was an error processing your request."

        # Append the user and bot messages to message_history
        message_history.append({'type': 'user', 'content': user_input})
        message_history.append({'type': 'bot', 'content': answer})

        return render_template('index.html', messages=message_history)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == "admin@gmail.com" and password == "admin123":
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')



@app.route('/logout', methods=['POST'])
def logout():
    if 'logged_in' in session:
        session.pop('logged_in')  # Remove the 'logged_in' session variable
        flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, port=5002)











# import requests


# def get_attendance(id, month, year):
#     headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0'}
#     payload = {'company_token': 'II@tNfQ70O'}
#     response = requests.get(f"https://superteclabs.com/apis2/AttendanceRecord.php?id={id}&month={month}&year={year}", headers=headers, data=payload)
#     id_ty = type(id)    
#     print(id_ty)
#     return response.text

# abc = get_attendance(217, 'September', 2023)
# print(abc)



# def get_detail():
#             import requests
#             headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0' }
#             payload = {'company_token': 'II@tNfQ70O'}
#             response = requests.post("https://superteclabs.com/apis2/retrieveallusers.php", data=payload,headers=headers)
#             return response.text
        
#         def get_attendance(id,month,year):
#             import requests
#             headers = { 'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0' }
#             payload = {'company_token': 'II@tNfQ70O'}
#             response = requests.get(f"https://superteclabs.com/apis2/AttendanceRecord.php?id={id}&month={month}&year={year}",headers=headers , data=payload )
#             return response.json()
        
 