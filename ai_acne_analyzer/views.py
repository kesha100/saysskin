# import os
# from django.shortcuts import get_object_or_404
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from transformers import pipeline
# from .models import Image
# from .serializers import ImageSerializer
# from supabase import create_client, Client
# from io import BytesIO
# import torch
# import logging

# # Supabase configuration
# SUPABASE_URL = os.getenv('SUPABASE_URL')
# SUPABASE_KEY = os.getenv('SUPABASE_KEY')
# SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET')

# # Initialize Supabase client
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# # Set up logging
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# handler = logging.StreamHandler()
# handler.setLevel(logging.DEBUG)
# formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# handler.setFormatter(formatter)
# logger.addHandler(handler)

# class ImageUploadView(APIView):
#     def post(self, request, *args, **kwargs):
#         logger.debug("Received image upload request")
#         image_serializer = ImageSerializer(data=request.data)
#         if image_serializer.is_valid():
#             try:
#                 image_instance = image_serializer.save()
#                 logger.debug(f"Image instance saved with ID: {image_instance.id}")
#             except Exception as e:
#                 logger.error(f"Error saving image instance: {e}")
#                 return Response({"error": "Error saving image instance"}, status=500)

#             try:
#                 file = image_instance.image
#                 file_data = file.read()
#                 file_extension = file.name.split('.')[-1]
#                 file_name = f"{image_instance.id}.{file_extension}"

#                 # Upload the image to Supabase Storage
#                 file.seek(0)  # Reset file pointer to the beginning
#                 result = supabase.storage().from_(SUPABASE_BUCKET).upload(file_name, file_data)
#                 if 'error' in result:
#                     logger.error(f"Error uploading to Supabase: {result['error']}")
#                     return Response({"error": "Error uploading to Supabase"}, status=500)

#                 # Get public URL from Supabase Storage
#                 public_url = supabase.storage().from_(SUPABASE_BUCKET).get_public_url(file_name)
#                 logger.debug(f"Image uploaded to Supabase: {public_url['publicURL']}")
#                 image_instance.aws_url = public_url['publicURL']

#                 # Use Hugging Face API directly with the Supabase URL
#                 device = 0 if torch.cuda.is_available() else -1
#                 acne_pipe = pipeline("image-classification", model="imfarzanansari/skintelligent-acne", device=device)
#                 wrinkle_pipe = pipeline("image-classification", model="imfarzanansari/skintelligent-wrinkles", device=device)

#                 # Perform the analysis
#                 acne_results = acne_pipe(public_url['publicURL'])
#                 wrinkle_results = wrinkle_pipe(public_url['publicURL'])

#                 # Save analysis results in the database
#                 image_instance.analysis_results = {
#                     "acne": acne_results,
#                     "wrinkles": wrinkle_results
#                 }
#                 image_instance.save()

#                 return Response({
#                     'id': image_instance.id,
#                     'aws_url': image_instance.aws_url,
#                     'analysis_results': image_instance.analysis_results
#                 }, status=status.HTTP_201_CREATED)

#             except Exception as e:
#                 logger.error(f"Error processing image upload: {e}")
#                 image_instance.delete()
#                 return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             logger.error(f"Image serializer errors: {image_serializer.errors}")
#             return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class ImageDetailView(APIView):
#     def get(self, request, pk, *args, **kwargs):
#         image_instance = get_object_or_404(Image, pk=pk)
#         serializer = ImageSerializer(image_instance)
#         return Response(serializer.data)
