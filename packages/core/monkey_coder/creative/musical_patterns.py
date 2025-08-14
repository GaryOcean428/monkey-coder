"""
Musical Improvisation Pattern System for Creative Code Generation.

This module implements musical theory principles to enable creative code generation
that can improvise while maintaining structure, similar to a concert pianist who
can improvise yet hold the melody.
"""

import logging
import random
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import numpy as np
from collections import deque

logger = logging.getLogger(__name__)

class MusicalMode(str, Enum):
    """Musical modes that influence code generation style."""
    IONIAN = "ionian"  # Major scale - conventional, clear
    DORIAN = "dorian"  # Minor with raised 6th - sophisticated, jazzy
    PHRYGIAN = "phrygian"  # Minor with lowered 2nd - exotic, experimental
    LYDIAN = "lydian"  # Major with raised 4th - dreamy, innovative
    MIXOLYDIAN = "mixolydian"  # Major with lowered 7th - bluesy, functional
    AEOLIAN = "aeolian"  # Natural minor - melancholic, deep
    LOCRIAN = "locrian"  # Diminished - unstable, avant-garde

class MusicalForm(str, Enum):
    """Musical forms that structure code generation."""
    SONATA = "sonata"  # Exposition-Development-Recapitulation (3 parts)
    RONDO = "rondo"  # ABACA pattern - recurring theme with variations
    FUGUE = "fugue"  # Interweaving themes - complex multi-threading
    THEME_VARIATIONS = "theme_variations"  # Main idea with creative variations
    BINARY = "binary"  # AB form - two contrasting sections
    TERNARY = "ternary"  # ABA form - statement, contrast, return
    THROUGH_COMPOSED = "through_composed"  # Continuous development

class Dynamics(str, Enum):
    """Dynamic levels that influence code verbosity and complexity."""
    PPP = "ppp"  # Pianississimo - extremely minimal
    PP = "pp"  # Pianissimo - very minimal
    P = "p"  # Piano - minimal, clean
    MP = "mp"  # Mezzo-piano - moderately minimal
    MF = "mf"  # Mezzo-forte - moderate
    F = "f"  # Forte - verbose, detailed
    FF = "ff"  # Fortissimo - very verbose
    FFF = "fff"  # Fortississimo - extremely verbose

@dataclass
class MusicalPhrase:
    """Represents a musical phrase in code generation."""
    phrase_id: str
    content: str
    mode: MusicalMode
    dynamics: Dynamics
    tension: float = 0.5  # 0.0 (relaxed) to 1.0 (tense)
    resolution_point: bool = False  # Is this a cadence/resolution point?
    can_improvise: bool = True  # Can this phrase be improvised upon?
    motif_references: List[str] = field(default_factory=list)  # References to other motifs

@dataclass
class Motif:
    """A recurring musical/code pattern that can be developed."""
    motif_id: str
    pattern: str  # Core pattern/concept
    transformations: List[str] = field(default_factory=list)  # Variations
    appearances: List[int] = field(default_factory=list)  # Where it appears
    importance: float = 0.5  # How central this motif is (0.0 to 1.0)

@dataclass
class HarmonicProgression:
    """Represents the harmonic structure of code generation."""
    chords: List[str]  # Sequence of "chords" (code structures)
    tension_curve: List[float]  # Tension levels throughout
    cadence_points: List[int]  # Indices where resolution occurs
    modulation_points: List[int]  # Where the "key" changes

class MusicalComposer:
    """
    Composes code using musical principles, enabling improvisation
    while maintaining structural integrity.
    """
    
    def __init__(self, form: MusicalForm = MusicalForm.SONATA):
        """
        Initialize the musical composer.
        
        Args:
            form: The musical form to use for composition
        """
        self.form = form
        self.mode = MusicalMode.IONIAN  # Start in "major"
        self.current_dynamics = Dynamics.MF
        
        # Musical elements
        self.phrases: List[MusicalPhrase] = []
        self.motifs: Dict[str, Motif] = {}
        self.harmonic_progression = None
        
        # Performance state
        self.current_measure = 0
        self.tension_level = 0.0
        self.improvisation_freedom = 0.3  # How much to improvise (0.0 to 1.0)
        
        # Memory of what's been played
        self.phrase_history: deque = deque(maxlen=20)
        self.upcoming_phrases: List[MusicalPhrase] = []
        
        # Key points in the music
        self.cadence_points: Set[int] = set()
        self.climax_point: Optional[int] = None
        self.development_sections: List[Tuple[int, int]] = []
    
    def compose_structure(self, task_description: str) -> Dict[str, Any]:
        """
        Compose the overall structure based on the task.
        
        Args:
            task_description: Description of the coding task
            
        Returns:
            Composition structure
        """
        # Analyze task to determine musical parameters
        complexity = self._analyze_complexity(task_description)
        
        # Choose appropriate mode based on task nature
        if "experimental" in task_description.lower():
            self.mode = MusicalMode.PHRYGIAN
        elif "innovative" in task_description.lower():
            self.mode = MusicalMode.LYDIAN
        elif "functional" in task_description.lower():
            self.mode = MusicalMode.MIXOLYDIAN
        elif "deep" in task_description.lower() or "complex" in task_description.lower():
            self.mode = MusicalMode.AEOLIAN
        
        # Create structure based on form
        if self.form == MusicalForm.SONATA:
            structure = self._create_sonata_form(complexity)
        elif self.form == MusicalForm.FUGUE:
            structure = self._create_fugue_form(complexity)
        elif self.form == MusicalForm.RONDO:
            structure = self._create_rondo_form(complexity)
        elif self.form == MusicalForm.THEME_VARIATIONS:
            structure = self._create_theme_variations_form(complexity)
        else:
            structure = self._create_default_form(complexity)
        
        # Add harmonic progression
        self.harmonic_progression = self._create_harmonic_progression(len(structure['sections']))
        
        return structure
    
    def _analyze_complexity(self, task_description: str) -> float:
        """Analyze task complexity (0.0 to 1.0)."""
        complexity_keywords = [
            'complex', 'advanced', 'sophisticated', 'intricate',
            'multi-threaded', 'distributed', 'scalable', 'enterprise'
        ]
        
        score = 0.0
        for keyword in complexity_keywords:
            if keyword in task_description.lower():
                score += 0.2
        
        return min(1.0, score)
    
    def _create_sonata_form(self, complexity: float) -> Dict[str, Any]:
        """Create sonata form structure: Exposition-Development-Recapitulation."""
        return {
            'form': 'sonata',
            'sections': [
                {
                    'name': 'exposition',
                    'description': 'Introduce main themes and establish structure',
                    'measures': int(8 + complexity * 8),
                    'themes': ['primary_theme', 'secondary_theme'],
                    'can_improvise': False,  # Stay structured in exposition
                    'dynamics': Dynamics.MF
                },
                {
                    'name': 'development',
                    'description': 'Explore and transform themes creatively',
                    'measures': int(12 + complexity * 12),
                    'themes': ['primary_variation', 'secondary_variation', 'combined'],
                    'can_improvise': True,  # Maximum improvisation here
                    'dynamics': Dynamics.F
                },
                {
                    'name': 'recapitulation',
                    'description': 'Return to main themes with resolution',
                    'measures': int(8 + complexity * 8),
                    'themes': ['primary_theme_return', 'secondary_theme_return', 'coda'],
                    'can_improvise': False,  # Return to structure
                    'dynamics': Dynamics.MF
                }
            ],
            'cadence_points': [7, 19, 27],  # Resolution points
            'climax_measure': 15  # Peak of development
        }
    
    def _create_fugue_form(self, complexity: float) -> Dict[str, Any]:
        """Create fugue form: interweaving themes."""
        voices = int(2 + complexity * 2)  # 2-4 voices
        
        return {
            'form': 'fugue',
            'sections': [
                {
                    'name': f'voice_{i+1}_entry',
                    'description': f'Voice {i+1} introduces subject',
                    'measures': 4,
                    'themes': ['subject' if i == 0 else 'answer'],
                    'can_improvise': i > 0,  # First voice strict, others can vary
                    'dynamics': Dynamics.P if i == 0 else Dynamics.MP
                }
                for i in range(voices)
            ] + [
                {
                    'name': 'episode',
                    'description': 'Free development between entries',
                    'measures': int(4 + complexity * 4),
                    'themes': ['episode_material'],
                    'can_improvise': True,
                    'dynamics': Dynamics.MF
                },
                {
                    'name': 'stretto',
                    'description': 'Overlapping entries building to climax',
                    'measures': int(6 + complexity * 4),
                    'themes': ['compressed_subject'],
                    'can_improvise': False,
                    'dynamics': Dynamics.F
                }
            ],
            'voice_interactions': voices,
            'contrapuntal': True
        }
    
    def _create_rondo_form(self, complexity: float) -> Dict[str, Any]:
        """Create rondo form: ABACA pattern."""
        return {
            'form': 'rondo',
            'sections': [
                {'name': 'A1', 'theme': 'main', 'can_improvise': False},
                {'name': 'B', 'theme': 'contrast1', 'can_improvise': True},
                {'name': 'A2', 'theme': 'main_varied', 'can_improvise': True},
                {'name': 'C', 'theme': 'contrast2', 'can_improvise': True},
                {'name': 'A3', 'theme': 'main_final', 'can_improvise': False}
            ],
            'recurring_theme': 'main',
            'variation_level': complexity
        }
    
    def _create_theme_variations_form(self, complexity: float) -> Dict[str, Any]:
        """Create theme and variations form."""
        num_variations = int(3 + complexity * 4)
        
        return {
            'form': 'theme_variations',
            'sections': [
                {
                    'name': 'theme',
                    'description': 'Original theme statement',
                    'can_improvise': False,
                    'dynamics': Dynamics.MP
                }
            ] + [
                {
                    'name': f'variation_{i+1}',
                    'description': f'Variation {i+1}',
                    'can_improvise': True,
                    'improvisation_level': (i + 1) / num_variations,  # Increasing freedom
                    'dynamics': self._get_variation_dynamics(i, num_variations)
                }
                for i in range(num_variations)
            ],
            'theme_transformations': num_variations
        }
    
    def _create_default_form(self, complexity: float) -> Dict[str, Any]:
        """Create a default ternary (ABA) form."""
        return {
            'form': 'ternary',
            'sections': [
                {'name': 'A', 'theme': 'main', 'can_improvise': False},
                {'name': 'B', 'theme': 'contrast', 'can_improvise': True},
                {'name': 'A_prime', 'theme': 'main_return', 'can_improvise': True}
            ]
        }
    
    def _create_harmonic_progression(self, num_sections: int) -> HarmonicProgression:
        """Create harmonic progression for the composition."""
        # Simple I-IV-V-I progression expanded
        basic_progression = ['I', 'ii', 'IV', 'V', 'vi', 'IV', 'V', 'I']
        
        # Extend for longer pieces
        chords = []
        for i in range(num_sections * 4):
            chords.append(basic_progression[i % len(basic_progression)])
        
        # Create tension curve
        tension_curve = []
        for i, chord in enumerate(chords):
            if chord == 'V':
                tension_curve.append(0.8)  # Dominant creates tension
            elif chord == 'I':
                tension_curve.append(0.2)  # Tonic releases tension
            elif chord in ['ii', 'vi']:
                tension_curve.append(0.5)  # Subdominant moderate tension
            else:
                tension_curve.append(0.4)
        
        # Find cadence points (V-I progressions)
        cadence_points = []
        for i in range(len(chords) - 1):
            if chords[i] == 'V' and chords[i + 1] == 'I':
                cadence_points.append(i + 1)
        
        return HarmonicProgression(
            chords=chords,
            tension_curve=tension_curve,
            cadence_points=cadence_points,
            modulation_points=[]  # Could add key changes
        )
    
    def _get_variation_dynamics(self, index: int, total: int) -> Dynamics:
        """Get dynamics for a variation."""
        # Create dynamic arc
        if index < total // 3:
            return Dynamics.P
        elif index < 2 * total // 3:
            return Dynamics.MF
        else:
            return Dynamics.F
    
    def improvise(
        self,
        base_content: str,
        current_position: int,
        context: Dict[str, Any]
    ) -> str:
        """
        Improvise on the base content while maintaining structure.
        
        Args:
            base_content: The base code/content to improvise on
            current_position: Current position in the composition
            context: Additional context for improvisation
            
        Returns:
            Improvised content
        """
        # Check if we're at a critical structural point
        if current_position in self.cadence_points:
            # Don't improvise at cadence points - maintain resolution
            return base_content
        
        # Determine improvisation level based on position
        if self.harmonic_progression:
            tension = self.harmonic_progression.tension_curve[
                current_position % len(self.harmonic_progression.tension_curve)
            ]
        else:
            tension = 0.5
        
        # Higher tension allows more improvisation
        improvisation_amount = tension * self.improvisation_freedom
        
        if random.random() > improvisation_amount:
            return base_content
        
        # Apply improvisation techniques
        techniques = [
            self._ornament,  # Add decorative elements
            self._sequence,  # Repeat pattern at different level
            self._inversion,  # Invert the pattern
            self._augmentation,  # Stretch the pattern
            self._diminution,  # Compress the pattern
            self._substitution  # Substitute with related pattern
        ]
        
        # Choose technique based on musical context
        if tension > 0.7:
            # High tension: use more dramatic techniques
            technique = random.choice([self._inversion, self._substitution, self._sequence])
        elif tension < 0.3:
            # Low tension: use subtle techniques
            technique = random.choice([self._ornament, self._augmentation])
        else:
            # Medium tension: any technique
            technique = random.choice(techniques)
        
        return technique(base_content, context)
    
    def _ornament(self, content: str, context: Dict[str, Any]) -> str:
        """Add ornamental decorations to the content."""
        # Add comments, docstrings, or minor enhancements
        ornaments = [
            "# Enhanced with additional clarity",
            "# Optimized for performance",
            "# Added for better maintainability"
        ]
        
        return f"{content}\n{random.choice(ornaments)}\n{content}"
    
    def _sequence(self, content: str, context: Dict[str, Any]) -> str:
        """Repeat pattern at different level."""
        # Duplicate with variation
        return f"{content}\n# Variation:\n{content.upper()}"
    
    def _inversion(self, content: str, context: Dict[str, Any]) -> str:
        """Invert the pattern."""
        # Reverse logic or structure
        lines = content.split('\n')
        return '\n'.join(reversed(lines))
    
    def _augmentation(self, content: str, context: Dict[str, Any]) -> str:
        """Stretch/expand the pattern."""
        # Add more detail or verbosity
        return f"# Expanded version:\n{content}\n# With additional context\n{content}"
    
    def _diminution(self, content: str, context: Dict[str, Any]) -> str:
        """Compress the pattern."""
        # Simplify or compress
        # In real implementation, this would intelligently compress code
        return content[:len(content)//2] + "..."
    
    def _substitution(self, content: str, context: Dict[str, Any]) -> str:
        """Substitute with related pattern."""
        # Replace with alternative approach
        return f"# Alternative approach:\n{content.replace('def', 'async def')}"
    
    def anticipate_resolution(self, current_position: int) -> Dict[str, Any]:
        """
        Anticipate upcoming resolution points and prepare.
        
        Args:
            current_position: Current position in composition
            
        Returns:
            Information about upcoming musical events
        """
        upcoming = {
            'next_cadence': None,
            'distance_to_cadence': float('inf'),
            'approaching_climax': False,
            'in_development': False,
            'suggested_dynamics': self.current_dynamics
        }
        
        # Find next cadence point
        if self.harmonic_progression:
            for cp in self.harmonic_progression.cadence_points:
                if cp > current_position:
                    upcoming['next_cadence'] = cp
                    upcoming['distance_to_cadence'] = cp - current_position
                    break
        
        # Check if approaching climax
        if self.climax_point:
            distance_to_climax = abs(self.climax_point - current_position)
            upcoming['approaching_climax'] = distance_to_climax < 4
        
        # Check if in development section
        for start, end in self.development_sections:
            if start <= current_position <= end:
                upcoming['in_development'] = True
                upcoming['suggested_dynamics'] = Dynamics.F
                break
        
        # Adjust dynamics based on position
        if upcoming['distance_to_cadence'] < 2:
            # Approaching resolution - gradually decrease dynamics
            upcoming['suggested_dynamics'] = Dynamics.MP
        elif upcoming['approaching_climax']:
            # Building to climax - increase dynamics
            upcoming['suggested_dynamics'] = Dynamics.FF
        
        return upcoming
    
    def create_motif(self, pattern: str, importance: float = 0.5) -> str:
        """
        Create a new motif that can be developed throughout.
        
        Args:
            pattern: The core pattern
            importance: How central this motif is (0.0 to 1.0)
            
        Returns:
            Motif ID
        """
        motif_id = f"motif_{len(self.motifs)}"
        
        motif = Motif(
            motif_id=motif_id,
            pattern=pattern,
            importance=importance
        )
        
        self.motifs[motif_id] = motif
        return motif_id
    
    def develop_motif(self, motif_id: str, transformation_type: str) -> str:
        """
        Develop an existing motif.
        
        Args:
            motif_id: ID of the motif to develop
            transformation_type: Type of transformation to apply
            
        Returns:
            Transformed motif
        """
        if motif_id not in self.motifs:
            return ""
        
        motif = self.motifs[motif_id]
        base_pattern = motif.pattern
        
        transformations = {
            'retrograde': lambda p: ''.join(reversed(p)),
            'inversion': lambda p: p.swapcase(),
            'augmentation': lambda p: ' '.join(p),
            'diminution': lambda p: p.replace(' ', ''),
            'transposition': lambda p: p.upper(),
            'fragmentation': lambda p: p[:len(p)//2]
        }
        
        if transformation_type in transformations:
            transformed = transformations[transformation_type](base_pattern)
            motif.transformations.append(transformed)
            return transformed
        
        return base_pattern
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get metrics about the current performance."""
        return {
            'current_measure': self.current_measure,
            'tension_level': self.tension_level,
            'improvisation_freedom': self.improvisation_freedom,
            'mode': self.mode.value,
            'dynamics': self.current_dynamics.value,
            'motif_count': len(self.motifs),
            'phrase_count': len(self.phrases),
            'history_length': len(self.phrase_history)
        }