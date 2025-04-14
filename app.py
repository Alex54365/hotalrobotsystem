from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from mqtt_client import start_mqtt, publish_message, mqtt_client, MQTT_TOPIC
import json
import csv
import os


app = Flask(__name__)

# 配置數據庫
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///customers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 定義數據庫模型
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)

# 初始化數據庫
with app.app_context():
    db.create_all()

start_mqtt()

# 首頁
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/control", methods=["POST"])
def control_esp32():
    data = request.json
    if "command" not in data:
        return jsonify({"status": "error", "message": "缺少指令"}), 400
    
    command = data["command"]
    publish_message(command)  # 發送 MQTT 訊息
    return jsonify({"status": "success", "message": f"已發送指令：{command}"}), 200

# 顯示客戶資料
@app.route('/customers')
def customers():
    all_customers = Customer.query.all()
    return render_template('customers.html', customers=all_customers)

# 新增客戶資料
@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        room = request.form.get('room')
        message = request.form.get('message')

        # 保存到數據庫
        new_customer = Customer(name=name, email=email, room=room, message=message)
        db.session.add(new_customer)
        db.session.commit()

        return redirect(url_for('about',email=email))
    return render_template('form.html')

# 編輯客戶資料
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_customer(id):
    customer = Customer.query.get_or_404(id)
    if request.method == 'POST':
        # 更新數據
        customer.name = request.form['name']
        customer.email = request.form['email']
        customer.room = request.form['room']
        customer.message = request.form['message']
        db.session.commit()
        return redirect('/customers')
    return render_template('edit.html', customer=customer)
    
@app.route('/add_or_update_customer', methods=['POST'])
def add_or_update_customer():
    name = request.form['name']
    email = request.form['email']
    room = request.form['room']
    message = request.form['message']
    
    existing_customer = Customer.query.filter_by(email=email).first()
    if existing_customer:
        # 更新已有記錄
        existing_customer.name = name
        existing_customer.room = room
        existing_customer.message = message
        message = "客戶資料更新成功！"
        
    else:
        # 添加新記錄
        new_customer = Customer(name=name, email=email, room=room, message=message)
        db.session.add(new_customer)
        message = "新客戶添加成功！"
    
    try:
        db.session.commit()
        return message
    except Exception as e:
        db.session.rollback()
        return f"Error: {e}", 500

# 刪除客戶資料
@app.route('/delete/<int:id>', methods=['POST'])
def delete_customer(id):
    customer = Customer.query.get_or_404(id)
    db.session.delete(customer)
    db.session.commit()
    return redirect('/customers')

@app.route('/send/<room>')
def send_order(room):
    room = room.upper()
    if room in ['A', 'B', 'C', 'D']:
        message = f"control:{room}"
        mqtt_client.publish(MQTT_TOPIC, message)
        print(f" 已傳送 MQTT 訂單：{message}")
        return render_template("send.html", room=room)
    else:
        return " 錯誤的房號"

@app.route('/about')
def about():
    email = request.args.get('email')
    if email:
        customer = Customer.query.filter_by(email=email).first()
        if customer:
            return render_template('about.html', customer=customer)
    return redirect(url_for('home'))

    
@app.route('/export')
def export():
    customers = Customer.query.all()

    # 建立 CSV 文件
    output = []
    output.append(['ID', 'Name', 'Email', 'Room', 'Message'])
    for customer in customers:
        output.append([customer.id, customer.name, customer.email, customer.room, customer.message])

    # 將資料轉換為 CSV
    si = "\n".join([",".join(map(str, row)) for row in output])
    response = Response(si, mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment; filename=customers.csv'
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
