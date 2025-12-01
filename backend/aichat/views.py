from django.shortcuts import render
from rest_framework.views import APIView, Response
from rest_framework import status
from google import generativeai as genai
import os

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Create your views here.

class AIAgent(APIView):
    def post(self, request):
        message = request.data["message"]
        prompt = f"""
        You are a guide for my mafia game.
        The user says {message}.
        Respone with short and precise information conserning the game.
        Anything conserning anyother thing should be met with a 'Sorry I can't help with'.
        This is the context of the game: 
        role: "There are 4 roles: Mafia (hidden killers) and Villager (innocent). Each has different abilities!",
        win: "Town wins if all mafia are eliminated. Mafia wins if they equal the innocent players.",
        strategy: "Listen to discussions, observe voting patterns, and ask questions. Don't trust everyone! As mafia, create alibis.",
        mafia: "Mafia members vote during the day and eliminate innocents at night.",
        day: "During the day, all players discuss and vote to eliminate someone they think is mafia.",
        night: "At night, mafia kills. Innocent players wait.",
        vote: "The player with the most votes during the day is eliminated.",
        How to play: "You can either create or join available lobbies and enjoy the game with friends or foes"
        default: "I can help! Ask about roles, winning conditions, strategy, or specific phases like day/night. What would you like to know?"
        Be concise and clear and SHORT/BREIF
        """
        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            ai_response = model.generate_content(prompt).text

            return Response({"message": ai_response}, status=200)
        except Exception as e:
            return Response({"message": f"Sorry I encountered an error: {str(e)}"}, status=500)

