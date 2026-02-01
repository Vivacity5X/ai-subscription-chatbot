from flask import Flask, render_template, request, jsonify
import mysql.connector
from datetime import date

app = Flask(__name__)

db = mysql.connector.connect(
    host="localhost",
    user="chatbot",
    password="chatbot123",
    database="subscription_chatbot"
)



cursor = db.cursor(dictionary=True)

USER_ID = 1  # Demo user

# -------- NLP Intent Detection --------
def detect_intent(msg):
    msg = msg.lower()

    if "plan" in msg and ("show" in msg or "view" in msg):
        return "view_plans"
    if "subscribe" in msg:
        return "subscribe"
    if "upgrade" in msg:
        return "upgrade"
    if "cancel" in msg:
        return "cancel"
    if "billing" in msg or "payment" in msg:
        return "billing"
    if "status" in msg or "current" in msg:
        return "status"
    return "unknown"

# -------- Business Logic --------
def show_plans():
    cursor.execute("SELECT * FROM subscription_plans")
    plans = cursor.fetchall()
    reply = "📦 Available Plans:\n"
    for p in plans:
        reply += f"\n{p['plan_name']} – ₹{p['price']}\n{p['features']}\n"
    return reply

def subscribe_plan(plan_name):
    cursor.execute("SELECT plan_id,price FROM subscription_plans WHERE plan_name=%s",(plan_name,))
    plan = cursor.fetchone()
    if not plan:
        return "❌ Plan not found."

    cursor.execute("DELETE FROM user_subscriptions WHERE user_id=%s",(USER_ID,))
    cursor.execute(
        "INSERT INTO user_subscriptions (user_id,plan_id,status,start_date) VALUES (%s,%s,'active',%s)",
        (USER_ID, plan['plan_id'], date.today())
    )
    cursor.execute(
        "INSERT INTO billing_history (user_id,plan_id,amount,payment_date) VALUES (%s,%s,%s,%s)",
        (USER_ID, plan['plan_id'], plan['price'], date.today())
    )
    db.commit()
    return f"✅ Subscribed to {plan_name} plan successfully!"

def current_status():
    cursor.execute("""
        SELECT p.plan_name FROM user_subscriptions u
        JOIN subscription_plans p ON u.plan_id=p.plan_id
        WHERE u.user_id=%s AND u.status='active'
    """,(USER_ID,))
    sub = cursor.fetchone()
    if not sub:
        return "❌ No active subscription."
    return f"📌 Your current plan is: {sub['plan_name']}"

def cancel_plan():
    cursor.execute("UPDATE user_subscriptions SET status='cancelled' WHERE user_id=%s",(USER_ID,))
    db.commit()
    return "❌ Your subscription has been cancelled."

def billing_history():
    cursor.execute("""
        SELECT p.plan_name, b.amount, b.payment_date
        FROM billing_history b
        JOIN subscription_plans p ON b.plan_id=p.plan_id
        WHERE b.user_id=%s
    """,(USER_ID,))
    records = cursor.fetchall()
    if not records:
        return "No billing records found."

    reply = "💳 Billing History:\n"
    for r in records:
        reply += f"\n{r['plan_name']} – ₹{r['amount']} on {r['payment_date']}"
    return reply

# -------- Routes --------
@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    msg = request.json["message"]
    intent = detect_intent(msg)

    if intent == "view_plans":
        reply = show_plans()
    elif intent == "subscribe":
        if "basic" in msg.lower():
            reply = subscribe_plan("Basic")
        elif "pro" in msg.lower():
            reply = subscribe_plan("Pro")
        elif "premium" in msg.lower():
            reply = subscribe_plan("Premium")
        else:
            reply = "Please specify a plan name."
    elif intent == "status":
        reply = current_status()
    elif intent == "cancel":
        reply = cancel_plan()
    elif intent == "billing":
        reply = billing_history()
    else:
        reply = "🤖 Sorry, I didn't understand. Try: show plans / subscribe / billing"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
