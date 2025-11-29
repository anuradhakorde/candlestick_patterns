#!/usr/bin/env python
"""
Script to populate user data with full details
"""
import os
import django
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'candlestickpattern.settings')
django.setup()

from django.contrib.auth import get_user_model

def populate_user_data():
    User = get_user_model()
    
    # Update existing admin user
    try:
        admin_user = User.objects.get(username='admin')
        admin_user.first_name = 'Admin'
        admin_user.last_name = 'User'
        admin_user.email = 'admin@candlestickpattern.com'
        admin_user.phone_number = '+1-555-0001'
        admin_user.date_of_birth = date(1990, 1, 1)
        admin_user.save()
        print(f"✅ Updated admin user: {admin_user.get_full_name()}")
    except User.DoesNotExist:
        print("❌ Admin user not found")
    
    # Update existing vik user
    try:
        vik_user = User.objects.get(username='vik')
        vik_user.first_name = 'Vikram'
        vik_user.last_name = 'Developer'
        vik_user.email = 'vik@candlestickpattern.com'
        vik_user.phone_number = '+1-555-0002'
        vik_user.date_of_birth = date(1985, 5, 15)
        vik_user.save()
        print(f"✅ Updated vik user: {vik_user.get_full_name()}")
    except User.DoesNotExist:
        print("❌ Vik user not found")
    
    # Create sample regular users
    sample_users = [
        {
            'username': 'trader1',
            'first_name': 'John',
            'last_name': 'Trader',
            'email': 'john.trader@email.com',
            'phone_number': '+1-555-1001',
            'date_of_birth': date(1988, 3, 22),
            'password': 'trader123'
        },
        {
            'username': 'analyst1',
            'first_name': 'Sarah',
            'last_name': 'Analyst',
            'email': 'sarah.analyst@email.com',
            'phone_number': '+1-555-1002',
            'date_of_birth': date(1992, 7, 10),
            'password': 'analyst123'
        },
        {
            'username': 'investor1',
            'first_name': 'Michael',
            'last_name': 'Investor',
            'email': 'michael.investor@email.com',
            'phone_number': '+1-555-1003',
            'date_of_birth': date(1985, 12, 5),
            'password': 'investor123'
        }
    ]
    
    for user_data in sample_users:
        username = user_data['username']
        if User.objects.filter(username=username).exists():
            print(f"⚠️  User {username} already exists, skipping...")
            continue
            
        password = user_data.pop('password')
        user = User.objects.create_user(
            username=username,
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            password=password
        )
        user.phone_number = user_data['phone_number']
        user.date_of_birth = user_data['date_of_birth']
        user.save()
        print(f"✅ Created user: {user.get_full_name()} ({username})")
    
    # Display all users
    print("\n📋 All users in database:")
    print("-" * 80)
    for user in User.objects.all():
        print(f"👤 {user.username:12} | {user.get_full_name():20} | {user.email:25} | Staff: {user.is_staff} | Super: {user.is_superuser}")
        if user.phone_number:
            print(f"   📞 {user.phone_number}")
        if user.date_of_birth:
            print(f"   🎂 {user.date_of_birth}")
        print()

if __name__ == '__main__':
    populate_user_data()