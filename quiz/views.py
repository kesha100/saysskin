from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from openai import OpenAI
from .models import Quiz, QuizSession
from .serializers import QuizSerializer, QuizSessionSerializer
import os, json
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from django.db import transaction
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics 
from dotenv import load_dotenv
load_dotenv()


api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

class QuizListCreateAPIView(generics.ListCreateAPIView):
    queryset = Quiz.objects.prefetch_related('questions__answers').all()
    serializer_class = QuizSerializer
    pagination_class = PageNumberPagination

    def get_serializer_context(self):
        # Pass the request context to the serializer for pagination
        return {'request': self.request}


class QuizSessionViewSet(ModelViewSet):
    queryset = QuizSession.objects.only('user', 'quiz', 'completed').all()
    serializer_class = QuizSessionSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user', 'quiz', 'completed']
    # pagination_class = PageNumberPagination


    @action(detail=True, methods=['post'])
    def start_quiz(self, request, pk=None):
        quiz = get_object_or_404(Quiz, pk=pk)

        # Handle quiz start for both anonymous and authenticated users
        if request.user.is_authenticated:
            user_quiz, created = QuizSession.objects.get_or_create(
                user=request.user, quiz=quiz, defaults={'completed': False}
            )
        else:
            # For anonymous users, create a quiz with a unique session identifier
            session_id = self.get_anonymous_session_id(request)
            user_quiz, created = QuizSession.objects.get_or_create(
                session_id=session_id, quiz=quiz, defaults={'completed': False}
            )

        return Response(self.get_serializer(user_quiz).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


    @action(detail=True, methods=['post'], url_path='start-and-fetch-quiz')
    def start_and_fetch_quiz(self, request, pk=None):
        # Step 1: Retrieve the quiz by its ID (pk)
        quiz = get_object_or_404(Quiz, pk=pk)
        
        # Step 2: Start or get the quiz session
        session_id = self.get_anonymous_session_id(request)
        
        try:
            with transaction.atomic():
                if request.user.is_authenticated:
                    # For authenticated users, get or create a quiz session
                    quiz_session, created = QuizSession.objects.get_or_create(
                        user=request.user, quiz=quiz, defaults={'completed': False, 'answers_data': {}}
                    )
                else:
                    # For anonymous users, track via session_id
                    quiz_session, created = QuizSession.objects.get_or_create(
                        session_id=session_id, quiz=quiz, defaults={'completed': False, 'answers_data': {}}
                    )
                
                # Ensure the quiz_session is saved
                quiz_session.save()
        
        except Exception as e:
            raise ValidationError(f"Error creating or retrieving quiz session: {str(e)}")
        
        # Step 3: Serialize the quiz and quiz session
        quiz_data = QuizSerializer(quiz).data
        session_data = QuizSessionSerializer(quiz_session).data
        
        # Step 4: Return both quiz and session data
        response_data = {
            'quiz': quiz_data,
            'quiz_session': session_data
        }
        
        # Add debug information
        response_data['debug'] = {
            'quiz_session_id': quiz_session.id,
            'is_authenticated': request.user.is_authenticated,
            'session_id': session_id if not request.user.is_authenticated else None
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def submit_answers(self, request, pk=None):
        quiz_session = self.get_object()

        if quiz_session.completed:
            return Response({'error': 'Quiz already completed'}, status=status.HTTP_400_BAD_REQUEST)

        # Merge incoming answers into the stored answers_data
        incoming_answers = request.data.get('answers_data', {})
        quiz_session.answers_data.update(incoming_answers)
        quiz_session.save()

        return Response(self.get_serializer(quiz_session).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def complete_quiz(self, request, pk=None):
        user_quiz = self.get_object()

        # Check if the quiz is already completed
        if user_quiz.completed:
            return Response({'error': 'Quiz has already been completed.'}, status=status.HTTP_400_BAD_REQUEST)

        # Update the quiz as completed
        user_quiz.completed = True
        user_quiz.save()

        # Optionally handle anonymous users (no user profile creation)
        if not request.user.is_authenticated:
            # Handle quiz completion for anonymous users
            return Response({'status': 'Quiz completed for anonymous user.'})

        # For authenticated users, update their profile based on quiz results
        self.create_update_user_profile(user_quiz)

        return Response({'status': 'Quiz completed and user profile updated.'})

    @action(detail=True, methods=['get'])
    def recommend_products(self,quiz_session_id):
        quiz_session = QuizSession.objects.get(id=quiz_session_id)

        if not quiz_session.completed:
            return Response({'error': 'Quiz must be completed to get recommendations'}, status=status.HTTP_400_BAD_REQUEST)

        # Cache key for recommendations
        cache_key = f'recommendations_{quiz_session.id}'
        recommendations = cache.get(cache_key)

        if not recommendations:
            gpt_recommendations = self.get_recommendation_from_chatgpt(quiz_session)
            if gpt_recommendations:
                recommendations = self.process_recommendations(gpt_recommendations)
                cache.set(cache_key, recommendations, timeout=3600)  # Cache for 1 hour
            else:
                return Response({'error': 'Failed to get recommendations'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(recommendations, status=status.HTTP_200_OK)

    def get_anonymous_session_id(self, request):
        if not request.session.session_key:
            request.session.create()
        return request.session.session_key
    def get_recommendation_from_chatgpt(self, quiz_session):
        # Load product data
        current_directory = os.path.dirname(__file__)
        json_file_path = os.path.join(current_directory, 'unique_brands.json')

        with open(json_file_path) as json_file:
            products_data = json.load(json_file)

        # Check if the structure is correct
        if 'korean_brands' not in products_data:
            raise ValueError("Expected 'korean_brands' key in products_data.")

        # Extract the list of brands
        korean_brands = products_data['korean_brands']
        
        # Ensure it's a list
        if not isinstance(korean_brands, list):
            raise ValueError("Expected 'korean_brands' to be a list.")

        # Get product names
        product_names = [brand['name'] for brand in korean_brands]
        brands_list = ", ".join(product_names)

        quiz = quiz_session.quiz  

        # Use .all() to get the related questions
        questions = quiz.questions.all()  # Correctly retrieve all questions

        # Create a mapping of question ID to question text
        question_map = {question.id: question.question_text for question in questions}
    
        # Create a mapping of answer ID to answer text for each question
        answer_map = {
            question.id: {answer.id: answer.answer_text for answer in question.answers.all()}  # Use .all() for answers too
            for question in questions
        }

        # Prepare the formatted answers, ensuring to use the correct key type
        formatted_answers = []
        for q_id, a_id in quiz_session.answers_data.items():
            # Convert keys to integer if necessary
            q_id_int = int(q_id)
            a_id_int = int(a_id)

            question_text = question_map.get(q_id_int)
            answer_text = answer_map.get(q_id_int, {}).get(a_id_int)

            if question_text and answer_text:
                formatted_answers.append(f"{question_text}: {answer_text}")

        formatted_answers_string = "\n".join(formatted_answers)
        
        print("Formatted Answers:")
        print(formatted_answers)
        print(formatted_answers_string)

        system_prompt = "You are an AI that recommends beauty products based on user quiz answers ."
        prompt = f"""
        User's answers: {formatted_answers_string}. Based on this, please recommend products:
        1. Cleanser
        2. Toner
        3. Moisturizer
        4. SPF
        5. Micellar 
        Use the following brands: {brands_list}. Return in JSON format.
        'recommended_products': 
            'cleanser': 
                "brand": "Cosrx",
                'product': 'Low pH Good Morning Gel Cleanser'
                'description': 'sepcify why this product depending on what user answer'
            'toner': 
                "brand": "Cosrx",
                'product': 'toner name'
                'description': 'sepcify why this product depending on what user answer'
            so on for other products
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                temperature=0.5,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return None

    def process_recommendations(self, gpt_recommendations):
        try:
            gpt_recommendations_json = json.loads(gpt_recommendations)
            # Load additional product data and match products
            return gpt_recommendations_json  # Process as needed
        except json.JSONDecodeError:
            return None

    def merge_anonymous_to_authenticated(self, request):
        session_id = self.get_anonymous_session_id(request)
        if session_id and request.user.is_authenticated:
            # Find the anonymous session
            try:
                quiz_session = QuizSession.objects.get(session_id=session_id, user__isnull=True)
                quiz_session.user = request.user
                quiz_session.save()
                return quiz_session
            except QuizSession.DoesNotExist:
                return None