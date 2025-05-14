from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from .models import Genders, Users
from django.contrib.auth.hashers import make_password, check_password
from django.core.paginator import Paginator

def gender_list(request):
    try: 
        genders = Genders.objects.all()
        
        data = {
            'genders':genders
        }
        
        return render(request, 'gender/GenderList.html', data)
    except Exception as e:
        return HttpResponse(f'Error: {e}')
    
def add_gender(request):
    try:
        if request.method == 'POST':
            gender = request.POST.get('gender')
            
            Genders.objects.create(gender=gender).save()
            messages.success(request, 'Gender added successfully!')
            return redirect('/gender/list')
        else:
            return render(request, 'gender/AddGender.html')
    except Exception as e:
        return HttpResponse(f'Error: {e}')
    
def edit_gender(request, genderId):
    try:
        if request.method == 'POST':
            genderObj = Genders.objects.get(pk=genderId)
            
            gender = request.POST.get('gender')
            
            genderObj.gender = gender
            genderObj.save()
            
            messages.success(request,'Gender updated successfully!')
            
            data = {
                'gender':genderObj
            }
            
            return render(request, 'gender/EditGender.html', data)
        else:
            genderObj = Genders.objects.get(pk=genderId)
            
            data = {
                'gender':genderObj
            }
            
            return render(request, 'gender/EditGender.html', data)
            
    except Exception as e:
        return HttpResponse(f'Error: {e}')
    
def delete_gender(request, genderId):
    try:
        if request.method == 'POST':
            genderObj = Genders.objects.get(pk=genderId)
            genderObj.delete()
            
            messages.success(request, 'Gender deleted successfully!')
            return redirect('/gender/list')
        else:
            genderObj = Genders.objects.get(pk=genderId)
            
            data = {
                'gender': genderObj
            }
            
            return render(request, 'gender/DeleteGender.html', data)
    except Exception as e:
        return HttpResponse(f'Error: {e}')
    
def user_list(request):
    try:
        search_query = request.GET.get('search', '')
        user_list = Users.objects.select_related('gender').all()
        
        if search_query:
            user_list = user_list.filter(
                full_name__icontains=search_query
            ) | user_list.filter(
                username__icontains=search_query
            ) | user_list.filter(
                email__icontains=search_query
            )
        
        paginator = Paginator(user_list, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        data = {
            'users': page_obj,
            'page_obj': page_obj,
            'search_query': search_query
        }
        
        return render(request, 'user/UserList.html', data)
    except Exception as e:
        return HttpResponse(f'Error: {e}')
    
def add_user(request):
    try:
        if request.method == 'POST':
            fullname = request.POST.get('full_name')
            gender = request.POST.get('gender')
            birthDate = request.POST.get('birth_date')
            address = request.POST.get('address')
            contactNumber = request.POST.get('contact_number')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirmPassword = request.POST.get('confirm_password')
            
            if password != confirmPassword:
                messages.error(request, 'Password and Confirm Password do not match!')
                data = {
                    'genders': Genders.objects.all(),
                    'form_data': {
                        'full_name': fullname,
                        'gender': gender,
                        'birth_date': birthDate,
                        'address': address,
                        'contact_number': contactNumber,
                        'email': email,
                        'username': username
                    }
                }
                return render(request, 'user/AddUser.html', data)
            
            # Check if username already exists
            if Users.objects.filter(username=username).exists():
                messages.error(request, 'Username already exists. Please choose a different username.')
                data = {
                    'genders': Genders.objects.all(),
                    'form_data': {
                        'full_name': fullname,
                        'gender': gender,
                        'birth_date': birthDate,
                        'address': address,
                        'contact_number': contactNumber,
                        'email': email,
                        'username': username
                    }
                }
                return render(request, 'user/AddUser.html', data)
            
            Users.objects.create(
                full_name=fullname,
                gender=Genders.objects.get(pk=gender),
                birth_date=birthDate,
                address=address,
                contact_number=contactNumber,
                email=email,
                username=username,
                password=make_password(password)    
            ).save()
            
            messages.success(request, 'User added successfully')
            return redirect('/user/add')
        else:
            genderObj = Genders.objects.all()
            
            data = {
                'genders': genderObj
            }
            
            return render(request, 'user/AddUser.html', data)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('/user/add')

def edit_user(request, userId):
    try:
        if request.method == 'POST':
            userObj = Users.objects.get(pk=userId)
            
            fullname = request.POST.get('full_name')
            gender = request.POST.get('gender')
            birthDate = request.POST.get('birth_date')
            address = request.POST.get('address')
            contactNumber = request.POST.get('contact_number')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirmPassword = request.POST.get('confirm_password')
            
            if not gender:
                messages.error(request, 'Please select a gender')
                return redirect(f'/user/edit/{userId}')

            if Users.objects.filter(username=username).exclude(user_id=userId).exists():
                messages.error(request, 'Username already exists. Please choose a different username.')
                return redirect(f'/user/edit/{userId}')
            
            if password and confirmPassword:
                if password != confirmPassword:
                    messages.error(request, 'Password and Confirm Password do not match!')
                    return redirect(f'/user/edit/{userId}')
                userObj.password = make_password(password)
            
            try:
                genderObj = Genders.objects.get(pk=gender)
                userObj.gender = genderObj
            except Genders.DoesNotExist:
                messages.error(request, 'Invalid gender selected')
                return redirect(f'/user/edit/{userId}')
            
            userObj.full_name = fullname
            userObj.birth_date = birthDate
            userObj.address = address
            userObj.contact_number = contactNumber
            userObj.email = email
            userObj.username = username
            userObj.save()
            
            messages.success(request, 'User updated successfully!')
            return redirect('/user/list')
        else:
            userObj = Users.objects.get(pk=userId)
            genderObj = Genders.objects.all()
            
            data = {
                'user': userObj,
                'gender': genderObj
            }
            
            return render(request, 'user/EditUser.html', data)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('/user/list')
    
def delete_user(request, userId):
    try:
        if request.method == 'GET':
            user = Users.objects.get(pk=userId)
            genderObj = Genders.objects.all()
            
            data = {
                'user': user,
                'gender': genderObj
            }
            
            return render(request, 'user/DeleteUser.html', data)
        else:
            user = Users.objects.get(pk=userId)
            user.delete()
            
            messages.success(request, f'User {user.full_name} has been deleted.')
            return redirect('/user/list')
    except Users.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('/user/list')
    except Exception as e:
        return HttpResponse(f'Error: {e}')

def login(request):
    try:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            try:
                user = Users.objects.get(username=username)
                if check_password(password, user.password):
                    request.session['userId'] = user.user_id
                    request.session['username'] = user.username
                    
                    messages.success(request, f'Welcome {user.full_name}!')
                    return redirect('/user/list')
                else:
                    messages.error(request, 'Invalid username or password.')
                    return render(request, 'user/login.html')
            except Users.DoesNotExist:
                messages.error(request, 'Invalid username or password.')
                return render(request, 'user/login.html')
        else:
            return render(request, 'user/login.html')
    except Exception as e:
        messages.error(request, f'An error occured: {str(e)}')
        return render(request, 'user.login.html')

def get_user_data(request):
    if 'userId' in request.session:
        try:
            user = Users.objects.get(user_id=request.session['userId'])
            return {'current_user': user}
        except Users.DoesNotExist:
            return {'current_user': None}
    return {'current_user': None} 

def logout(request):
    request.session.flush()
    return redirect('/login/')