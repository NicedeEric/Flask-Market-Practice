from stripe.api_resources import checkout
from market import app, db
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, PurchaseItemForm, SellItemForm
from flask_login import login_user, logout_user, login_required, current_user
import stripe

app.config[
    'STRIPE_PUBLIC_KEY'] = 'pk_test_51Izc1zJvJNLl4RaydOM9onfV6KvqsvAbok7CoUnzhTbBgDP3Pks3hsw5inPfsWZzLbJTw9KktXU9raYRsZL7ws2700BgOxA7We'
app.config[
    'STRIPE_SECRET_KEY'] = 'sk_test_51Izc1zJvJNLl4Ray0wN1W4W8Ar94TRq1bFXJADuBEVNk4Z00b9UKdt8UuneEhh41vzeixMfEdjTiwWXiBSHYIp9e00L84SQDeM'
stripe.api_key = app.config['STRIPE_SECRET_KEY']


@app.route('/')
@app.route('/home')
def home_page():
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': 2000,
                    'product_data': {
                        'name': 'Stubborn Attachments',
                        'images': ['https://i.imgur.com/EHyR2nP.png'],
                    },
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url=url_for('thanks_page', _external=True) +
        '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('home_page', _external=True),
    )

    return render_template(
        'home.html',
        checkout_session_id=session['id'],
        checkout_public_key=app.config['STRIPE_PUBLIC_KEY'],
    )


@app.route('/market', methods=['GET', "POST"])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    sell_form = SellItemForm()
    if request.method == "POST":
        # purchase item
        purchased_item = request.form.get('purchased_item')
        p_item_object = Item.query.filter_by(name=purchased_item).first()
        if p_item_object:
            if current_user.can_purchase(p_item_object):
                current_user.buy(p_item_object)
                flash(
                    f'Congratulations! You have purchased {p_item_object.name} for {p_item_object.price}$!',
                    category='success')
            else:
                flash(
                    f"Unfortunately, you don't have enough money to purchase",
                    category='danger')

        # sell item
        sold_item = request.form.get('sold_item')
        s_item_object = Item.query.filter_by(name=sold_item).first()
        if s_item_object:
            if current_user.can_sell(s_item_object):
                current_user.sell(s_item_object)
                flash(
                    f'Congratulations! You have sold {s_item_object.name} for {s_item_object.price}$!',
                    category='success')
            else:
                flash(
                    "Something went wrong, you can't sell this item since you don't own it!",
                    category='danger')
        #redirect to market_page
        return redirect(url_for('market_page'))

    if request.method == 'GET':
        items = Item.query.filter_by(owner=None)
        owned_items = Item.query.filter_by(owner=current_user.id)
        return render_template(
            'market.html',
            items=items,
            purchase_form=purchase_form,
            owned_items=owned_items,
            sell_form=sell_form,
        )


@app.route('/thanks')
def thanks_page():
    return f'<h1>Thank you!</h1>'


@app.route('/register', methods=['POST', 'GET'])
def register_page():
    form = RegisterForm()
    # check whether the user have pressed the submit button
    # form.validate()
    if form.validate_on_submit():
        print('validated')
        user_to_create = User(username=form.username.data,
                              email_address=form.email_address.data,
                              password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(
            f'Account created successfully! You are now logged in as: {user_to_create.username}',
            category='success')
        return redirect(url_for('market_page'))

    # display error message when resgister
    if form.errors != {}:  #if there are errors from the validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating an user: {err_msg}',
                  category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            attempted_user = User.query.filter_by(
                username=form.username.data).first()
            if attempted_user:
                if attempted_user.check_password_correction(
                        attempted_password=form.password.data):
                    login_user(attempted_user)
                    flash(
                        f'Success! You are logged in as: {attempted_user.username}',
                        category='success')
                    return redirect(url_for('market_page'))
                else:
                    flash("Username and password don't match!",
                          category='danger')
                    return redirect(url_for('login_page'))
            else:
                flash("Username doesn't exist!", category='danger')
                return redirect(url_for('login_page'))

    if request.method == 'GET':
        return render_template('login.html', form=form)


@app.route('/logout')
def logout_page():
    logout_user()
    flash(f'You have been logged out', category='info')
    return redirect(url_for('home_page'))