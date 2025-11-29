from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

User = get_user_model()


def home(request):
    """
    Homepage view for CandlestickPattern project.
    """
    context = {
        'title': 'CandlestickPattern - Stock Analysis Tool',
        'description': 'Analyze stock market data and detect candlestick patterns'
    }
    return render(request, 'myapp/home.html', context)


@login_required
def profile(request):
    """
    User profile view.
    """
    return render(request, 'myapp/profile.html', {'user': request.user})


# Helper function to check if user is staff or superuser
def is_staff_or_superuser(user):
    return user.is_staff or user.is_superuser


@login_required
@user_passes_test(is_staff_or_superuser)
def user_list(request):
    """
    List all users with pagination and search functionality.
    """
    search_query = request.GET.get('search', '')
    users = User.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    users = users.order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(users, 10)  # 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_users': User.objects.count()
    }
    return render(request, 'myapp/user_list.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def user_detail(request, user_id):
    """
    View detailed information about a specific user.
    """
    user = get_object_or_404(User, id=user_id)
    context = {
        'user_detail': user
    }
    return render(request, 'myapp/user_detail.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def user_create(request):
    """
    Create a new user.
    """
    if request.method == 'POST':
        from .forms import UserCreateForm
        form = UserCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" has been created successfully.')
            return redirect('myapp:user_detail', user_id=user.id)
    else:
        from .forms import UserCreateForm
        form = UserCreateForm()
    
    context = {
        'form': form,
        'title': 'Create New User'
    }
    return render(request, 'myapp/user_form.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def user_edit(request, user_id):
    """
    Edit an existing user.
    """
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        from .forms import UserEditForm
        form = UserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" has been updated successfully.')
            return redirect('myapp:user_detail', user_id=user.id)
    else:
        from .forms import UserEditForm
        form = UserEditForm(instance=user)
    
    context = {
        'form': form,
        'user_detail': user,
        'title': f'Edit User: {user.username}'
    }
    return render(request, 'myapp/user_form.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def user_delete(request, user_id):
    """
    Delete a user with confirmation.
    """
    user = get_object_or_404(User, id=user_id)
    
    # Prevent deletion of current user
    if user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('myapp:user_detail', user_id=user.id)
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User "{username}" has been deleted successfully.')
        return redirect('myapp:user_list')
    
    context = {
        'user_detail': user
    }
    return render(request, 'myapp/user_delete.html', context)
