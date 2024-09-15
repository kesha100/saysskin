from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
import os, re
import openai
from openai import OpenAI
from products.models import Tag, SkinType, Concern
from products.serializers import ProductSerializer
from .models import Quiz, UserQuiz, Question, Answer, UserAnswer
from user.models import UserProfile
from .serializers import QuizSerializer, UserQuizSerializer, UserAnswerSerializer, QuestionSerializer
from django.db.models import Count
from .permissions import IsAdminUserOrReadOnly
from dotenv import load_dotenv
import logging
# from .sephora_scraper import fetch_products_from_makeup_api
# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
from .unique_brands import brands
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
import json

class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAdminUserOrReadOnly]


class UserQuizViewSet(ModelViewSet):
    queryset = UserQuiz.objects.all()
    serializer_class = UserQuizSerializer

    @action(detail=True, methods=['post'])
    def start_quiz(self, request, pk=None):
        quiz = get_object_or_404(Quiz, pk=pk)

        # Handle quiz start for both anonymous and authenticated users
        if request.user.is_authenticated:
            user_quiz, created = UserQuiz.objects.get_or_create(
                user=request.user, quiz=quiz, defaults={'completed': False}
            )
        else:
            # For anonymous users, create a quiz with a unique session identifier
            session_id = self.get_anonymous_session_id(request)
            user_quiz, created = UserQuiz.objects.get_or_create(
                session_id=session_id, quiz=quiz, defaults={'completed': False}
            )

        return Response(self.get_serializer(user_quiz).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def get_anonymous_session_id(self, request):
        # Get or generate a session ID for anonymous users
        if not request.session.session_key:
            request.session.create()  # Generate session ID if it doesn't exist
        return request.session.session_key
    
    

    @action(detail=True, methods=['get'])
    def recommend_products(self, request, pk=None):
        user_quiz = self.get_object()

        # Ensure the quiz is completed before proceeding
        if not user_quiz.completed:
            return Response({'error': 'Quiz must be completed to get recommendations'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch recommendations from ChatGPT
        gpt_recommendations = self.get_recommendation_from_chatgpt(user_quiz)

        if gpt_recommendations:
            # Load product data
            current_directory = os.path.dirname(__file__)
            json_file_path = os.path.join(current_directory, 'aruuke.json')
            with open(json_file_path, 'r', encoding='utf-8') as json_file:
                products_data = json.load(json_file)

            # Parse GPT recommendations string into JSON
            try:
                gpt_recommendations_json = json.loads(gpt_recommendations)  # Convert string to JSON
                logger.debug(f"GPT Recommendations JSON: {gpt_recommendations_json}")

                # Match products
                matched_products = self.match_products(gpt_recommendations_json, products_data)

                # Filter out SPF products
                filtered_products = [product for product in matched_products if "sun cream" not in product['name'].lower()]

                # Separate morning and night routines
                morning_routine = matched_products  # First 4 products for morning routine

                # Assuming makeup remover is a predefined product
                makeup_remover = {
                    "name": "BIODERMA SENSIBIO H2O МИЦЕЛЛЯРНАЯ ВОДА",
                    "price": "720.00 сом",
                    "link": "https://distore.one/product/bioderma-sensibio-h2o/",
                    "image": "https://distore.one/wp-content/uploads/2023/10/5f74b38b52d411edbab0000c291e907c_81607722663d11edbab4000c291e907c.jpg",
                }

                # Night routine starts with makeup remover followed by the remaining morning products
                night_routine = [makeup_remover] + filtered_products

                return Response({
                    'morning_routine': morning_routine,
                    'night_routine': night_routine,
                    
                }, status=status.HTTP_200_OK)

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse GPT recommendations as JSON: {e}")
                return Response({'error': 'Failed to parse recommendations'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'Failed to get recommendations'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
    def get_recommendation_from_chatgpt(self, user_quiz):
        current_directory = os.path.dirname(__file__)
        json_file_path = os.path.join(current_directory, 'product_titles.json') 
        with open(json_file_path) as json_file:
            products_data = json.load(json_file)

        # Convert the product list into a readable format
        product_names = [product for product in products_data]  # Adjust based on the structure of your JSON
        brands_list = ", ".join(product_names)
        user_answers = UserAnswer.objects.filter(user_quiz=user_quiz)
    
        # Collect question and selected answer data
        answer_data = []
        for answer in user_answers:
            question_text = answer.question.question_text  # Assuming Question model has a 'text' field
            selected_answer_text = answer.selected_answer.answer_text # Assuming Answer model has a 'text' field
            answer_data.append(f"Question: {question_text}, Answer: {selected_answer_text}")
        
        # Join all answers into a single string for the prompt
        formatted_answers = "\n".join(answer_data)

        system_prompt = "You are an AI that recommends beauty products based on user preferences/answers for the quiz."
        "The user has provided their preferences. Based on these, recommend  products for they're daily use,"
        "including descriptions, why they suit the user's needs, and the type of product it is."
    
        prompt = f"""
        User's answers {formatted_answers} depending on them please provide the best skincare 4products:
        1. cleanser
        2. toner
        3. cream
        4. spf
        Choose products only from the following list of brands randomly, not only first:
        {brands_list}
        In JSON Format
        
        {{
            "recommended_products": [
                {{
                "name": "Product Name",
                "description": "Product Description"
                }}
            ]
            }}
        """

        try:
            # Make API call to ChatGPT
            response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        response_format= { "type": "json_object" },
                        temperature= 0.5,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": prompt}
                        ],

            
                    )
            logger.debug("OpenAI API call successful")
            
            # Parse response from ChatGPT
            recommendation_text = response.choices[0].message.content.strip()
            return recommendation_text
        
        except Exception as e:
            logger.error(f"Error from OpenAI API: {e}")

    def normalize_string(self, s):
        return re.sub(r'\s+', ' ', s.strip()).lower()

    def match_products(self, gpt_recommendations, products_data):
        try:
            # Get the recommended products from the GPT response
            recommended_products = gpt_recommendations.get("recommended_products") or gpt_recommendations.get("products")
            recommended_names = [self.normalize_string(product['name']) for product in recommended_products]
            
            matched_products = []
            for product in products_data:
                normalized_title = self.normalize_string(product["title"])
                # Check for exact or partial matches
                if any(recommended_name in normalized_title for recommended_name in recommended_names):
                    matched_products.append({
                        "name": product['title'],
                        "price": product['price'],
                        "link": product['link'],
                        "image": product['images'][0] if 'images' in product and product['images'] else None,
                    })

            # Debug: Print the list of matched products (if any)
            if matched_products:
                print(f"Matched products: {matched_products}")
            else:
                print("No matching products found.")

            return matched_products

        except KeyError as e:
            print(f"Key error: {e}")
            return []
    @action(detail=True, methods=['post'])
    def complete_quiz(self, request, pk=None):
        user_quiz = self.get_object()

        # Update the quiz as completed
        user_quiz.completed = True
        user_quiz.save()

        # Optionally handle anonymous users (no user profile creation)
        if not request.user.is_authenticated:
            return Response({'status': 'Quiz completed for anonymous user.'})

        # For authenticated users, update their profile
        self.create_update_user_profile(user_quiz)
        return Response({'status': 'Quiz completed and user profile updated.'})


    def create_update_user_profile(self, user_quiz):
        # Initialize or get existing profile
        profile, _ = UserProfile.objects.get_or_create(user=user_quiz.user)

        # Example: Categorize answers into skin types, concerns, etc.
        # Collect tags from answers
        answer_tags = Tag.objects.filter(answers__questions__userquiz=user_quiz).annotate(count=Count('id'))

        # Logic to decide on skin types, concerns based on tags
        # This part of the implementation depends heavily on how tags are structured and how they map to skin types and concerns
        # Let's assume tags directly relate to skin types and concerns

        skin_types = SkinType.objects.filter(tag__in=answer_tags)
        concerns = Concern.objects.filter(tag__in=answer_tags)

        # Update profile
        profile.skin_types.set(skin_types)
        profile.concerns.set(concerns)
        profile.save()



class UserAnswerViewSet(ModelViewSet):
    queryset = UserAnswer.objects.all()
    serializer_class = UserAnswerSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        user_quiz = self.get_user_quiz(request, data['quiz_id'])
        question = get_object_or_404(Question, id=data['question_id'])
        answer = get_object_or_404(Answer, id=data['answer_id'])

        user_answer, created = UserAnswer.objects.update_or_create(
            user_quiz=user_quiz, question=question,
            defaults={'selected_answer': answer}
        )

        return Response(self.get_serializer(user_answer).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    def get_anonymous_session_id(self, request):
        # Get or generate a session ID for anonymous users
        if not request.session.session_key:
            request.session.create()  # Generate session ID if it doesn't exist
        return request.session.session_key
    
    def get_user_quiz(self, request, quiz_id):
        quiz = get_object_or_404(Quiz, id=quiz_id)

        # Check if the user is authenticated
        if request.user.is_authenticated:
            user_quiz, created = UserQuiz.objects.get_or_create(
                user=request.user, quiz=quiz, defaults={'completed': False}
            )
        else:
            # Handle for anonymous users
            session_id = self.get_anonymous_session_id(request)
            user_quiz, created = UserQuiz.objects.get_or_create(
                session_id=session_id, quiz=quiz, defaults={'completed': False}
            )

        return user_quiz