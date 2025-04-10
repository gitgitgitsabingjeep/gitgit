from django.shortcuts import render, redirect, get_object_or_404
from .models import Dish, Account 

# Create your views here.
global current_user
global message
message = None
current_user = None

def better_menu(request):
    global current_user
    if current_user:
        dish_objects = Dish.objects.all()
        return render(request, 'tapasapp/better_list.html', {'dishes':dish_objects, 'user':current_user})
    else:
        return redirect('login')

def add_menu(request):
    global current_user
    if current_user:
        if(request.method=="POST"):
            dishname = request.POST.get('dname')
            cooktime = request.POST.get('ctime')
            preptime = request.POST.get('ptime')
            Dish.objects.create(name=dishname, cook_time=cooktime, prep_time=preptime)
            return redirect('better_menu')
        else:
            return render(request, 'tapasapp/add_menu.html', {'user':current_user})
    else:
        return redirect('login')

def view_detail(request, pk):
    global current_user
    if current_user:
        d = get_object_or_404(Dish, pk=pk)
        return render(request, 'tapasapp/view_detail.html', {'d': d, 'user':current_user})
    else:
        return redirect('login')

def delete_dish(request, pk):
    Dish.objects.filter(pk=pk).delete()
    return redirect('better_menu')

def update_dish(request, pk):
    global current_user
    if current_user:
        if(request.method=="POST"):
            cooktime = request.POST.get('ctime')
            preptime = request.POST.get('ptime')
            Dish.objects.filter(pk=pk).update(cook_time=cooktime, prep_time=preptime)
            return redirect('view_detail', pk=pk)
        else:
            d = get_object_or_404(Dish, pk=pk)
            return render(request, 'tapasapp/update_menu.html', {'d':d, 'user':current_user})
    else:
        return redirect('login')

def basic_list(request, pk):
    global current_user
    if current_user:
        if(request.method=="POST"):
            button = request.POST.get("button")

            if button == "logout":
                current_user = None
                return redirect('login')

        else:
            dish_objects = Dish.objects.all()
            return render(request, 'tapasapp/basic_list.html', {'dishes':dish_objects, 'user':current_user})
    else:
        return redirect('login')

def manage_account(request, pk):
    global current_user
    if current_user:
        if(request.method=="POST"):
            button = request.POST.get("button")

            if button == "delete_account":
                return redirect('delete_account', pk=pk)
        
        else:
            user = get_object_or_404(Account, pk=pk)
            message = request.session.pop('message', None)
            return render(request, 'tapasapp/manage_account.html', {'user':user, 'message':message})
    else:
        return redirect('login')
    
def change_password(request, pk):
    global current_user
    if current_user:
        if(request.method=="POST"):
            button = request.POST.get("button")

            if button == "confirm":
                old_password = request.POST.get('old_password')
                new_password = request.POST.get('new_password')
                new_password2 = request.POST.get('new_password2')

                if new_password == new_password2:
                    if old_password == get_object_or_404(Account, pk=pk).getPassword():
                        Account.objects.filter(pk=pk).update(password=new_password)
                        request.session['message'] = 'Password changed successfully.'
                        return redirect('manage_account', pk=pk)
                    
                    else:
                        message = "Input correct old password. Try again."
                        return render(request, 'tapasapp/change_password.html', {'message':message, 'user':current_user})
                
                else:
                    message = "Unmatching passwords. Try again."
                    return render(request, 'tapasapp/change_password.html', {'message':message, 'user':current_user})
            
            elif button == "cancel":
                return redirect('manage_account', pk=pk)
        
        else:
            return render(request, 'tapasapp/change_password.html', {'user':current_user})
    else:
        return redirect('login')

def delete_account(request, pk):
    Account.objects.filter(pk=pk).delete()
    request.session['message'] = 'Account deleted.'
    return redirect('login')

def login(request):
    if(request.method=="POST"):
        button = request.POST.get("button")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if button == "login":
            valid_account = Account.objects.filter(username=username).exists()
            if valid_account:
                credentials = Account.objects.get(username=username)
                if password == credentials.getPassword():
                    global current_user
                    current_user = credentials
                    return redirect('basic_list', pk=current_user.pk)
                else:
                    return render(request, 'tapasapp/login.html', {'message': 'Incorrect password.'})
            else:
                return render(request, 'tapasapp/login.html', {'message': 'Account does not exist.'})
        
        elif button == "signup":
            return redirect('signup')
        
    else:
        message = request.session.pop('message', None)
        fusername = request.session.pop('fresh_username', None)
        return render(request, 'tapasapp/login.html', {'message':message, 'fusername':fusername})
        

def signup(request):
    if(request.method=="POST"):
        button = request.POST.get("button")
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        if button == "signup":
            username_exists = Account.objects.filter(username=username).exists()

            if not username_exists:
                Account.objects.create(username=username, password=password)
                request.session['message'] = 'Account created successfully.'
                request.session['fresh_username'] = username
                return redirect('login')
            else:
                return render(request, 'tapasapp/signup.html', {'message':'Username is already taken.'})
        
    else:
        return render(request, 'tapasapp/signup.html')