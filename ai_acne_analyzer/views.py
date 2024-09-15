from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .acne_model import analyze_acne  # Import your acne analyzer model

class AcneAnalysisView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # To handle image uploads

    def post(self, request, *args, **kwargs):
        image = request.FILES.get('image')  # Get the image from the request
        
        # Pass the image to the acne analyzer model
        analysis_result = analyze_acne(image)

        return Response(analysis_result)
