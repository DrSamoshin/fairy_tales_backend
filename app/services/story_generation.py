import logging
from typing import Dict, Any, AsyncGenerator
from openai import AsyncOpenAI

from app.core.configs import settings
from app.schemas.story import StoryGenerate


class StoryGenerationService:
    """Service for generating fairy tales using OpenAI GPT-4o-mini"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = AsyncOpenAI(api_key=settings.openai.API_KEY)
    
    async def generate_story(self, story_params: StoryGenerate) -> str:
        """
        Generate a fairy tale story based on provided parameters using OpenAI.
        
        Args:
            story_params: StoryGenerate object with all story parameters
            
        Returns:
            str: Generated story content
        """
        self.logger.info(f"Generating story: {story_params.story_name}")
        
        try:
            # Build the prompt for OpenAI
            prompt = self._build_prompt(story_params)
            
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=settings.openai.MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai.MAX_TOKENS,
                temperature=settings.openai.TEMPERATURE
            )
            
            story_content = response.choices[0].message.content
            self.logger.info(f"Generated story of {len(story_content)} characters")
            
            return story_content
            
        except Exception as e:
            self.logger.error(f"Error generating story: {str(e)}")
            raise Exception(f"Failed to generate story: {str(e)}")
    
    async def generate_story_stream(self, story_params: StoryGenerate) -> AsyncGenerator[str, None]:
        """
        Generate a fairy tale story with streaming response.
        
        Args:
            story_params: StoryGenerate object with all story parameters
            
        Yields:
            str: Chunks of generated story content
        """
        self.logger.info(f"Starting streaming generation for story: {story_params.story_name}")
        
        try:
            # Build the prompt for OpenAI
            prompt = self._build_prompt(story_params)
            
            # Call OpenAI API with streaming
            stream = await self.client.chat.completions.create(
                model=settings.openai.MODEL,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=settings.openai.MAX_TOKENS,
                temperature=settings.openai.TEMPERATURE,
                stream=True
            )
            
            # Stream the response
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    self.logger.debug(f"Streaming chunk: {len(content)} characters")
                    yield content
            
            self.logger.info("Streaming generation completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in streaming generation: {str(e)}")
            raise Exception(f"Failed to generate story stream: {str(e)}")
    
    def _get_system_prompt(self) -> str:
        """
        Returns the system prompt that defines the AI's role and constraints.
        This prompt ensures child-friendly content and fairy tale style.
        """
        return """You are a professional children's fairy tale writer specializing in age-appropriate stories for children up to 12 years old.

STRICT GUIDELINES:
1. Create ONLY fairy tales and fantasy stories suitable for children
2. Content must be 100% appropriate for ages 0-12 years
3. NO violence, scary content, death, or inappropriate themes
4. Focus on positive values: friendship, kindness, courage, learning, family
5. Use simple, clear language appropriate for the target age
6. Include magic, wonder, and imagination
7. Always have a positive, uplifting ending
8. Promote good morals and life lessons

FORBIDDEN CONTENT:
- Violence, fighting, or scary scenes
- Death, illness, or sad endings
- Adult themes or complex emotional situations
- Frightening creatures or situations
- Any content that might cause nightmares or distress

STORY STRUCTURE:
- Clear beginning, middle, and end
- Engaging characters children can relate to
- Simple conflicts that are easily resolved
- Educational or moral elements woven naturally
- Descriptive language that sparks imagination

FORMAT REQUIREMENTS:
- Write in PLAIN TEXT format only
- NO markdown formatting (no #, *, **, _, etc.)
- NO headers, bold text, or special formatting
- Use simple paragraphs separated by line breaks
- Present the story as continuous narrative text

Remember: You are creating magical, safe, and enriching experiences for young minds."""

    def _build_prompt(self, story_params: StoryGenerate) -> str:
        """Build the user prompt with story parameters"""
        
        # Age-appropriate guidelines
        age_guidance = self._get_age_specific_guidance(story_params.age)
        
        # Language-specific elements
        language_guidance = self._get_language_guidance(story_params.language.value)
        
        prompt = f"""Create a {story_params.story_style.value.lower()} fairy tale with these specifications:

STORY DETAILS:
- Title: "{story_params.story_name}"
- Main character: {story_params.hero_name}
- Story idea: {story_params.story_idea}
- Target age: {story_params.age} years old
- Language: {story_params.language.value.upper()}
- Style: {story_params.story_style.value}

AGE REQUIREMENTS:
{age_guidance}

LANGUAGE REQUIREMENTS:
{language_guidance}

STORY REQUIREMENTS:
- Length: Approximately 800-1200 words
- Include traditional fairy tale elements and magical moments
- Make {story_params.hero_name} a relatable and positive role model
- Incorporate the story idea naturally into the plot
- End with a clear moral lesson appropriate for the age group
- Use rich, descriptive language that helps children visualize the story

Please write the complete fairy tale now."""
        
        return prompt
    
    def _get_age_specific_guidance(self, age: int) -> str:
        """Get age-specific content guidance"""
        if age <= 5:
            return """- Use very simple sentences and basic vocabulary
- Focus on concrete concepts and familiar situations
- Include repetitive elements and simple rhymes
- Story should be 5-8 minutes reading time
- Emphasize basic concepts like colors, numbers, animals
- Very gentle conflicts with immediate, happy solutions"""
        
        elif age <= 8:
            return """- Use clear, engaging sentences with expanded vocabulary
- Include some adventure but keep it safe and non-threatening
- Add simple problem-solving elements
- Story should be 8-12 minutes reading time
- Can include mild suspense that quickly resolves positively
- Focus on friendship, sharing, and basic life lessons"""
        
        elif age <= 12:
            return """- Use rich vocabulary and more complex sentence structures
- Include character development and emotional growth
- Add meaningful challenges that teach resilience
- Story should be 12-15 minutes reading time
- Can explore themes of courage, honesty, and perseverance
- Include subtle moral lessons woven into the narrative"""
        
        else:
            return """- Use sophisticated language and narrative techniques
- Explore deeper themes while maintaining appropriateness
- Include complex character relationships and growth
- Story should be 15-20 minutes reading time
- Address more nuanced moral and ethical concepts
- Prepare for transition to young adult themes"""
    
    def _get_language_guidance(self, language: str) -> str:
        """Get language-specific guidance for story generation"""
        guidance = {
            "en": "Write in clear, engaging English with proper grammar and rich vocabulary appropriate for native English-speaking children.",
            "ru": "Пишите на ясном, увлекательном русском языке с правильной грамматикой и богатой лексикой, подходящей для русскоговорящих детей.",
            "es": "Escribe en español claro y atractivo con gramática correcta y vocabulario rico apropiado para niños hispanohablantes.",
            "fr": "Écrivez en français clair et engageant avec une grammaire correcte et un vocabulaire riche approprié pour les enfants francophones.",
            "de": "Schreiben Sie in klarem, ansprechendem Deutsch mit korrekter Grammatik und reichem Wortschatz, der für deutschsprachige Kinder geeignet ist."
        }
        return guidance.get(language, guidance["en"])


# Create service instance
story_generation_service = StoryGenerationService()