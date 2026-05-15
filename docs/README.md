# Intelligent Conversational Agent

## Overview

Create a conversational AI system that simulates an intelligent agent for a fictional
business called AD&DHelp. The bot should conduct short interviews with customers to gather
information and provide appropriate responses regarding customer doubts about Advanced Dungeons & Dragons Role Playing Games, books, rulebooks, game mechanics, etc. 

## Core Requirements

1. **Conversational Flow**
    - Implement a bot that can engage in natural conversation with users
    - Bot should collect specific information. The agent would collect information about customer doubts about AD&D
    including: game system, problem category, problem description, and
    urgency level
    - Extract and validate this information into a structured format
    - Handle basic error cases and invalid inputs gracefully
    - Maintain conversation context throughout the interaction
2. **Data Extraction & Storage**
    - Store conversations and extracted data in a structured format (JSON)
    - Implement basic data validation for collected information
    - Generate a summary of the conversation with extracted key points
3. **Technical Requirements**
    - Use Python for backend implementation
    - Implement proper error handling
    - Use the LLM of your choice, considering the use case
    - Use the conversational AI platform/model of your choice for text
    transcription and TTS