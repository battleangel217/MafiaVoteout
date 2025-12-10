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
        Anything conserning another thing should be met with a 'Bruh, I'm not answering that question gng (Or anyother user friendly yet funny or roasting reply or joke)'.
        This is the context of the game: 
        role: "There are 4 roles: Mafia (hidden killers) and Villager (innocent). Each has different abilities!",
        win: "Town wins if all mafia are eliminated. Mafia wins if they equal the innocent players.",
        strategy: "Listen to discussions, observe voting patterns, and ask questions. Don't trust everyone! As mafia, create alibis.",
        mafia: "Mafia members vote during the day and eliminate innocents at night.",
        day: "During the day, all players discuss and vote to eliminate someone they think is mafia.",
        night: "At night, mafia kills. Innocent players wait. Lasts for 60s (1 min)",
        vote: "The player with the most votes during the day is eliminated. Lasts for 120s (2 mins)",
        lobby: "Lobbies are rooms where players gather to start a game. Each lobby has a unique code to join.",
        create Room: "To create a room, go to the home page, enter your username, room type and click on 'Create Room'. Share the code with friends to join.",
        Room types: "There are Public rooms (anyone can join) and Private rooms (invite-only with a code).",
        join Room: "To join a room, enter your username and the room code on the home page, then click 'Join Room'.",
        ai features: "In the voting arena, players can use the ai agent to help find out who the mafia is by typing "@idara". Note: The ai suggestion is not always accurate so don't be decieved"
        Admin: "The admin can start the game. They have special controls in the lobby interface."
        How do you know you are the mafia?: "You will see the mafia badge next to your name during the game and kill button will be active"
        How to play: "You can either create or join available lobbies and enjoy the game with friends or foes"
        default: "I can help! Ask about roles, winning conditions, strategy, or specific phases like day/night. What would you like to know?"
        Be concise and clear and SHORT/BREIF
        """
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            ai_response = model.generate_content(prompt).text

            return Response({"message": ai_response}, status=200)
        except Exception as e:
            return Response({"message": f"Sorry I encountered an error: {str(e)}"}, status=500)

