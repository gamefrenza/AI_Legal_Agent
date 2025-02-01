from typing import Dict, Optional
import spacy
from transformers import pipeline

class NLPProcessor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_lg")
        self.summarizer = pipeline("summarization")
        self.generator = pipeline("text-generation")
    
    async def enhance_content(self, text: str, context: Optional[Dict] = None) -> str:
        """Enhance content using NLP"""
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Perform named entity recognition
        entities = self._extract_entities(doc)
        
        # Enhance content based on context
        if context:
            text = await self._context_aware_enhancement(text, context, entities)
        
        # Improve text clarity and structure
        text = await self._improve_text_structure(text)
        
        return text
    
    async def _context_aware_enhancement(
        self,
        text: str,
        context: Dict,
        entities: Dict
    ) -> str:
        """Enhance text based on context and entities"""
        
        # Add relevant context
        if context.get('jurisdiction'):
            text = self._add_jurisdiction_context(text, context['jurisdiction'])
        
        # Add entity definitions where needed
        text = self._add_entity_definitions(text, entities)
        
        return text
    
    async def _improve_text_structure(self, text: str) -> str:
        """Improve text structure and clarity"""
        
        # Split into sentences
        doc = self.nlp(text)
        sentences = [sent.text.strip() for sent in doc.sents]
        
        # Improve each sentence
        improved_sentences = []
        for sent in sentences:
            # Check for passive voice
            if self._is_passive(sent):
                sent = self._convert_to_active(sent)
            
            # Simplify complex sentences
            if self._is_complex(sent):
                sent = self._simplify_sentence(sent)
                
            improved_sentences.append(sent)
        
        return ' '.join(improved_sentences)
    
    def _extract_entities(self, doc) -> Dict:
        """Extract and classify named entities"""
        entities = {}
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)
        return entities 