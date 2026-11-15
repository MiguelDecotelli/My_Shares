from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FloatField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from my_shares.models import User
from my_shares.my_functions import apology

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder":"Usuário", "autocomplete": False})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder":"Senha"})
    submit = SubmitField('Logar')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder":"Usuário", "autocomplete": False})
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('pass_confirm', message='Senhas devem ser iguais')], render_kw={"placeholder":"Senha"})
    pass_confirm = PasswordField('Confirm Password', validators=[DataRequired()], render_kw={"placeholder":"Confirmar senha"})
    submit = SubmitField('Registrar')

    def validate_username(self, field):
        # WTForms exige que o método comece com 'validate_'
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Que pena, nome de usuário já está em uso!')
        
class ChangePassword(FlaskForm):
    old_password = PasswordField('old_assword', validators=[DataRequired()], render_kw={"placeholder":"Senha atual"})
    new_password = PasswordField('Password', validators=[DataRequired(), EqualTo('pass_confirm', message='Senhas devem ser iguais!')], render_kw={"placeholder":"Nova senha"})
    pass_confirm = PasswordField('Confirm Password', validators=[DataRequired()], render_kw={"placeholder":"Confirme nova senha"})
    submit = SubmitField('Alterar senha')

class QuoteForm(FlaskForm):
    symbol = StringField('Código', validators=[DataRequired()], render_kw={"placeholder": "Ex: PETR4, VALE3", "autocomplete": "off", "autofocus": True})
    submit = SubmitField('Cotar')

class BuyForm(FlaskForm):
    symbol = StringField('Código', validators=[DataRequired()], render_kw={"placeholder": "Ex: PETR4", "autocomplete": "off", "autofocus": True})
    shares = IntegerField('Quantidade', validators=[DataRequired()], render_kw={"placeholder": "Quantas cotas?", "min": "1", "autocomplete": "off"})
    submit = SubmitField('Comprar')

class SellForm(FlaskForm):
    symbol = StringField('Código', validators=[DataRequired()], render_kw={"placeholder": "Ex: PETR4", "autocomplete": "off", "autofocus": True})
    shares = IntegerField('Quantidade', validators=[DataRequired()], render_kw={"placeholder": "Quantas cotas?", "min": "1", "autocomplete": "off"})
    submit = SubmitField('Vender')

class StockListForm(FlaskForm):
    symbol_search = StringField('Pesquisar Empresa', render_kw={"placeholder": "Digite o nome da empresa (Ex: Petrobras)", "autocomplete": "off", "autofocus": True})
    submit = SubmitField('Pesquisar')

class CashForm(FlaskForm):
    add_cash = FloatField('Adicionar Saldo (R$)', validators=[DataRequired()], render_kw={"placeholder": "Informe o Valor", "autocomplete": "off", "autofocus": True})
    add_card = StringField('Cartão de Crédito', validators=[DataRequired()], render_kw={"placeholder": "Número do Cartão (Fictício)", "autocomplete": "off"})
    password = PasswordField('Senha', validators=[DataRequired()], render_kw={"placeholder": "Sua Senha"})
    submit = SubmitField('Adicionar Saldo')

# class QuoteForm(FlaskForm):
#     symbol = StringField('Symbol', validators=[DataRequired()], render_kw={"placeholder":"Symbol", "autocomplete": False, "autofocus": True})
#     submit = SubmitField('Quote')

# class BuyForm(FlaskForm):
#     symbol = StringField('Symbol', validators=[DataRequired()], render_kw={"placeholder":"Symbol", "autocomplete": False, "autofocus": True})
#     shares = IntegerField('Shares', validators=[DataRequired()], render_kw={"placeholder":"Shares", "min":1, "autocomplete": False})
#     submit = SubmitField('Buy')

# class SellForm(FlaskForm):
#     symbol = StringField('Symbol', validators=[DataRequired()], render_kw={"placeholder":"Symbol", "autocomplete": False, "autofocus": True})
#     shares = IntegerField('Shares', validators=[DataRequired()], render_kw={"placeholder":"Shares", "min":1, "autocomplete": False})
#     submit = SubmitField('Sell')


# class StockListForm(FlaskForm):
#     symbol_search = StringField('Symbol Search', render_kw={"placeholder":"Type the Company's Name", "autocomplete": False, "autofocus": True})
#     submit = SubmitField('Search')

# class CashForm(FlaskForm):
#     add_cash = FloatField('Add Cash', validators=[DataRequired()], render_kw={"placeholder":"Inform Amount", "autocomplete": False, "autofocus": True})
#     add_card = StringField('Add Card', validators=[DataRequired()], render_kw={"placeholder":"Inform Credit Card Number", "autocomplete": False})
#     password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder":"Password"})
#     submit = SubmitField('Add Cash')