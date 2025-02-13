from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, LoginSerializer, UserSerializer, UserProfileSerializer
from .models import UserProfile, CustomUser
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404

# from django.conf import settings
 
# CustomUser = settings.AUTH_USER_MODEL
# Login User
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

# Register User
class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer, UserSerializer
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import CustomUser 
from quiz.models import QuizSession
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user)

            # Check if the user had any anonymous quizzes associated with the session ID
            session_id = request.session.session_key
            if not session_id:
                request.session.create()  # Create a new session if none exists
                session_id = request.session.session_key

            # Find any anonymous quizzes associated with the session ID
            anonymous_quizzes = QuizSession.objects.filter(session_id=session_id, user__isnull=True)

            # If there are quizzes linked to the anonymous session, assign them to the authenticated user
            if anonymous_quizzes.exists():
                anonymous_quizzes.update(user=user)  # Clear the session ID after linking to the user

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': user_serializer.data,
                'message': f'{anonymous_quizzes.count()} quizzes have been successfully merged to your account'
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Profile View
class ProfileView(APIView):
    # permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        if str(request.user.id) != user_id and not request.user.is_staff:
            return Response({"detail": "You do not have Profile, because you havent't authorized yet"}, status=status.HTTP_403_FORBIDDEN)
        user_profile = get_object_or_404(UserProfile, user_id=user_id)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data)

    def put(self, request, user_id):

        if str(request.user.id) != user_id:
            return Response({"detail": "You do not have permission to update this profile."},
                            status=status.HTTP_403_FORBIDDEN)
        
        user_profile = get_object_or_404(UserProfile, user_id=user_id)  
        serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


