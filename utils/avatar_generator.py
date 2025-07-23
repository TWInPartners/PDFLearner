import streamlit as st
import random
import json
from typing import Dict, List

class AvatarGenerator:
    """Generate customizable avatars for user profiles"""
    
    def __init__(self):
        self.avatar_options = {
            'skin_tones': {
                'Light Peach': '#F5DEB3',
                'Medium Beige': '#DEB887', 
                'Warm Tan': '#D2B48C',
                'Golden Brown': '#CD853F',
                'Rich Brown': '#8B4513',
                'Deep Brown': '#654321'
            },
            'hair_colors': {
                'Dark Brown': '#2C1B18',
                'Chestnut': '#8B4513',
                'Golden Blonde': '#D4AF37',
                'Auburn Red': '#B22222',
                'Jet Black': '#000000',
                'Silver Gray': '#696969'
            },
            'hair_styles': {
                'Short & Neat': 'short',
                'Medium Length': 'medium',
                'Long & Flowing': 'long',
                'Curly & Fun': 'curly',
                'Bald & Bold': 'bald',
                'Stylish Ponytail': 'ponytail'
            },
            'eye_colors': {
                'Bright Blue': '#4169E1',
                'Warm Brown': '#8B4513',
                'Forest Green': '#228B22',
                'Emerald Green': '#32CD32',
                'Steel Gray': '#808080',
                'Deep Black': '#000000'
            },
            'accessories': {
                'None': 'none',
                'Classic Glasses': 'glasses',
                'Stylish Hat': 'hat',
                'Pretty Earrings': 'earrings',
                'Elegant Necklace': 'necklace',
                'Cool Cap': 'cap'
            },
            'expressions': {
                'Happy Smile': 'smile',
                'Calm & Neutral': 'neutral',
                'Joyful & Bright': 'happy',
                'Cool & Confident': 'cool',
                'Playful Wink': 'wink',
                'Laughing': 'laugh'
            }
        }
    
    def generate_random_avatar(self) -> Dict:
        """Generate a random avatar configuration"""
        return {
            'skin_tone': random.choice(list(self.avatar_options['skin_tones'].values())),
            'hair_color': random.choice(list(self.avatar_options['hair_colors'].values())),
            'hair_style': random.choice(list(self.avatar_options['hair_styles'].values())),
            'eye_color': random.choice(list(self.avatar_options['eye_colors'].values())),
            'accessory': random.choice(list(self.avatar_options['accessories'].values())),
            'expression': random.choice(list(self.avatar_options['expressions'].values()))
        }
    
    def render_avatar_svg(self, avatar_config: Dict) -> str:
        """Generate SVG representation of avatar"""
        skin_tone = avatar_config.get('skin_tone', '#F5DEB3')
        hair_color = avatar_config.get('hair_color', '#2C1B18')
        hair_style = avatar_config.get('hair_style', 'short')
        eye_color = avatar_config.get('eye_color', '#4169E1')
        accessory = avatar_config.get('accessory', 'none')
        expression = avatar_config.get('expression', 'smile')
        
        # Enhanced SVG structure with better styling
        svg = f'''
        <svg width="120" height="120" viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <radialGradient id="faceGradient" cx="0.5" cy="0.3" r="0.7">
                    <stop offset="0%" style="stop-color:{self._lighten_color(skin_tone)};stop-opacity:1" />
                    <stop offset="100%" style="stop-color:{skin_tone};stop-opacity:1" />
                </radialGradient>
                <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
                    <feDropShadow dx="2" dy="3" stdDeviation="3" flood-color="rgba(0,0,0,0.2)"/>
                </filter>
            </defs>
            
            <!-- Face with gradient -->
            <circle cx="60" cy="65" r="35" fill="url(#faceGradient)" stroke="#DDD" stroke-width="1.5" filter="url(#shadow)"/>
            
            <!-- Hair -->
            {self._get_hair_svg(hair_style, hair_color)}
            
            <!-- Eyes -->
            <circle cx="50" cy="58" r="4" fill="white" stroke="#CCC" stroke-width="0.5"/>
            <circle cx="70" cy="58" r="4" fill="white" stroke="#CCC" stroke-width="0.5"/>
            <circle cx="50" cy="58" r="2.5" fill="{eye_color}"/>
            <circle cx="70" cy="58" r="2.5" fill="{eye_color}"/>
            <circle cx="51" cy="57" r="0.8" fill="white" opacity="0.8"/>
            <circle cx="71" cy="57" r="0.8" fill="white" opacity="0.8"/>
            
            <!-- Eyebrows -->
            <path d="M 46 54 Q 50 52 54 54" stroke="{self._darken_color(skin_tone)}" stroke-width="1.5" fill="none"/>
            <path d="M 66 54 Q 70 52 74 54" stroke="{self._darken_color(skin_tone)}" stroke-width="1.5" fill="none"/>
            
            <!-- Nose -->
            <ellipse cx="60" cy="65" rx="1.5" ry="2.5" fill="{self._darken_color(skin_tone)}" opacity="0.6"/>
            
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
    
    def _lighten_color(self, color: str) -> str:
        """Lighten a hex color for highlights"""
        if color.startswith('#'):
            color = color[1:]
        
        # Convert hex to RGB
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        
        # Lighten by 15%
        r = min(255, int(r * 1.15))
        g = min(255, int(g * 1.15))
        b = min(255, int(b * 1.15))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def render_avatar_customizer(self, initial_config: Dict = None) -> Dict:
        """Render avatar customization interface with live preview"""
        if initial_config is None:
            initial_config = self.generate_random_avatar()
        
        st.markdown("### 🎨 Customize Your Avatar")
        
        # Use a unique key for this customizer instance
        customizer_key = "avatar_customizer"
        
        # Initialize or get current configuration
        if f'{customizer_key}_config' not in st.session_state:
            st.session_state[f'{customizer_key}_config'] = initial_config.copy()
        
        current_config = st.session_state[f'{customizer_key}_config']
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Live avatar preview
            avatar_svg = self.render_avatar_svg(current_config)
            st.markdown(f"""
            <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 15px; margin-bottom: 1rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                {avatar_svg}
                <p style="margin-top: 1rem; font-weight: bold; color: #4a5568;">Your Avatar Preview</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🎲 Random Avatar", use_container_width=True, key=f"{customizer_key}_random"):
                new_random = self.generate_random_avatar()
                st.session_state[f'{customizer_key}_config'] = new_random
                st.rerun()
        
        with col2:
            # Helper function to get current selection index
            def get_selection_index(option_dict, current_value):
                for i, (name, value) in enumerate(option_dict.items()):
                    if value == current_value:
                        return i
                return 0
            
            # Track if any changes were made
            config_changed = False
            new_config = current_config.copy()
            
            # Skin tone
            skin_tone_names = list(self.avatar_options['skin_tones'].keys())
            skin_tone_index = get_selection_index(self.avatar_options['skin_tones'], current_config.get('skin_tone'))
            selected_skin_name = st.selectbox(
                "🎨 Skin Tone", 
                skin_tone_names, 
                index=skin_tone_index, 
                key=f"{customizer_key}_skin"
            )
            new_skin_tone = self.avatar_options['skin_tones'][selected_skin_name]
            if new_skin_tone != current_config.get('skin_tone'):
                new_config['skin_tone'] = new_skin_tone
                config_changed = True
            
            # Hair
            col_hair1, col_hair2 = st.columns(2)
            with col_hair1:
                hair_style_names = list(self.avatar_options['hair_styles'].keys())
                hair_style_index = get_selection_index(self.avatar_options['hair_styles'], current_config.get('hair_style'))
                selected_hair_style = st.selectbox(
                    "💇 Hair Style", 
                    hair_style_names, 
                    index=hair_style_index, 
                    key=f"{customizer_key}_hair_style"
                )
                new_hair_style = self.avatar_options['hair_styles'][selected_hair_style]
                if new_hair_style != current_config.get('hair_style'):
                    new_config['hair_style'] = new_hair_style
                    config_changed = True
                
            with col_hair2:
                hair_color_names = list(self.avatar_options['hair_colors'].keys())
                hair_color_index = get_selection_index(self.avatar_options['hair_colors'], current_config.get('hair_color'))
                selected_hair_color = st.selectbox(
                    "🎨 Hair Color", 
                    hair_color_names, 
                    index=hair_color_index, 
                    key=f"{customizer_key}_hair_color"
                )
                new_hair_color = self.avatar_options['hair_colors'][selected_hair_color]
                if new_hair_color != current_config.get('hair_color'):
                    new_config['hair_color'] = new_hair_color
                    config_changed = True
            
            # Eyes
            eye_color_names = list(self.avatar_options['eye_colors'].keys())
            eye_color_index = get_selection_index(self.avatar_options['eye_colors'], current_config.get('eye_color'))
            selected_eye_color = st.selectbox(
                "👁️ Eye Color", 
                eye_color_names, 
                index=eye_color_index, 
                key=f"{customizer_key}_eyes"
            )
            new_eye_color = self.avatar_options['eye_colors'][selected_eye_color]
            if new_eye_color != current_config.get('eye_color'):
                new_config['eye_color'] = new_eye_color
                config_changed = True
            
            # Expression and accessories
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                expression_names = list(self.avatar_options['expressions'].keys())
                expression_index = get_selection_index(self.avatar_options['expressions'], current_config.get('expression'))
                selected_expression = st.selectbox(
                    "😊 Expression", 
                    expression_names, 
                    index=expression_index, 
                    key=f"{customizer_key}_expression"
                )
                new_expression = self.avatar_options['expressions'][selected_expression]
                if new_expression != current_config.get('expression'):
                    new_config['expression'] = new_expression
                    config_changed = True
                
            with col_exp2:
                accessory_names = list(self.avatar_options['accessories'].keys())
                accessory_index = get_selection_index(self.avatar_options['accessories'], current_config.get('accessory'))
                selected_accessory = st.selectbox(
                    "✨ Accessory", 
                    accessory_names, 
                    index=accessory_index, 
                    key=f"{customizer_key}_accessory"
                )
                new_accessory = self.avatar_options['accessories'][selected_accessory]
                if new_accessory != current_config.get('accessory'):
                    new_config['accessory'] = new_accessory
                    config_changed = True
            
            # Update configuration if changed
            if config_changed:
                st.session_state[f'{customizer_key}_config'] = new_config
                st.rerun()
        
        return st.session_state[f'{customizer_key}_config']
    
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