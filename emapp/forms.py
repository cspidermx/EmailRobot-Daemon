from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange
from emapp.models import User


class StartStop(FlaskForm):
    submit = SubmitField('_____')


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Recuerdame')
    submit = SubmitField('Ingresar')


class RegistrationForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repetir Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrar')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Nombre de usuario no disponible.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Dirección de correo en uso por otro usuario.')


class EditProfileForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    oldpassword = PasswordField('Password Anterior')
    newpassword = PasswordField('Password Nuevo')
    newpassword2 = PasswordField('Repetir Password Nuevo', validators=[EqualTo('newpassword')])
    submit = SubmitField('Enviar')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.username.data = original_username
        self.original_email = original_email
        self.email.data = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError('Nombre de usuario no disponible.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Dirección de correo en uso por otro usuario.')

    def validate_oldpassword(self, pwd):
        if self.newpassword.data != "":
            user = User.query.filter_by(username=self.username.id).first()
            if user is None:
                raise ValidationError('Usuario desconocido. ')
            else:
                if not user.check_password(pwd.data):
                    raise ValidationError('Password anterior incorrecto.')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Restablecer Password')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Dirección de correo no encontrada.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repetir Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Solicitar Restablecer Password')


class EditOutAccForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Password')
    servidor = StringField('Servidor', validators=[DataRequired()])
    puerto = DecimalField('Puerto', validators=[DataRequired(), NumberRange()], places=0)
    ssl = BooleanField('SSL')
    submit = SubmitField('Guardar')


class EditInAccForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Password')
    servidor = StringField('Servidor', validators=[DataRequired()])
    puerto = DecimalField('Puerto', validators=[DataRequired(), NumberRange()], places=0)
    submit = SubmitField('Guardar')


class EditDBAccForm(FlaskForm):
    driver = SelectField('Base de Datos', choices=[('postgresql://', 'Postgres'),
                                                     ('mysql://', 'MySQL'),
                                                     ('oracle://', 'Oracle'),
                                                     ('sqlite:///', 'SQLite')])
    servidor = StringField('URL', validators=[DataRequired()])
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Password')
    submit = SubmitField('Guardar')
