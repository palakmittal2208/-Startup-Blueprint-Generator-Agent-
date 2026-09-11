# 🚀 Startup Blueprint Generator Agent

An advanced, AI-powered web application designed to help entrepreneurs instantly generate structured business blueprints, market strategies, and financial insights using the IBM watsonx AI API.

## 🌟 Project Overview
Building a startup plan from scratch can take weeks. This application bridges that gap by leveraging cutting-edge IBM watsonx Granite language models to transform a simple text description of a startup concept into a professional, concise, and actionable business blueprint.

## 💡 Sample Startup Idea Tested
* **Concept**: An edtech app that teaches coding to kids aged 8-14 through gamified AI-powered lessons, adapting difficulty based on the child's learning pace.

## ✨ Key Features
* **AI-Driven Intelligence**: Powered by IBM watsonx for deep, context-aware business analysis.
* **Sleek UI/UX Design**: Built with a modern dark-mode glassmorphism interface for a smooth user experience.
* **Rapid Generation**: Delivers structured insights and strategies in seconds.

## 🛠️ Technology Stack
* **Programming Language**: Python
* **Backend Framework**: Flask
* **Frontend**: HTML5, CSS3, JavaScript
* **APIs & Libraries**: IBM watsonx AI API, Requests, Python-Dotenv

## ⚙️ Installation & Setup Guide
1. Clone the repository: 
   git clone https://github.com/palakmittal2208/-Startup-Blueprint-Generator-Agent-
2. Navigate into the folder: 
   cd Startup-Blueprint-Generator-Agent
3. Install dependencies: 
   pip install -r requirements.txt
4. Set up your environment variables in a .env file.
5. Run the application: 
   python app.py
   
 ## ⚠️ Challenges Faced & Troubleshooting (IBM watsonx AI Integration)

During the development and testing of the live web application, we encountered a few technical hurdles related to the AI model's response generation:

* **Infinite Loop & Repetition Issue:** 
  * While processing certain prompts, the application occasionally got caught in a repetitive loop, generating overlapping or redundant sentences instead of moving forward with the blueprint text.
  * *Cause:* This happened due to prompt formatting or response stream handling where the model kept repeating tokens without a proper exit condition.

* **Incomplete / Truncated Outputs:** 
  * The generated startup blueprints were sometimes cutting off midway and failing to display the complete content.
  * *Cause:* The `max_new_tokens` parameter limit was initially too low for comprehensive text generation, causing the model to stop abruptly before finishing the response.

* **Resolution:** 
  * Adjusted the model generation parameters (increasing token limits and optimizing prompt structure) in the backend code to ensure clean, continuous, and non-repeating outputs from IBM watsonx.
