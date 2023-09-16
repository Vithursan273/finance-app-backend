from django.shortcuts import render
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.permissions import BasePermission
from . models import *
from . serializer import *
from rest_framework.response import Response
from .validations import custom_validation, validate_email, validate_password
from rest_framework.authentication import SessionAuthentication
from django.contrib.auth import get_user_model, login, logout
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie

import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

# Create your views here.

class ExpenseView(APIView):
    
    def get(self, request):
        csrf_token = request.META.get('HTTP_X_CSRFTOKEN')
        if not csrf_token:
             return Response(csrf_token, status=status.HTTP_400_BAD_REQUEST)
        output = [{"expenseName": output.expenseName, "expenseCategory": output.expenseCategory, "expenseCost": output.expenseCost, "expenseFrequency": output.expenseFrequency}
                  for output in Expense.objects.all()]
        return Response(output)

    def post(self, request):
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(request.data)

    def delete(self, request):
        expense_name = request.data.get('expenseName', None)
        if not expense_name:
            return Response({"error": "Please provide the 'expenseName' value to delete the object."},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            # react_object = React.objects.get(employee=employee_name)
            # react_object.delete()
            react_objects = Expense.objects.filter(expenseName=expense_name)
            react_objects.delete()
            return Response({"message": "Object deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Expense.DoesNotExist:
            return Response({"error": "Object with the specified expense value does not exist."},
                            status=status.HTTP_404_NOT_FOUND)
        
class ExpensepdfView(APIView):
     
     def get(self, request):
          buf = io.BytesIO()
          c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
          textob = c.beginText()
          textob.setTextOrigin(inch, inch)
          textob.setFont("Helvetica", 14)

          output = Expense.objects.all()
          
          lines = []

          for expense in output:
               lines.append(expense.expenseName)
               lines.append(expense.expenseCategory)
               lines.append(str(expense.expenseCost))
               lines.append(expense.expenseFrequency)
               lines.append(" ")

          for line in lines:
               textob.textLine(line)

          c.drawText(textob)
          c.showPage()
          c.save()
          buf.seek(0)

          return FileResponse(buf, as_attachment=True, filename='expenses.pdf')

class TesterView(APIView):

    serializer_class = TesterSerializer

    def get(self, request):
        output = [{"name": output.name, "email": output.email}
                  for output in Tester.objects.all()]
        return Response(output)

    def post(self, request):

        serializer = TesterSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(request.data)
        
# User Authentication

class UserRegister(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
	def post(self, request):
		clean_data = custom_validation(request.data)
		serializer = UserRegisterSerializer(data=clean_data)
		if serializer.is_valid(raise_exception=True):
			user = serializer.create(clean_data)
			if user:
				return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(status=status.HTTP_400_BAD_REQUEST)

class UserLogin(APIView):
    permission_classes = (permissions.AllowAny,)
    authentication_classes = ()

    def post(self,request):
        data = request.data
        assert validate_email(data)
        assert validate_password(data)
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
                user = serializer.check_user(data)
                login(request, user)
                return Response(serializer.data, status=status.HTTP_200_OK)

class UserLogout(APIView):
	permission_classes = (permissions.AllowAny,)
	authentication_classes = ()
        
	def post(self, request):
		logout(request)
		return Response(status=status.HTTP_200_OK)

class UserView(APIView):
      permission_classes = (permissions.IsAuthenticated,)
      authentication_classes = (SessionAuthentication,)

      def get(self, request):
            serializer = UserSerializer(request.user)
            return Response({'user': serializer.data}, status=status.HTTP_200_OK)