from flask import Flask, render_template, redirect, request, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///combined.db'
db = SQLAlchemy(app)

# Define ToDo model
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(200), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<Task %r>' % self.id

# Define Expense model
class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now())
    category = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Expense %r>' % self.id 


# Homepage route
@app.route('/')
def index():
    return render_template('index.html')

# ToDo List route
@app.route('/todo', methods=['POST', 'GET'])
def todo():
    if request.method == 'POST':
        task_urgency = request.form['type']
        task_content = request.form['content']
        new_task = Todo(type=task_urgency, content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/todo')
        except:
            return "There was an error adding your new task!"
        
    elif request.method == 'GET' and request.args.get('sort') == 'priority':
        tasks = Todo.query.order_by(Todo.type).all()
        return render_template('todo.html', tasks=tasks)
    elif request.method == 'GET' and request.args.get('sort') == 'date':
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('todo.html', tasks=tasks)
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('todo.html', tasks=tasks)

# Expense Tracker route
@app.route('/expenses', methods=['POST', 'GET'])
def expenses():
    budget_limits = {
        'Self' : 5000,
        'House' : 10000,
        'Office' : 5000
    }
    category_budget_usage = {}
    if request.method == 'POST':
        amount_spent = request.form['amount']
        category_spent = request.form['category']
        description_spent = request.form['description']
        new_expense = Expense(amount=amount_spent, category=category_spent, description=description_spent)

        try:
            db.session.add(new_expense)
            db.session.commit()
            return redirect('/expenses')
        except:
            return "There was an error adding your expense!"
        
    else:
        for category in budget_limits:
            expenses_in_category = Expense.query.filter_by(category=category).all()
            total_expenses_category = sum(expense.amount for expense in expenses_in_category )
            remaining_budget_category = budget_limits[category] - total_expenses_category
            budget_percentage_category = (total_expenses_category/budget_limits[category])*100

            category_budget_usage[category]={
                'total_expenses':total_expenses_category,
                'remaining_budget':remaining_budget_category,
                'budget_percentage': budget_percentage_category
            }
        category_filter = request.args.get('category')
        if category_filter:
            expenses = Expense.query.filter_by(category=category_filter).order_by(Expense.date).all()
        else:
            expenses = Expense.query.order_by(Expense.date).all()
        total_expenses = sum(expense.amount for expense in expenses)
        budget = sum(budget_limits.values())
        remaining_balance = budget - total_expenses
        return render_template('expenses.html', expenses=expenses, total_expenses=total_expenses, remaining_balance=remaining_balance,category_budget_usage=category_budget_usage)

#delete route for todo list
@app.route('/delete_todo/<int:id>')
def delete_todo(id):
    del_task = Todo.query.get_or_404(id)
    try:
        db.session.delete(del_task)
        db.session.commit()
        return redirect('/todo')
    except:
        return "There was an error deleting expense"


#delete route for expense tracker
@app.route('/delete_exp/<int:id>')
def delete_exp(id):
    del_expense = Expense.query.get_or_404(id)
    try:
        db.session.delete(del_expense)
        db.session.commit()
        return redirect('/expenses')
    except:
        return "There was an error deleting expense"


#update route for todo list
@app.route('/update_todo/<int:id>', methods=['POST','GET'])
def  update_todo(id):
    task = Todo.query.get_or_404(id)
    if request.method =="POST":
        task.type = request.form['type']
        task.content  = request.form['content']
        try:
            db.session.commit()
            return redirect('/todo')
        except:
            return "Issue while updating task!"
    else:
        return render_template('update_todo.html',task=task)

#update route for expense tracker
@app.route('/update_expenses/<int:id>',methods=['POST','GET'])
def update_expenses(id):
    expense = Expense.query.get_or_404(id)
    if request.method == "POST":
        expense.amount = request.form['amount']
        expense.category = request.form['category']
        expense.description = request.form['description']
        try:
            db.session.commit()
            return redirect('/expenses')
        except:
            return "An issue occured while updating task!"
    else:
        return render_template('update_expenses.html',expense=expense)


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
