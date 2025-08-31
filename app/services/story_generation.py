import logging
from typing import Dict, Any, AsyncGenerator, List
from openai import AsyncOpenAI

from app.core.configs import settings
from app.schemas.story import StoryGenerateWithHeroesRequest
from app.schemas.hero import HeroOut


class StoryGenerationService:
    """Service for generating fairy tales using OpenAI GPT-4o-mini"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.client = AsyncOpenAI(api_key=settings.openai.API_KEY)
    

    async def generate_story_with_heroes(self, story_params: StoryGenerateWithHeroesRequest) -> str:
        """
        Generate a fairy tale story with multiple heroes.
        
        Args:
            story_params: StoryGenerateWithHeroesRequest object with heroes list
            
        Returns:
            str: Generated story content
        """
        self.logger.info(f"Generating story with heroes: {story_params.story_name}")
        
        try:
            # Build the prompt for OpenAI with heroes
            prompt = self._build_prompt_with_heroes(story_params)
            
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
            self.logger.info(f"Generated story with heroes of {len(story_content)} characters")
            
            return story_content
            
        except Exception as e:
            self.logger.error(f"Error generating story with heroes: {str(e)}")
            raise Exception(f"Failed to generate story with heroes: {str(e)}")

    async def generate_story_with_heroes_stream(self, story_params: StoryGenerateWithHeroesRequest) -> AsyncGenerator[str, None]:
        """
        Generate a fairy tale story with multiple heroes using streaming response.
        
        Args:
            story_params: StoryGenerateWithHeroesRequest object with heroes list
            
        Yields:
            str: Chunks of generated story content
        """
        self.logger.info(f"🚀 Starting streaming generation for story with heroes: {story_params.story_name}")
        self.logger.info(f"📊 Heroes count: {len(story_params.heroes)}")
        self.logger.info(f"🎯 Story style: {story_params.story_style}, Language: {story_params.language}")
        
        try:
            # Build the prompt for OpenAI with heroes
            self.logger.info("🔨 Building prompt with heroes...")
            prompt = self._build_prompt_with_heroes(story_params)
            self.logger.info(f"📝 Prompt length: {len(prompt)} characters")
            self.logger.debug(f"📄 Full prompt: {prompt[:500]}...")
            
            # Call OpenAI API with streaming
            self.logger.info("🌐 Calling OpenAI API for streaming...")
            self.logger.info(f"🔧 Model: {settings.openai.MODEL}, Max tokens: {settings.openai.MAX_TOKENS}, Temp: {settings.openai.TEMPERATURE}")
            
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
            
            self.logger.info("✅ OpenAI stream created successfully, starting to process chunks...")
            
            chunk_count = 0
            total_content = ""
            
            # Stream the response
            async for chunk in stream:
                chunk_count += 1
                self.logger.debug(f"📦 Processing chunk #{chunk_count}")
                
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    total_content += content
                    self.logger.debug(f"📤 Yielding chunk: {len(content)} characters")
                    yield content
                else:
                    self.logger.debug(f"⚪ Empty chunk #{chunk_count}")
            
            self.logger.info(f"🎉 Streaming generation with heroes completed successfully!")
            self.logger.info(f"📈 Total chunks processed: {chunk_count}")
            self.logger.info(f"📊 Total content length: {len(total_content)} characters")
            
        except Exception as e:
            self.logger.error(f"❌ Error in streaming generation with heroes: {str(e)}")
            self.logger.error(f"🔍 Error type: {type(e).__name__}")
            import traceback
            self.logger.error(f"📍 Traceback: {traceback.format_exc()}")
            raise Exception(f"Failed to generate story stream with heroes: {str(e)}")
    
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
- DO NOT end stories with "The End", "Конец", "Fin", "Finale" or similar ending phrases
- Stories should conclude naturally with the final narrative sentence
- Use ONLY short dashes (-) for punctuation, NOT long em-dashes (—) or en-dashes (–)

Remember: You are creating magical, safe, and enriching experiences for young minds."""

    def _build_prompt_with_heroes(self, story_params: StoryGenerateWithHeroesRequest) -> str:
        """Build the user prompt with story parameters and heroes list"""
        
        self.logger.info(f"📝 Building prompt for story: {story_params.story_name}")
        self.logger.info(f"🦸 Heroes received: {len(story_params.heroes)}")
        
        for i, hero in enumerate(story_params.heroes):
            self.logger.info(f"🦸‍♂️ Hero {i+1}: {hero.name} (age {hero.age}, {hero.gender})")
        
        # Determine age from the average of heroes' ages or use youngest hero's age for age-appropriate content
        hero_ages = [hero.age for hero in story_params.heroes]
        target_age = min(hero_ages)  # Use youngest hero's age for appropriate content
        self.logger.info(f"🎯 Target age for content: {target_age}")
        
        # Age-appropriate guidelines
        age_guidance = self._get_age_specific_guidance(target_age)
        
        # Language-specific elements
        language_guidance = self._get_language_guidance(story_params.language.value)
        
        # Build heroes description
        self.logger.info("🎭 Formatting heroes for prompt...")
        heroes_description = self._format_heroes_for_prompt(story_params.heroes)
        self.logger.info(f"📋 Heroes description length: {len(heroes_description)} chars")
        
        prompt = f"""Create a {story_params.story_style.value.lower()} fairy tale with these specifications:

STORY DETAILS:
- Title: "{story_params.story_name}"
- Story idea: {story_params.story_idea}
- Language: {story_params.language.value.upper()}
- Style: {story_params.story_style.value}
- Story length: {story_params.story_length.value} (1=very short, 2=short, 3=medium, 4=long, 5=very long)

MAIN CHARACTERS (HEROES):
{heroes_description}

AGE REQUIREMENTS:
{age_guidance}

LANGUAGE REQUIREMENTS:
{language_guidance}

STORY REQUIREMENTS:
- Length: {self._get_length_guidance(story_params.story_length.value)}
- Include traditional fairy tale elements and magical moments
- Feature ALL the heroes listed above as main characters in the story
- Give each hero meaningful roles and showcase their unique personalities and powers
- Create interactions between the heroes that highlight their different strengths
- Incorporate the story idea naturally into the plot involving all heroes
- End with a clear moral lesson appropriate for the age group
- Use rich, descriptive language that helps children visualize the story
- IMPORTANT: Do NOT end with "The End" or equivalent phrases - let the story conclude naturally
- Use simple punctuation: short dashes (-) only, avoid long dashes (—) or special symbols
- Balance the story so all heroes contribute meaningfully to the adventure

Please write the complete fairy tale now featuring all the heroes working together."""
        
        return prompt

    def _format_heroes_for_prompt(self, heroes: List[HeroOut]) -> str:
        """Format heroes list for inclusion in the prompt"""
        heroes_text = ""
        for i, hero in enumerate(heroes, 1):
            heroes_text += f"""
{i}. {hero.name} ({hero.gender}, age {hero.age})
   - Appearance: {hero.appearance or 'Not specified'}
   - Personality: {hero.personality or 'Not specified'}
   - Special Power: {hero.power or 'No special powers'}"""
        
        return heroes_text.strip()
    
    def _get_age_specific_guidance(self, age: int) -> str:
        """Get age-specific content guidance"""
        if age <= 5:
            return """- Use very simple sentences and basic vocabulary
- Focus on concrete concepts and familiar situations
- Include repetitive elements and simple rhymes
- Story should be 2-3 minutes reading time
- Emphasize basic concepts like colors, numbers, animals
- Very gentle conflicts with immediate, happy solutions"""
        
        elif age <= 8:
            return """- Use clear, engaging sentences with expanded vocabulary
- Include some adventure but keep it safe and non-threatening
- Add simple problem-solving elements
- Story should be 3-4 minutes reading time
- Can include mild suspense that quickly resolves positively
- Focus on friendship, sharing, and basic life lessons"""
        
        elif age <= 12:
            return """- Use rich vocabulary and more complex sentence structures
- Include character development and emotional growth
- Add meaningful challenges that teach resilience
- Story should be 4-5 minutes reading time
- Can explore themes of courage, honesty, and perseverance
- Include subtle moral lessons woven into the narrative"""
        
        else:
            return """- Use sophisticated language and narrative techniques
- Explore deeper themes while maintaining appropriateness
- Include complex character relationships and growth
- Story should be 5-6 minutes reading time
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
    
    def _get_length_guidance(self, story_length: int) -> str:
        """Get length-specific guidance for story generation"""
        length_guidance = {
            1: "Approximately 100-200 words (very short story)",
            2: "Approximately 200-300 words (short story)",
            3: "Approximately 300-400 words (medium story)",
            4: "Approximately 400-500 words (long story)",
            5: "Approximately 500-600 words (very long story)"
        }
        return length_guidance.get(story_length, length_guidance[3])


# Create service instance
story_generation_service = StoryGenerationService()