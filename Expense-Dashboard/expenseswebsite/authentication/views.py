from django.shortcuts import render, redirect
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str, DjangoUnicodeDecodeError
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.template.loader import render_to_string
from .utils import account_activation_token
from django.urls import reverse
from django.contrib import auth
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import render
from expenses.models import Expense
from django.db.models import Sum
from django.core.paginator import Paginator
from django.shortcuts import render
from userincome.models import UserIncome  
from django.db.models import Sum
from django.core.paginator import Paginator

# Create your views here.

class EmailValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        email = data['email']
        if not validate_email(email):
            return JsonResponse({'email_error': 'Email is invalid'}, status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error': 'sorry email in use,choose another one '}, status=409)
        return JsonResponse({'email_valid': True})


class UsernameValidationView(View):
    def post(self, request):
        data = json.loads(request.body)
        username = data['username']
        if not str(username).isalnum():
            return JsonResponse({'username_error': 'username should only contain alphanumeric characters'}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error': 'sorry username in use,choose another one '}, status=409)
        return JsonResponse({'username_valid': True})


class RegistrationView(View):
    def get(self, request):
        return render(request, 'authentication/register.html')

    def post(self, request):
        # Get user data from the POST request
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        # Prepare context for re-rendering the form in case of errors
        context = {
            'fieldValues': request.POST
        }

        # Validate and create the user account
        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():
                if len(password) < 6:
                    messages.error(request, 'Password too short')
                    return render(request, 'authentication/register.html', context)

                user = User.objects.create_user(username=username, email=email)
                user.set_password(password)
                user.is_active = True  # Directly activate the user
                user.save()

                messages.success(request, 'Account successfully created. You can now log in.')
                return redirect('login')  # Redirect to login page

        # Handle errors if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username is already in use')
        elif User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already in use')

        return render(request, 'authentication/register.html', context)



class VerificationView(View):
    def get(self, request, uidb64, token):
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=id)

            if not account_activation_token.check_token(user, token):
                return redirect('login'+'?message='+'User already activated')

            if user.is_active:
                return redirect('login')
            user.is_active = True
            user.save()

            messages.success(request, 'Account activated successfully')
            return redirect('login')

        except Exception as ex:
            pass

        return redirect('login')


class LoginView(View):
    def get(self, request):
        return render(request, 'authentication/login.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']

        if username and password:
            user = auth.authenticate(username=username, password=password)

            if user:
                if user.is_active:
                    auth.login(request, user)
                    messages.success(request, 'Welcome, ' +
                                     user.username+' you are now logged in')
                    return redirect('expenses')
                messages.error(
                    request, 'Account is not active,please check your email')
                return render(request, 'authentication/login.html')
            messages.error(
                request, 'Invalid credentials,try again')
            return render(request, 'authentication/login.html')

        messages.error(
            request, 'Please fill all fields')
        return render(request, 'authentication/login.html')


class LogoutView(View):
    def post(self, request):
        auth.logout(request)
        messages.success(request, 'You have been logged out')
        return redirect('login')
    

def dashboard(request):
    # Calculate total expenses
    total_expenses = Expense.objects.filter(owner=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate total income
    total_income = UserIncome.objects.filter(owner=request.user).aggregate(Sum('amount'))['amount__sum'] or 0

    # Calculate savings as the difference between total income and total expenses
    total_savings = total_income - total_expenses

    # Paginate the expenses
    page_number = request.GET.get('page', 1)
    expenses = Expense.objects.filter(owner=request.user).order_by('-date')
    paginator = Paginator(expenses, 10)
    page_obj = paginator.get_page(page_number)

    context = {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_savings': total_savings,
        'page_obj': page_obj,
        'currency': 'USD',  # Adjust according to your currency settings
    }

    return render(request, 'expenses/index.html', context)


# # View to verify username and email
# def verify_user(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email = request.POST.get('email')

#         try:
#             user = User.objects.get(username=username, email=email)
#             # Redirect to the page where they can set a new password
#             return redirect('set-newpassword', user_id=user.id)
#         except User.DoesNotExist:
#             messages.error(request, "Invalid username or email")
#             return redirect('reset-password')
#     return render(request, 'authentication/reset-password.html')

# # View to handle the password reset
# def update_password(request, user_id):
#     user = User.objects.get(id=user_id)
#     if request.method == 'POST':
#         new_password = request.POST.get('new_password')
#         user.set_password(new_password)
#         user.save()
#         messages.success(request, "Password has been updated successfully. Please log in.")
#         return redirect('login')
#     return render(request, 'authentication/set-newpassword.html', {'user_id': user.id})
