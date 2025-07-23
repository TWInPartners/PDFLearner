import streamlit as st
import random
import json
from typing import Dict, List

class AvatarGenerator:
    """Generate customizable avatars for user profiles"""
    
    def __init__(self):
        self.avatar_options = {
            'skin_tones': ['#F5DEB3', '#DEB887', '#D2B48C', '#CD853F', '#8B4513', '#654321'],
            'hair_colors': ['#2C1B18', '#8B4513', '#D4AF37', '#B22222', '#000000', '#696969'],
            'hair_styles': ['short', 'medium', 'long', 'curly', 'bald', 'ponytail'],
            'eye_colors': ['#4169E1', '#8B4513', '#228B22', '#32CD32', '#808080', '#000000'],
            'accessories': ['none', 'glasses', 'hat', 'earrings', 'necklace', 'cap'],
            'expressions': ['smile', 'neutral', 'happy', 'cool', 'wink', 'laugh']
        }
    
    def generate_random_avatar(self) -> Dict:
        """Generate a random avatar configuration"""
        return {
            'skin_tone': random.choice(self.avatar_options['skin_tones']),
            'hair_color': random.choice(self.avatar_options['hair_colors']),
            'hair_style': random.choice(self.avatar_options['hair_styles']),
            'eye_color': random.choice(self.avatar_options['eye_colors']),
            'accessory': random.choice(self.avatar_options['accessories']),
            'expression': random.choice(self.avatar_options['expressions'])
        }
    
    def render_avatar_svg(self, avatar_config: Dict) -> str:
        """Generate SVG representation of avatar"""
        skin_tone = avatar_config.get('skin_tone', '#F5DEB3')
        hair_color = avatar_config.get('hair_color', '#2C1B18')
        hair_style = avatar_config.get('hair_style', 'short')
        eye_color = avatar_config.get('eye_color', '#4169E1')
        accessory = avatar_config.get('accessory', 'none')
        expression = avatar_config.get('expression', 'smile')
        
        # Base SVG structure
        svg = f'''
        <svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
            <!-- Face -->
            <circle cx="60" cy="65" r="35" fill="{skin_tone}" stroke="#DDD" stroke-width="2"/>
            
            <!-- Hair -->
            {self._get_hair_svg(hair_style, hair_color)}
            
            <!-- Eyes -->
            <circle cx="50" cy="58" r="4" fill="white"/>
            <circle cx="70" cy="58" r="4" fill="white"/>
            <circle cx="50" cy="58" r="2" fill="{eye_color}"/>
            <circle cx="70" cy="58" r="2" fill="{eye_color}"/>
            
            <!-- Nose -->
            <ellipse cx="60" cy="65" rx="1.5" ry="2" fill="{self._darken_color(skin_tone)}"/>
            
            <!-- Mouth -->
            {self._get_mouth_svg(expression)}
            
            <!-- Accessories -->
            {self._get_accessory_svg(accessory)}
        </svg>
        '''
        
        return svg
    
    def _get_hair_svg(self, style: str, color: str) -> str:
        """Generate hair SVG based on style"""
        if style == 'bald':
            return ''
        elif style == 'short':
            return f'<path d="M 30 45 Q 60 25 90 45 Q 85 35 60 30 Q 35 35 30 45" fill="{color}"/>'
        elif style == 'medium':
            return f'<path d="M 25 45 Q 60 20 95 45 Q 95 40 90 35 Q 60 25 30 35 Q 25 40 25 45" fill="{color}"/>'
        elif style == 'long':
            return f'<path d="M 20 45 Q 60 15 100 45 Q 100 55 95 65 Q 60 20 25 65 Q 20 55 20 45" fill="{color}"/>'
        elif style == 'curly':
            return f'''
            <circle cx="35" cy="40" r="8" fill="{color}"/>
            <circle cx="50" cy="35" r="9" fill="{color}"/>
            <circle cx="65" cy="35" r="9" fill="{color}"/>
            <circle cx="80" cy="40" r="8" fill="{color}"/>
            '''
        elif style == 'ponytail':
            return f'''
            <path d="M 30 45 Q 60 25 90 45 Q 85 35 60 30 Q 35 35 30 45" fill="{color}"/>
            <ellipse cx="85" cy="55" rx="6" ry="15" fill="{color}"/>
            '''
        else:
            return f'<path d="M 30 45 Q 60 25 90 45 Q 85 35 60 30 Q 35 35 30 45" fill="{color}"/>'
    
    def _get_mouth_svg(self, expression: str) -> str:
        """Generate mouth SVG based on expression"""
        if expression == 'smile':
            return '<path d="M 50 75 Q 60 80 70 75" stroke="#000" stroke-width="2" fill="none"/>'
        elif expression == 'happy':
            return '<path d="M 50 75 Q 60 82 70 75" stroke="#000" stroke-width="2" fill="none"/>'
        elif expression == 'neutral':
            return '<line x1="52" y1="75" x2="68" y2="75" stroke="#000" stroke-width="2"/>'
        elif expression == 'cool':
            return '<path d="M 52 77 Q 60 75 68 77" stroke="#000" stroke-width="2" fill="none"/>'
        elif expression == 'wink':
            return '''
            <path d="M 50 75 Q 60 80 70 75" stroke="#000" stroke-width="2" fill="none"/>
            <path d="M 47 56 L 53 58" stroke="#000" stroke-width="2"/>
            '''
        elif expression == 'laugh':
            return '''
            <ellipse cx="60" cy="78" rx="8" ry="4" fill="#000"/>
            <ellipse cx="60" cy="78" rx="6" ry="2" fill="#FFF"/>
            '''
        else:
            return '<path d="M 50 75 Q 60 80 70 75" stroke="#000" stroke-width="2" fill="none"/>'
    
    def _get_accessory_svg(self, accessory: str) -> str:
        """Generate accessory SVG"""
        if accessory == 'glasses':
            return '''
            <circle cx="50" cy="58" r="8" fill="none" stroke="#000" stroke-width="2"/>
            <circle cx="70" cy="58" r="8" fill="none" stroke="#000" stroke-width="2"/>
            <line x1="58" y1="58" x2="62" y2="58" stroke="#000" stroke-width="2"/>
            '''
        elif accessory == 'hat':
            return '<rect x="35" y="30" width="50" height="8" fill="#4169E1" rx="4"/>'
        elif accessory == 'cap':
            return '''
            <path d="M 30 40 Q 60 25 90 40 L 95 35 Q 60 20 25 35 Z" fill="#FF4500"/>
            <ellipse cx="95" cy="42" rx="8" ry="3" fill="#FF4500"/>
            '''
        elif accessory == 'earrings':
            return '''
            <circle cx="35" cy="68" r="2" fill="#FFD700"/>
            <circle cx="85" cy="68" r="2" fill="#FFD700"/>
            '''
        elif accessory == 'necklace':
            return '''
            <ellipse cx="60" cy="85" rx="15" ry="5" fill="none" stroke="#FFD700" stroke-width="2"/>
            <circle cx="60" cy="90" r="3" fill="#FFD700"/>
            '''
        else:
            return ''
    
    def _darken_color(self, color: str) -> str:
        """Darken a hex color for shading"""
        if color.startswith('#'):
            color = color[1:]
        
        # Convert hex to RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        # Darken by 20%
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def render_avatar_customizer(self, initial_config: Dict = None) -> Dict:
        """Render avatar customization interface"""
        if initial_config is None:
            initial_config = self.generate_random_avatar()
        
        st.markdown("### 🎨 Customize Your Avatar")
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Avatar preview
            avatar_svg = self.render_avatar_svg(initial_config)
            st.markdown(f"""
            <div style="text-align: center; padding: 1rem;">
                {avatar_svg}
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎲 Random Avatar", use_container_width=True):
                return self.generate_random_avatar()
        
        with col2:
            # Customization options
            config = {}
            
            # Skin tone
            config['skin_tone'] = st.selectbox(
                "Skin Tone",
                self.avatar_options['skin_tones'],
                index=self.avatar_options['skin_tones'].index(initial_config.get('skin_tone', self.avatar_options['skin_tones'][0]))
            )
            
            # Hair
            col_hair1, col_hair2 = st.columns(2)
            with col_hair1:
                config['hair_style'] = st.selectbox(
                    "Hair Style",
                    self.avatar_options['hair_styles'],
                    index=self.avatar_options['hair_styles'].index(initial_config.get('hair_style', 'short'))
                )
            with col_hair2:
                config['hair_color'] = st.selectbox(
                    "Hair Color",
                    self.avatar_options['hair_colors'],
                    index=self.avatar_options['hair_colors'].index(initial_config.get('hair_color', self.avatar_options['hair_colors'][0]))
                )
            
            # Eyes
            config['eye_color'] = st.selectbox(
                "Eye Color",
                self.avatar_options['eye_colors'],
                index=self.avatar_options['eye_colors'].index(initial_config.get('eye_color', self.avatar_options['eye_colors'][0]))
            )
            
            # Expression and accessories
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                config['expression'] = st.selectbox(
                    "Expression",
                    self.avatar_options['expressions'],
                    index=self.avatar_options['expressions'].index(initial_config.get('expression', 'smile'))
                )
            with col_exp2:
                config['accessory'] = st.selectbox(
                    "Accessory",
                    self.avatar_options['accessories'],
                    index=self.avatar_options['accessories'].index(initial_config.get('accessory', 'none'))
                )
        
        return config
    
    def get_avatar_achievements(self, user_stats: Dict) -> List[str]:
        """Get available avatar achievements based on user stats"""
        achievements = []
        
        level = user_stats.get('level', 1)
        streak = user_stats.get('current_streak', 0)
        badges = user_stats.get('badges_count', 0)
        
        # Level-based unlocks
        if level >= 5:
            achievements.append("🎩 Fancy Hat (Level 5+)")
        if level >= 10:
            achievements.append("👑 Crown (Level 10+)")
        if level >= 15:
            achievements.append("🕶️ Cool Sunglasses (Level 15+)")
        
        # Streak-based unlocks
        if streak >= 7:
            achievements.append("🔥 Fire Hair (7-day streak)")
        if streak >= 30:
            achievements.append("⚡ Lightning Hair (30-day streak)")
        
        # Badge-based unlocks
        if badges >= 5:
            achievements.append("💎 Diamond Earrings (5+ badges)")
        if badges >= 10:
            achievements.append("🌟 Star Crown (10+ badges)")
        
        return achievements