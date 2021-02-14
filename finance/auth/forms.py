from django import forms

class RegistrationForm(forms.Form):
    NORMAL = 'N'
    BROKER = 'B'
    ADMIN = 'A'

    USER_TYPE = (
        (NORMAL, 'Normal'),
        (BROKER, 'Broker'),
        (ADMIN, 'Admin'),
    )
    username = forms.CharField(label='Username', max_length=30, required=True,
                               widget=forms.TextInput(attrs={'class': 'input100',
                                                            'type': 'text',
                                                            'name': 'username',
                                                            'placeholder': 'Username'}))
    p1 = forms.CharField(label='Password', max_length=30, required=True,
                        widget=forms.PasswordInput(attrs={'class': 'input100',
                                                          'type': 'password',
                                                          'name': 'p1',
                                                          'placeholder': 'Password'}))
    p2 = forms.CharField(label='Password', max_length=30, required=True,
                        widget=forms.PasswordInput(attrs={'class': 'input100',
                                                          'type': 'password',
                                                          'name': 'p2',
                                                          'placeholder': 'Confirm Password'}))
    email = forms.EmailField(label='Email', max_length=30, required=True,
                             widget=forms.TextInput(attrs={'class': 'input100',
                                                            'type': 'text',
                                                            'name': 'email',
                                                            'placeholder': 'Email'}))
    first_name = forms.CharField(label='First Name', max_length=30, required=True,
                                 widget=forms.TextInput(attrs={'class': 'input100',
                                                            'type': 'text',
                                                            'name': 'first_name',
                                                            'placeholder': 'First Name'}))
    last_name = forms.CharField(label='Last Name', max_length=30, required=True,
                                widget=forms.TextInput(attrs={'class': 'input100',
                                                            'type': 'text',
                                                            'name': 'last_name',
                                                            'placeholder': 'Last Name'}))
    CHOICES = (('N', 'Normal User'),
               ('B', 'Broker'))

    user_type = forms.ChoiceField(choices=CHOICES, widget=forms.Select(attrs={'class': 'input100',
                                                                              'type': 'select',
                                                                              'name': 'user_type',
                                                                              'placeholder': 'User Type'}))


class SigninForm(forms.Form):
    username = forms.CharField(label='Username', max_length=30, required=True,
                               widget=forms.TextInput(attrs={'class': 'input100',
                                                            'type': 'text',
                                                            'name': 'username',
                                                            'placeholder': 'Username'}))
    p = forms.CharField(label='Password', max_length=30, required=True,
                        widget=forms.PasswordInput(attrs={'class': 'input100',
                                                          'type': 'password',
                                                          'name': 'pass',
                                                          'placeholder': 'Password'}))
