import re
import random
from typing import List, Dict

class FlashcardGenerator:
    def __init__(self):
        self.question_starters = [
            "What is",
            "Define",
            "Explain",
            "Describe",
            "How does",
            "Why is",
            "What are the main features of",
            "What is the purpose of",
            "How can you",
            "What does"
        ]
    
    def generate_flashcards(self, text: str, num_cards: int = 15) -> List[Dict]:
        """
        Generate flashcards from extracted text
        
        Args:
            text (str): Source text
            num_cards (int): Number of flashcards to generate
            
        Returns:
            List[Dict]: List of flashcard dictionaries
        """
        flashcards = []
        
        try:
            # Split text into sentences and paragraphs
            sentences = self._split_into_sentences(text)
            paragraphs = self._split_into_paragraphs(text)
            
            # Extract key concepts and definitions
            concepts = self._extract_key_concepts(text)
            definitions = self._extract_definitions(text)
            
            # Generate different types of flashcards
            card_types = [
                ('concept', 0.4),
                ('definition', 0.3),
                ('fact', 0.2),
                ('process', 0.1)
            ]
            
            cards_generated = 0
            
            for card_type, ratio in card_types:
                cards_needed = min(int(num_cards * ratio), num_cards - cards_generated)
                
                if card_type == 'concept' and concepts:
                    flashcards.extend(self._generate_concept_cards(concepts, cards_needed))
                elif card_type == 'definition' and definitions:
                    flashcards.extend(self._generate_definition_cards(definitions, cards_needed))
                elif card_type == 'fact':
                    flashcards.extend(self._generate_fact_cards(sentences, cards_needed))
                elif card_type == 'process':
                    flashcards.extend(self._generate_process_cards(paragraphs, cards_needed))
                
                cards_generated = len(flashcards)
                
                if cards_generated >= num_cards:
                    break
            
            # Fill remaining slots with general cards
            while len(flashcards) < num_cards and sentences:
                flashcards.extend(self._generate_general_cards(sentences, num_cards - len(flashcards)))
            
            # Shuffle and return requested number
            random.shuffle(flashcards)
            return flashcards[:num_cards]
            
        except Exception as e:
            # Fallback to simple sentence-based generation
            return self._generate_simple_flashcards(text, num_cards)
    
    def generate_questions(self, text: str, num_questions: int = 10) -> List[Dict]:
        """
        Generate multiple choice questions from text
        
        Args:
            text (str): Source text
            num_questions (int): Number of questions to generate
            
        Returns:
            List[Dict]: List of question dictionaries
        """
        questions = []
        
        try:
            sentences = self._split_into_sentences(text)
            concepts = self._extract_key_concepts(text)
            
            # Generate different types of questions
            question_sources = []
            
            # Add concept-based questions
            for concept in concepts[:num_questions]:
                question_sources.append(('concept', concept))
            
            # Add sentence-based questions
            for sentence in sentences[:num_questions]:
                if len(sentence.split()) > 8:  # Only use substantial sentences
                    question_sources.append(('sentence', sentence))
            
            random.shuffle(question_sources)
            
            for source_type, source_content in question_sources[:num_questions]:
                if source_type == 'concept':
                    question = self._generate_concept_question(source_content, text)
                else:
                    question = self._generate_sentence_question(source_content, text)
                
                if question:
                    questions.append(question)
            
            return questions[:num_questions]
            
        except Exception as e:
            return self._generate_simple_questions(text, num_questions)
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        paragraphs = text.split('\n\n')
        return [p.strip() for p in paragraphs if len(p.strip()) > 50]
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts and terms from text"""
        # Look for capitalized terms, technical terms, and important phrases
        concepts = []
        
        # Find capitalized terms (potential proper nouns/concepts)
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        concepts.extend(list(set(capitalized_terms)))
        
        # Find terms in quotes
        quoted_terms = re.findall(r'"([^"]*)"', text)
        concepts.extend(quoted_terms)
        
        # Find terms that appear frequently
        words = text.lower().split()
        word_freq = {}
        for word in words:
            if len(word) > 4 and word.isalpha():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Add frequent important-looking words
        frequent_words = [word for word, freq in word_freq.items() if freq > 2 and len(word) > 6]
        concepts.extend(frequent_words[:10])
        
        return list(set(concepts))[:20]  # Return up to 20 unique concepts
    
    def _extract_definitions(self, text: str) -> List[Dict]:
        """Extract definitions from text"""
        definitions = []
        
        # Look for definition patterns
        definition_patterns = [
            r'([A-Za-z\s]+)\s+is\s+([^.]+)',
            r'([A-Za-z\s]+)\s+refers to\s+([^.]+)',
            r'([A-Za-z\s]+)\s+means\s+([^.]+)',
            r'([A-Za-z\s]+)\s+can be defined as\s+([^.]+)',
        ]
        
        for pattern in definition_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for term, definition in matches:
                if len(term.strip()) < 50 and len(definition.strip()) > 10:
                    definitions.append({
                        'term': term.strip(),
                        'definition': definition.strip()
                    })
        
        return definitions[:15]
    
    def _generate_concept_cards(self, concepts: List[str], num_cards: int) -> List[Dict]:
        """Generate flashcards for key concepts"""
        cards = []
        
        for concept in concepts[:num_cards]:
            question = f"What is {concept}?"
            answer = f"A key concept mentioned in the document. {concept} is an important term that appears in the text."
            
            cards.append({
                'question': question,
                'answer': answer,
                'type': 'concept'
            })
        
        return cards
    
    def _generate_definition_cards(self, definitions: List[Dict], num_cards: int) -> List[Dict]:
        """Generate flashcards from definitions"""
        cards = []
        
        for definition in definitions[:num_cards]:
            cards.append({
                'question': f"What is {definition['term']}?",
                'answer': definition['definition'],
                'type': 'definition'
            })
        
        return cards
    
    def _generate_fact_cards(self, sentences: List[str], num_cards: int) -> List[Dict]:
        """Generate fact-based flashcards"""
        cards = []
        
        for sentence in sentences[:num_cards]:
            # Try to create a question from the sentence
            words = sentence.split()
            if len(words) > 8:
                # Remove the last few words to create a question
                question_words = words[:max(5, len(words) - 3)]
                question = " ".join(question_words) + "...?"
                answer = sentence
                
                cards.append({
                    'question': f"Complete: {question}",
                    'answer': answer,
                    'type': 'fact'
                })
        
        return cards
    
    def _generate_process_cards(self, paragraphs: List[str], num_cards: int) -> List[Dict]:
        """Generate process-based flashcards"""
        cards = []
        
        for paragraph in paragraphs[:num_cards]:
            # Look for process indicators
            if any(word in paragraph.lower() for word in ['first', 'then', 'next', 'finally', 'process', 'step']):
                question = "Describe the process mentioned in the text."
                answer = paragraph[:200] + "..." if len(paragraph) > 200 else paragraph
                
                cards.append({
                    'question': question,
                    'answer': answer,
                    'type': 'process'
                })
        
        return cards
    
    def _generate_general_cards(self, sentences: List[str], num_cards: int) -> List[Dict]:
        """Generate general flashcards from sentences"""
        cards = []
        
        selected_sentences = random.sample(sentences, min(num_cards, len(sentences)))
        
        for sentence in selected_sentences:
            starter = random.choice(self.question_starters)
            # Extract the main subject/concept from the sentence
            words = sentence.split()
            if len(words) > 5:
                question = f"{starter} mentioned in this context?"
                answer = sentence
                
                cards.append({
                    'question': question,
                    'answer': answer,
                    'type': 'general'
                })
        
        return cards
    
    def _generate_simple_flashcards(self, text: str, num_cards: int) -> List[Dict]:
        """Fallback method for simple flashcard generation"""
        sentences = self._split_into_sentences(text)
        flashcards = []
        
        for i, sentence in enumerate(sentences[:num_cards]):
            question = f"What does the text say about topic {i + 1}?"
            answer = sentence
            
            flashcards.append({
                'question': question,
                'answer': answer,
                'type': 'simple'
            })
        
        return flashcards
    
    def _generate_concept_question(self, concept: str, text: str) -> Dict:
        """Generate a multiple choice question about a concept"""
        # Find sentences containing the concept
        sentences = [s for s in self._split_into_sentences(text) if concept.lower() in s.lower()]
        
        if not sentences:
            return {}
        
        # Use the first sentence as context
        context_sentence = sentences[0]
        
        question = f"What is mentioned about {concept} in the text?"
        correct_answer = context_sentence[:100] + "..." if len(context_sentence) > 100 else context_sentence
        
        # Generate distractors
        other_sentences = [s for s in self._split_into_sentences(text) if concept.lower() not in s.lower()]
        distractors = [s[:100] + "..." if len(s) > 100 else s for s in random.sample(other_sentences, min(3, len(other_sentences)))]
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        
        return {
            'question': question,
            'options': options,
            'correct_answer': correct_answer,
            'type': 'concept'
        }
    
    def _generate_sentence_question(self, sentence: str, text: str) -> Dict:
        """Generate a multiple choice question from a sentence"""
        words = sentence.split()
        
        if len(words) < 8:
            return {}
        
        # Create a fill-in-the-blank question
        key_word_index = len(words) // 2
        key_word = words[key_word_index]
        
        # Create question by removing the key word
        question_words = words.copy()
        question_words[key_word_index] = "_____"
        question = "Fill in the blank: " + " ".join(question_words)
        
        correct_answer = key_word
        
        # Generate distractors from other words in text
        all_words = text.split()
        similar_words = [w for w in all_words if len(w) > 3 and w != key_word and w.isalpha()]
        distractors = random.sample(similar_words, min(3, len(similar_words)))
        
        options = [correct_answer] + distractors
        random.shuffle(options)
        
        return {
            'question': question,
            'options': options,
            'correct_answer': correct_answer,
            'type': 'fill_blank'
        }
    
    def _generate_simple_questions(self, text: str, num_questions: int) -> List[Dict]:
        """Fallback method for simple question generation"""
        sentences = self._split_into_sentences(text)
        questions = []
        
        for i, sentence in enumerate(sentences[:num_questions]):
            question_text = f"What does statement {i + 1} in the text refer to?"
            correct_answer = sentence[:80] + "..." if len(sentence) > 80 else sentence
            
            # Simple distractors
            distractors = [
                "This information is not mentioned in the text",
                "The text discusses a different topic",
                "This refers to a different concept"
            ]
            
            options = [correct_answer] + distractors
            random.shuffle(options)
            
            questions.append({
                'question': question_text,
                'options': options,
                'correct_answer': correct_answer,
                'type': 'simple'
            })
        
        return questions
