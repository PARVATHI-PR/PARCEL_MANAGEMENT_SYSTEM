from flask import Flask, render_template,request
import subprocess
app=Flask(__name__)
@app.route('/')
def home():
   return render_template('index.html')
@app.route('/register')
def register():
   return render_template('register.html')
#form submission
@app.route('/book',methods=['POST'])
def book():
   #feeding data
   #sender data
    sender_name = request.form['senderName']
    sender_phone = request.form['senderPhone']
    sender_address = request.form['senderAddress']
    sender_city =request.form['senderCity']
#receiver details
    receiver_name = request.form['receiverName']
    receiver_phone = request.form['receiverPhone']
    receiver_address = request.form['receiverAddress']
    receiver_city =request.form['receiverCity']


#parcel details 
    weight = request.form['weight']
    parcel_type = request.form['parcelType']
    spl_instruction = request.form['specialInstructions']

#run c 
    result = subprocess.run(["program.exe"],
            input=f"{sender_name}\n{sender_address}\n{sender_city}\n{sender_phone}\n"
              f"{receiver_name}\n{receiver_address}\n{receiver_city}\n{receiver_phone}\n"
              f"{weight}\n{parcel_type}\n{spl_instruction}\n",
        text=True,
        capture_output=True
)
    output = result.stdout

    #tracking
    tracking="Null"
    booking_datetime = "Not Found"
    for line in output.splitlines():
        line=line.strip()
        if "Tracking No" in line:
         tracking = line.split(":",1)[1].strip()
        if "Date" in line:
         booking_datetime = line.split(":",1)[1].strip() 
    #send html
    return render_template("confirm.html",
        sender_name=sender_name,
        sender_phone=sender_phone,
        sender_address=sender_address,
        sender_city=sender_city,
        receiver_name=receiver_name,
        receiver_phone=receiver_phone,
        receiver_address=receiver_address,
        receiver_city=receiver_city,
        weight=weight,
        parcel_type=parcel_type,
        spl_instruction=spl_instruction,
        date=booking_datetime,
        tracking=tracking
    )
@app.route('/search')
def search():
    pass     
if __name__ == "__main__":
    app.run(debug=True)