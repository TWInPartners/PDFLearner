import streamlit as st
import random
import base64
from typing import Dict, Any

class FixedAvatarGenerator:
    """Simplified avatar generator with real-time updates and robust error handling"""
    
    def __init__(self):
        self.avatar_options = {
            'skin_tones': {
                'Light': '#FDBCB4',
                'Fair': '#F1C27D', 
                'Medium': '#E0AC69',
                'Olive': '#C68642',
                'Dark': '#8D5524',
                'Deep': '#654321'
            },
            'hair_styles': {
                'Short': 'short',
                'Medium': 'medium',
                'Long': 'long',
                'Curly': 'curly',
                'Wavy': 'wavy',
                'Straight': 'straight'
            },
            'hair_colors': {
                'Black': '#000000',
                'Brown': '#8B4513',
                'Blonde': '#DAA520',
                'Red': '#CD853F',
                'Auburn': '#A0522D',
                'Gray': '#808080'
            },
            'eye_colors': {
                'Brown': '#8B4513',
                'Blue': '#4169E1',
                'Green': '#228B22',
                'Hazel': '#DAA520',
                'Gray': '#708090',
                'Amber': '#FFBF00'
            },
            'expressions': {
                'Happy': 'smile',
                'Neutral': 'neutral',
                'Excited': 'excited',
                'Confident': 'confident',
                'Friendly': 'friendly',
                'Thoughtful': 'thoughtful'
            },
            'accessories': {
                'None': 'none',
                'Glasses': 'glasses',
                'Hat': 'hat',
                'Headband': 'headband',
                'Earrings': 'earrings',
                'Necklace': 'necklace'
            }
        }
    
    def generate_random_avatar(self) -> Dict[str, str]:
        """Generate a random avatar configuration safely"""
        try:
            return {
                'skin_tone': random.choice(list(self.avatar_options['skin_tones'].values())),
                'hair_style': random.choice(list(self.avatar_options['hair_styles'].values())),
                'hair_color': random.choice(list(self.avatar_options['hair_colors'].values())),
                'eye_color': random.choice(list(self.avatar_options['eye_colors'].values())),
                'expression': random.choice(list(self.avatar_options['expressions'].values())),
                'accessory': random.choice(list(self.avatar_options['accessories'].values()))
            }
        except Exception:
            # Safe fallback
            return {
                'skin_tone': '#FDBCB4',
                'hair_style': 'short',
                'hair_color': '#8B4513',
                'eye_color': '#4169E1',
                'expression': 'smile',
                'accessory': 'none'
            }
    
    def render_avatar_svg(self, config: Dict[str, str]) -> str:
        """Render avatar as SVG with safe defaults"""
        # Safe config with defaults
        safe_config = {
            'skin_tone': config.get('skin_tone', '#FDBCB4'),
            'hair_style': config.get('hair_style', 'short'),
            'hair_color': config.get('hair_color', '#8B4513'),
            'eye_color': config.get('eye_color', '#4169E1'),
            'expression': config.get('expression', 'smile'),
            'accessory': config.get('accessory', 'none')
        }
        
        # Create SVG with safe values
        svg = f"""
        <svg width="150" height="150" viewBox="0 0 150 150" xmlns="http://www.w3.org/2000/svg">
            <!-- Background circle -->
            <circle cx="75" cy="75" r="70" fill="{safe_config['skin_tone']}" stroke="#ccc" stroke-width="2"/>
            
            <!-- Hair -->
            <path d="M20 60 Q75 10 130 60 Q130 40 75 30 Q20 40 20 60" fill="{safe_config['hair_color']}"/>
            
            <!-- Eyes -->
            <circle cx="55" cy="65" r="8" fill="white"/>
            <circle cx="95" cy="65" r="8" fill="white"/>
            <circle cx="55" cy="65" r="5" fill="{safe_config['eye_color']}"/>
            <circle cx="95" cy="65" r="5" fill="{safe_config['eye_color']}"/>
            
            <!-- Nose -->
            <circle cx="75" cy="80" r="2" fill="#FFB6C1"/>
            
            <!-- Mouth based on expression -->
            <path d="M65 95 Q75 105 85 95" stroke="#FF69B4" stroke-width="3" fill="none"/>
            
            <!-- Accessory based on type -->
            {self._render_accessory(safe_config['accessory'])}
        </svg>
        """
        return svg
    
    def _render_accessory(self, accessory_type: str) -> str:
        """Render accessory SVG element"""
        if accessory_type == 'glasses':
            return '<rect x="45" y="60" width="20" height="15" fill="none" stroke="#333" stroke-width="2" rx="8"/><rect x="85" y="60" width="20" height="15" fill="none" stroke="#333" stroke-width="2" rx="8"/><line x1="65" y1="67" x2="85" y2="67" stroke="#333" stroke-width="2"/>'
        elif accessory_type == 'hat':
            return '<rect x="30" y="25" width="90" height="15" fill="#4169E1" rx="5"/><rect x="25" y="35" width="100" height="8" fill="#4169E1"/>'
        elif accessory_type == 'headband':
            return '<rect x="35" y="45" width="80" height="6" fill="#FF69B4" rx="3"/>'
        else:
            return ''
    
    def render_avatar_customizer_with_live_update(self, current_config: Dict[str, str]) -> Dict[str, str]:
        """Render avatar customizer with real-time updates"""
        
        # Initialize session state for real-time updates
        if 'live_avatar_config' not in st.session_state:
            st.session_state.live_avatar_config = current_config.copy()
        
        st.markdown("### 🎨 Avatar Customizer")
        
        # Create two columns for customization and preview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### Customize Your Look")
            
            # Helper function to get current option index
            def get_option_index(options_dict, current_value):
                try:
                    return list(options_dict.values()).index(current_value)
                except (ValueError, KeyError):
                    return 0
            
            # Skin tone
            skin_options = list(self.avatar_options['skin_tones'].keys())
            skin_index = get_option_index(self.avatar_options['skin_tones'], current_config.get('skin_tone'))
            selected_skin = st.selectbox(
                "🎨 Skin Tone", 
                skin_options, 
                index=skin_index,
                key="avatar_skin"
            )
            
            # Hair
            col_hair1, col_hair2 = st.columns(2)
            with col_hair1:
                hair_style_options = list(self.avatar_options['hair_styles'].keys())
                hair_style_index = get_option_index(self.avatar_options['hair_styles'], current_config.get('hair_style'))
                selected_hair_style = st.selectbox(
                    "💇 Hair Style", 
                    hair_style_options, 
                    index=hair_style_index,
                    key="avatar_hair_style"
                )
            
            with col_hair2:
                hair_color_options = list(self.avatar_options['hair_colors'].keys())
                hair_color_index = get_option_index(self.avatar_options['hair_colors'], current_config.get('hair_color'))
                selected_hair_color = st.selectbox(
                    "🎨 Hair Color", 
                    hair_color_options, 
                    index=hair_color_index,
                    key="avatar_hair_color"
                )
            
            # Eyes
            eye_color_options = list(self.avatar_options['eye_colors'].keys())
            eye_color_index = get_option_index(self.avatar_options['eye_colors'], current_config.get('eye_color'))
            selected_eye_color = st.selectbox(
                "👁️ Eye Color", 
                eye_color_options, 
                index=eye_color_index,
                key="avatar_eyes"
            )
            
            # Expression and accessories
            col_exp1, col_exp2 = st.columns(2)
            with col_exp1:
                expression_options = list(self.avatar_options['expressions'].keys())
                expression_index = get_option_index(self.avatar_options['expressions'], current_config.get('expression'))
                selected_expression = st.selectbox(
                    "😊 Expression", 
                    expression_options, 
                    index=expression_index,
                    key="avatar_expression"
                )
            
            with col_exp2:
                accessory_options = list(self.avatar_options['accessories'].keys())
                accessory_index = get_option_index(self.avatar_options['accessories'], current_config.get('accessory'))
                selected_accessory = st.selectbox(
                    "✨ Accessory", 
                    accessory_options, 
                    index=accessory_index,
                    key="avatar_accessory"
                )
        
        # Build the current configuration from selections
        new_config = {
            'skin_tone': self.avatar_options['skin_tones'][selected_skin],
            'hair_style': self.avatar_options['hair_styles'][selected_hair_style],
            'hair_color': self.avatar_options['hair_colors'][selected_hair_color],
            'eye_color': self.avatar_options['eye_colors'][selected_eye_color],
            'expression': self.avatar_options['expressions'][selected_expression],
            'accessory': self.avatar_options['accessories'][selected_accessory]
        }
        
        # Update session state with live changes
        st.session_state.live_avatar_config = new_config
        
        with col2:
            st.markdown("#### 👁️ Live Preview")
            
            # Display live avatar preview
            avatar_svg = self.render_avatar_svg(new_config)
            
            # Convert to data URL for display
            svg_bytes = avatar_svg.encode('utf-8')
            svg_b64 = base64.b64encode(svg_bytes).decode('utf-8')
            svg_data_url = f"data:image/svg+xml;base64,{svg_b64}"
            
            st.image(svg_data_url, width=150)
            st.caption("Your Avatar Preview")
            
            # Random avatar button
            if st.button("🎲 Generate Random", use_container_width=True):
                random_config = self.generate_random_avatar()
                st.session_state.live_avatar_config = random_config
                st.rerun()
        
        return new_config