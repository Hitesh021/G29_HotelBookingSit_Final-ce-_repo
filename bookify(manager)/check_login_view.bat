@echo off
echo Examining login view code...
cd mainProject
python -c "
import inspect
from loginApp.views import login_view

print('=== Login View Code ===')
print(inspect.getsource(login_view))

print('\n=== Key parts to check ===')
print('1. How is the role being compared? (case-sensitive or not)')
print('2. How is the user profile being retrieved?')
print('3. Are there any additional validation checks?')

print('\n=== Instructions ===')
print('Look for lines like:')
print('- if actual_role != selected_role:')
print('- profile, created = UserProfile.objects.get_or_create(user=user)')
print('- if selected_role == \"admin\" and not user.is_superuser:')
"
echo.
echo Login view examination completed.
pause 