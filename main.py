from PyPDF2 import PdfReader
from django.shortcuts import render, HttpResponse,HttpResponseRedirect,redirect
from .models import FilesUpload,Signup
import google.generativeai as genai
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from PIL import Image
from django.contrib.auth import get_user_model
from django.contrib import messages
import json

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as file:
        reader = PdfReader(file)
        num_pages = len(reader.pages)
        for page_num in range(num_pages):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

def generate_questions(text):
    genai.configure(api_key="AIzaSyBGr8QJ-5E_IY2DlhKL668swEVq_PCGs80")

    # Set up the model
    generation_config = {
      "temperature": 0.9,
      "top_p": 1,
      "top_k": 1,
      "max_output_tokens": 2048,
    }

    safety_settings = [
      {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      },
      {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      },
      {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      },
      {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
      },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    # Start conversation with a history of user input
    convo = model.start_chat(history=[{"role": "user", "parts": [text]}, {"role": "model", "parts": [""]}])

    # Generate questions
    convo.send_message("Generate all important questions from given text: " + text)
    return convo.last.text

# def generate_questions(text):
#     genai.configure(api_key="AIzaSyBGr8QJ-5E_IY2DlhKL668swEVq_PCGs80")
#
#     # Set up the model
#     generation_config = {
#         "temperature": 0.9,
#         "top_p": 1,
#         "top_k": 1,
#         "max_output_tokens": 2048,
#     }
#
#     safety_settings = [
#         {
#             "category": "HARM_CATEGORY_HARASSMENT",
#             "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#         },
#         {
#             "category": "HARM_CATEGORY_HATE_SPEECH",
#             "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#         },
#         {
#             "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
#             "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#         },
#         {
#             "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
#             "threshold": "BLOCK_MEDIUM_AND_ABOVE"
#         },
#     ]
#
#     model = genai.GenerativeModel(model_name="gemini-1.0-pro",
#                                   generation_config=generation_config,
#                                   safety_settings=safety_settings)
#
#     # Start conversation with a history of user input
#     convo = model.start_chat(history=[
#         {"role": "user", "parts": [text]},
#         {"role": "model", "parts": [""]},
#     ])
#
#     # Generate questions
#     convo.send_message("Generate questions from given text: " + text)
#     return convo.last.text

def categorize_questions(generated_questions):
    short_questions = []
    long_questions = []
    very_long_questions = []

    for question in generated_questions:
        length = len(question.split())
        if length <= 5:
            short_questions.append(question)
        elif length <= 10:
            long_questions.append(question)
        else:
            very_long_questions.append(question)

    return short_questions, long_questions, very_long_questions

def reply(user_message):
    import google.generativeai as genai

    genai.configure(api_key="AIzaSyBGr8QJ-5E_IY2DlhKL668swEVq_PCGs80")

    # Set up the model
    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.0-pro",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    convo = model.start_chat(history=[
        {
            "role": "user",
            "parts": [user_message]
        },
        {
            "role": "model",
            "parts": [""]
        },
    ])

    convo.send_message(user_message)

    return convo.last.text

# def uploadpdf(request):
#     if request.method == "POST":
#         if 'file' in request.FILES:
#
#             # File upload part
#             file = request.FILES["file"]
#             if file.name.endswith('.img'):
#                 image = file
#                 question = request.POST.get('question', '')
#                 response = image_recognition(question, image)
#                 return HttpResponse(response)
#             document = FilesUpload.objects.create(file=file)
#             document.save()
#             file_path = document.file.path
#             # Check if the file is an image
#
#             extracted_text = extract_text_from_pdf(file_path)
#             generated_questions = generate_questions(extracted_text)
#             short_questions, long_questions, very_long_questions = categorize_questions(generated_questions.split('\n'))
#             response = "\n\nShort Questions:" + "\n".join(short_questions) + \
#                         "\n\nLong Questions:<br>" + "\n".join(long_questions) + \
#                         "\n\nVery Long Questions:<br>" + "\n".join(very_long_questions)
#             response = "\n\nImportant Questions:\n" + "\n".join(short_questions + long_questions + very_long_questions)
#             definition_short = "Define: "
#
#             # Create a numbered list of all questions
#             # Create a list of all questions with proper numbering and formatting
#             all_questions = short_questions + long_questions + very_long_questions
#             formatted_questions = [f"**{i + 1}.** {question}" for i, question in enumerate(all_questions)]
#             #
#             response = "\n\nImportant Questions:<br>" + "<br>".join(formatted_questions)
#             # Escape asterisks in each question
#             all_questions = [(question.replace('**', '-') + "\n") for question in
#                              short_questions + long_questions + very_long_questions]
#
#             # Join all questions together with appropriate formatting
#             response = "\n\nImportant Questions:" + "\n".join(all_questions)
#
#             return HttpResponse(response)
#         elif 'message' in request.POST:
#             # Text message part
#             user_message = request.POST.get('message', '')
#             generated_questions = reply(user_message)
#             # short_questions, long_questions, very_long_questions = categorize_questions(generated_questions.split('\n'))
#             # response = "<br><br>Short Questions:<br>" + "<br>".join(short_questions) + \
#             #            "<br><br>Long Questions:<br>" + "<br>".join(long_questions) + \
#             #            "<br><br>Very Long Questions:<br>" + "<br>".join(very_long_questions)
#             return HttpResponse(generated_questions)
#         elif 'image' in request.POST:
#             image = request.FILES["image"]
#             question = request.POST.get('question', '')
#             response = image_recognition(question, image)
#             return HttpResponse(response)
#     return render(request, 'testapp/uploadpdf.html', {})

def uploadpdf(request):
    if request.method == "POST":
        if 'file' in request.FILES:
            file = request.FILES["file"]
            file_name = file.name
            file_extension = file_name.split('.')[-1].lower()

            if file_extension == 'pdf':
                document = FilesUpload.objects.create(file=file)
                document.save()
                file_path = document.file.path

                extracted_text = extract_text_from_pdf(file_path)
                if "Error" in extracted_text:
                    return HttpResponse(extracted_text)

                generated_questions = generate_questions(extracted_text)
                short_questions, long_questions, very_long_questions = categorize_questions(
                    generated_questions.split('\n'))
                formatted_questions = [f"**{i + 1}.** {question}" for i, question in
                                       enumerate(short_questions + long_questions + very_long_questions)]
                response = "\n\nImportant Questions:<br>" + "<br>".join(formatted_questions)

                return HttpResponse(response)


            elif file_extension in ['jpg', 'jpeg', 'png', 'bmp', 'gif']:

                question = request.POST.get('question', '')

                image = Image.open(file)

                response = image_recognition(question, image)

                return HttpResponse(response)

            else:
                return HttpResponse("Error: Unsupported file type.")

        elif 'message' in request.POST:
            user_message = request.POST.get('message', '')
            generated_questions = reply(user_message)
            return HttpResponse(generated_questions)

    return render(request, 'testapp/uploadpdf.html', {})


# def signup(request):
#     if request.method == 'POST':  # Change to POST method
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         obj=Signup.concrete_model(email,password)
#         obj.save()
#     return render(request, 'testapp/signin.html')

def signup(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)
        user = User.objects.create_user(username=name, email=email, password=password)
        user.save()

        # Sending welcome email
        subject = 'Welcome to Your Personal Chatbot'
        html_message = render_to_string('testapp/welcome_email.html', {'name': name})
        plain_message = strip_tags(html_message)
        from_email = 'personalchatbot911@gmail.com'  # Update with your email
        to_email = [email]
        send_mail(subject, plain_message, from_email, to_email, html_message=html_message,fail_silently=False)

        return HttpResponseRedirect('http://127.0.0.1:8000/signin/')
    return render(request, 'testapp/signin.html')

# def signin(request):
#     if request.method=='POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             # Authentication successful
#             user = form.get_user()
#             return HttpResponseRedirect('http://127.0.0.1:8000/uploadpdf')
#             # Assuming you have a URL pattern named 'home'
#
#         # If the request method is not POST or authentication fails, render the login form
#     form = AuthenticationForm()
#     return render(request, 'testapp/login.html', {'form': form})

def signin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Authentication successful
            user = form.get_user()
            username = user.username
            # Redirect to the desired URL after successful login
            redirect_url = reverse('uploadpdf') + f'?username={username}'
            return HttpResponseRedirect(redirect_url)
        else:
            print(form.errors)  # Print form errors for debugging

    # Extract the username from the URL query parameters
    username = request.GET.get('username', '')

    # If the request method is not POST or authentication fails, render the login form
    form = AuthenticationForm()
    return render(request, 'testapp/login.html', {'form': form, 'username': username})

    # If the request method is not POST or authentication fails, render the login form

def image_recognition(question,image):
    import google.generativeai as genai

    genai.configure(api_key="AIzaSyBGr8QJ-5E_IY2DlhKL668swEVq_PCGs80")
    model = genai.GenerativeModel(model_name="gemini-pro-vision")
    if question != "" and image is not None:
        response = model.generate_content([question, image])
    elif image is not None:
        response = model.generate_content(image)
    elif question != "":
        response = model.generate_content(question)
    else:
        response = "Please provide either a question or an image to generate content."
    return response.text



# import PyPDF2
# from PyPDF2 import PdfReader
# from django.shortcuts import render, HttpResponse
# from .models import FilesUpload
# from nltk.tokenize import sent_tokenize
# from summa import keywords
# from transformers import pipeline
#
#
# def review(request):
#     return render(request, 'testapp/login.html', {})
#
# def extract_text_from_pdf(file_path):
#     text = ""
#     with open(file_path, 'rb') as file:
#         reader = PdfReader(file)
#         num_pages = len(reader.pages)
#         for page_num in range(num_pages):
#             page = reader.pages[page_num]
#             text += page.extract_text()
#     return text
#
# def extract_important_questions(text):
#     # Initialize the question generation model
#     question_generator = pipeline("question-generation")
#
#     # Generate questions for the given text
#     questions = question_generator(text)
#
#     # Extract only the generated questions
#     important_questions = [question["question"] for question in questions]
#
#     return important_questions
#
# def uploadpdf(request):
#     if request.method == "POST":
#         file = request.FILES["file"]
#         document = FilesUpload.objects.create(file=file)
#         document.save()
#
#         # Get the path to the uploaded file
#         file_path = document.file.path
#
#         # Extract text from the PDF
#         extracted_text = extract_text_from_pdf(file_path)
#
#         # Extract important questions using deep learning-based method
#         important_questions = extract_important_questions(extracted_text)
#
#         # Do something with the extracted text and important questions
#         print(extracted_text)
#         print("Important Questions:")
#         for idx, question in enumerate(important_questions, 1):
#             print(f"{idx}. {question}")
#
#         # Return the extracted text and important questions as the HTTP response
#         return HttpResponse(important_questions)
#
#     return render(request, 'testapp/uploadpdf.html', {})



# import PyPDF2
# from PyPDF2 import PdfReader
# from django.shortcuts import render, HttpResponse
# from .models import FilesUpload
# from transformers import pipeline
#
# def review(request):
#     return render(request, 'testapp/login.html', {})
#
# def extract_text_from_pdf(file_path):
#     text = ""
#     with open(file_path, 'rb') as file:
#         reader = PdfReader(file)
#         num_pages = len(reader.pages)
#         for page_num in range(num_pages):
#             page = reader.pages[page_num]
#             text += page.extract_text()
#     return text
#
# def extract_important_questions(text):
#     # Initialize the question generation model
#     question_generator = pipeline("question-generation")
#
#     # Generate questions for the given text
#     questions = question_generator(text)
#
#     # Extract only the generated questions
#     important_questions = [question["question"] for question in questions]
#
#     return important_questions
#
# def uploadpdf(request):
#     if request.method == "POST":
#         file = request.FILES["file"]
#         document = FilesUpload.objects.create(file=file)
#         document.save()
#
#         # Get the path to the uploaded file
#         file_path = document.file.path
#
#         # Extract text from the PDF
#         extracted_text = extract_text_from_pdf(file_path)
#
#         # Extract important questions using deep learning-based method
#         important_questions = extract_important_questions(extracted_text)
#
#         # Do something with the extracted text and important questions
#         print(extracted_text)
#         print("Important Questions:")
#         for idx, question in enumerate(important_questions, 1):
#             print(f"{idx}. {question}")
#
#         # Return the extracted text and important questions as the HTTP response
#         return HttpResponse("Important Questions:\n" + '\n'.join(important_questions))
#
#     return render(request, 'testapp/uploadpdf.html', {})


# from PyPDF2 import PdfReader
# from django.shortcuts import render, HttpResponse
# from .models import FilesUpload
# from transformers import pipeline
#
# def review(request):
#     return render(request, 'testapp/login.html', {})
#
# def extract_text_from_pdf(file_path):
#     text = ""
#     with open(file_path, 'rb') as file:
#         reader = PdfReader(file)
#         num_pages = len(reader.pages)
#         for page_num in range(num_pages):
#             page = reader.pages[page_num]
#             text += page.extract_text()
#     return text
#
# def extract_important_questions(text):
#     # Initialize the text-to-text generation model
#     question_generator = pipeline("text2text-generation", model="t5-small", tokenizer="t5-small")
#
#     # Generate questions for the given text using beam search decoding
#     questions = question_generator(text, max_length=32, num_return_sequences=5, num_beams=5, early_stopping=True)
#
#     # Extract only the generated questions
#     important_questions = [question["generated_text"].strip() for question in questions]
#
#     return important_questions
#
# def uploadpdf(request):
#     if request.method == "POST":
#         file = request.FILES["file"]
#         document = FilesUpload.objects.create(file=file)
#         document.save()
#
#         # Get the path to the uploaded file
#         file_path = document.file.path
#
#         # Extract text from the PDF
#         extracted_text = extract_text_from_pdf(file_path)
#
#         # Extract important questions using text-to-text generation method
#         important_questions = extract_important_questions(extracted_text)
#
#         # Do something with the extracted text and important questions
#         print(extracted_text)
#         print("Important Questions:")
#         for idx, question in enumerate(important_questions, 1):
#             print(f"{idx}. {question}")
#
#         # Return the extracted text and important questions as the HTTP response
#         return HttpResponse("Important Questions:\n" + '\n'.join(important_questions))
#
#     return render(request, 'testapp/uploadpdf.html', {})

