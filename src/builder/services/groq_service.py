# builder/services/ai_service.py - Complete Enhanced Version

import json
import os
import re
import random
import base64
from openai import OpenAI
from django.conf import settings

# ============================================
# SVG BACKGROUND PATTERNS - FOR HERO SECTIONS
# ============================================

SVG_PATTERNS = {
    'geometric': """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" opacity="0.4">
  <defs>
    <linearGradient id="g1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:%COLOR1%;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:%COLOR2%;stop-opacity:0.1" />
    </linearGradient>
  </defs>
  <rect width="800" height="800" fill="url(#g1)" />
  <polygon points="400,50 500,200 700,200 550,300 600,500 400,400 200,500 250,300 100,200 300,200" fill="%COLOR1%" opacity="0.15" />
  <circle cx="600" cy="600" r="150" fill="%COLOR2%" opacity="0.08" />
  <circle cx="200" cy="150" r="100" fill="%COLOR2%" opacity="0.06" />
  <polygon points="400,100 450,200 550,200 470,250 500,350 400,300 300,350 330,250 250,200 350,200" fill="%COLOR1%" opacity="0.1" />
</svg>
""",
    'waves': """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320" preserveAspectRatio="none" style="height:100%;width:100%;">
  <defs>
    <linearGradient id="wg1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:%COLOR1%;stop-opacity:0.25" />
      <stop offset="50%" style="stop-color:%COLOR2%;stop-opacity:0.15" />
      <stop offset="100%" style="stop-color:%COLOR1%;stop-opacity:0.25" />
    </linearGradient>
  </defs>
  <path fill="url(#wg1)" d="M0,192L48,176C96,160,192,128,288,133.3C384,139,480,181,576,181.3C672,181,768,139,864,122.7C960,107,1056,117,1152,138.7C1248,160,1344,192,1392,208L1440,224L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"/>
  <path fill="%COLOR1%" opacity="0.1" d="M0,256L48,245.3C96,235,192,213,288,213.3C384,213,480,235,576,245.3C672,256,768,256,864,245.3C960,235,1056,213,1152,213.3C1248,213,1344,235,1392,245.3L1440,256L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z"/>
</svg>
""",
    'dots': """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" opacity="0.3">
  <defs>
    <pattern id="dots" x="0" y="0" width="40" height="40" patternUnits="userSpaceOnUse">
      <circle cx="20" cy="20" r="4" fill="%COLOR1%" opacity="0.4" />
      <circle cx="0" cy="0" r="3" fill="%COLOR2%" opacity="0.3" />
      <circle cx="40" cy="0" r="2" fill="%COLOR1%" opacity="0.2" />
      <circle cx="0" cy="40" r="2" fill="%COLOR2%" opacity="0.2" />
      <circle cx="40" cy="40" r="3" fill="%COLOR1%" opacity="0.3" />
    </pattern>
  </defs>
  <rect width="800" height="800" fill="url(#dots)" />
</svg>
""",
    'gradient_mesh': """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" opacity="0.5">
  <defs>
    <radialGradient id="rg1" cx="20%" cy="30%" r="70%">
      <stop offset="0%" style="stop-color:%COLOR1%;stop-opacity:0.3" />
      <stop offset="50%" style="stop-color:%COLOR2%;stop-opacity:0.15" />
      <stop offset="100%" style="stop-color:%COLOR1%;stop-opacity:0" />
    </radialGradient>
    <radialGradient id="rg2" cx="80%" cy="70%" r="60%">
      <stop offset="0%" style="stop-color:%COLOR2%;stop-opacity:0.2" />
      <stop offset="100%" style="stop-color:%COLOR1%;stop-opacity:0" />
    </radialGradient>
  </defs>
  <rect width="800" height="800" fill="%BGCOLOR%" />
  <rect width="800" height="800" fill="url(#rg1)" />
  <rect width="800" height="800" fill="url(#rg2)" />
  <ellipse cx="300" cy="200" rx="250" ry="200" fill="%COLOR1%" opacity="0.08" />
  <ellipse cx="550" cy="500" rx="300" ry="250" fill="%COLOR2%" opacity="0.06" />
</svg>
""",
    'abstract_circles': """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" opacity="0.35">
  <defs>
    <linearGradient id="lc1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:%COLOR1%;stop-opacity:0.3" />
      <stop offset="100%" style="stop-color:%COLOR2%;stop-opacity:0.1" />
    </linearGradient>
  </defs>
  <rect width="800" height="800" fill="%BGCOLOR%" />
  <circle cx="200" cy="200" r="180" fill="url(#lc1)" />
  <circle cx="600" cy="600" r="250" fill="url(#lc1)" opacity="0.5" />
  <circle cx="400" cy="400" r="120" fill="%COLOR1%" opacity="0.12" />
  <circle cx="150" cy="650" r="100" fill="%COLOR2%" opacity="0.1" />
  <circle cx="650" cy="150" r="80" fill="%COLOR1%" opacity="0.08" />
</svg>
""",
    'mountain_peaks': """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320" preserveAspectRatio="none" style="height:100%;width:100%;">
  <defs>
    <linearGradient id="mg1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:%COLOR1%;stop-opacity:0.2" />
      <stop offset="100%" style="stop-color:%COLOR2%;stop-opacity:0.1" />
    </linearGradient>
  </defs>
  <path fill="url(#mg1)" d="M0,160L60,149.3C120,139,240,117,360,122.7C480,128,600,160,720,181.3C840,203,960,213,1080,197.3C1200,181,1320,139,1380,117.3L1440,96L1440,320L1380,320C1320,320,1200,320,1080,320C960,320,840,320,720,320C600,320,480,320,360,320C240,320,120,320,60,320L0,320Z"/>
  <path fill="%COLOR1%" opacity="0.15" d="M0,224L60,213.3C120,203,240,181,360,186.7C480,192,600,224,720,245.3C840,267,960,277,1080,261.3C1200,245,1320,203,1380,181.3L1440,160L1440,320L1380,320C1320,320,1200,320,1080,320C960,320,840,320,720,320C600,320,480,320,360,320C240,320,120,320,60,320L0,320Z"/>
</svg>
""",
    'particle_grid': """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" opacity="0.25">
  <defs>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <rect width="800" height="800" fill="%BGCOLOR%" />
  <g filter="url(#glow)">
    <circle cx="100" cy="100" r="4" fill="%COLOR1%" opacity="0.6" />
    <circle cx="200" cy="50" r="3" fill="%COLOR2%" opacity="0.5" />
    <circle cx="300" cy="150" r="5" fill="%COLOR1%" opacity="0.4" />
    <circle cx="400" cy="80" r="3" fill="%COLOR2%" opacity="0.6" />
    <circle cx="500" cy="120" r="4" fill="%COLOR1%" opacity="0.5" />
    <circle cx="600" cy="60" r="3" fill="%COLOR2%" opacity="0.4" />
    <circle cx="700" cy="140" r="5" fill="%COLOR1%" opacity="0.5" />
    <circle cx="150" cy="250" r="3" fill="%COLOR2%" opacity="0.5" />
    <circle cx="250" cy="300" r="4" fill="%COLOR1%" opacity="0.6" />
    <circle cx="350" cy="220" r="3" fill="%COLOR2%" opacity="0.4" />
    <circle cx="450" cy="280" r="5" fill="%COLOR1%" opacity="0.5" />
    <circle cx="550" cy="240" r="3" fill="%COLOR2%" opacity="0.6" />
    <circle cx="650" cy="310" r="4" fill="%COLOR1%" opacity="0.4" />
    <circle cx="750" cy="260" r="3" fill="%COLOR2%" opacity="0.5" />
    <circle cx="100" cy="400" r="4" fill="%COLOR1%" opacity="0.4" />
    <circle cx="200" cy="450" r="5" fill="%COLOR2%" opacity="0.5" />
    <circle cx="300" cy="380" r="3" fill="%COLOR1%" opacity="0.6" />
    <circle cx="400" cy="420" r="4" fill="%COLOR2%" opacity="0.4" />
    <circle cx="500" cy="390" r="3" fill="%COLOR1%" opacity="0.5" />
    <circle cx="600" cy="460" r="5" fill="%COLOR2%" opacity="0.5" />
    <circle cx="700" cy="410" r="3" fill="%COLOR1%" opacity="0.4" />
    <circle cx="100" cy="550" r="3" fill="%COLOR2%" opacity="0.5" />
    <circle cx="200" cy="600" r="4" fill="%COLOR1%" opacity="0.6" />
    <circle cx="300" cy="530" r="5" fill="%COLOR2%" opacity="0.4" />
    <circle cx="400" cy="580" r="3" fill="%COLOR1%" opacity="0.5" />
    <circle cx="500" cy="550" r="4" fill="%COLOR2%" opacity="0.5" />
    <circle cx="600" cy="620" r="3" fill="%COLOR1%" opacity="0.4" />
    <circle cx="700" cy="570" r="5" fill="%COLOR2%" opacity="0.6" />
    <circle cx="150" cy="700" r="3" fill="%COLOR1%" opacity="0.5" />
    <circle cx="350" cy="720" r="4" fill="%COLOR2%" opacity="0.4" />
    <circle cx="550" cy="710" r="3" fill="%COLOR1%" opacity="0.5" />
    <circle cx="750" cy="690" r="4" fill="%COLOR2%" opacity="0.6" />
  </g>
</svg>
"""
}

# ============================================
# TEMPLATE STRUCTURE - WITH FULL CONTEXT
# ============================================

TEMPLATE_STRUCTURE = {
    'name': 'modernecommerce33',
    'description': 'A modern e-commerce template with a clean, minimalist aesthetic.',
    'container': {
        'selector': 'body',
        'bg': '#fcf8f4',
        'font_family': "'Plus Jakarta Sans', sans-serif",
        'color': '#232b28',
        'overflow_x': 'hidden',
        'line_height': '1.6'
    },
    'sections': {
        # ============================================
        # NAVIGATION (Sections 1-10)
        # ============================================
        'nav': {
            'ids': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
            'container': '.organic-nav',
            'max_width': '1400px',
            'margin': '0 auto',
            'padding': '30px 4%',
            'display': 'flex',
            'justify_content': 'space-between',
            'align_items': 'center',
            'position': 'sticky',
            'top': '0',
            'z_index': '1000',
            'bg': 'rgba(252, 248, 244, 0.95)',
            'backdrop_filter': 'blur(12px)',
            'border_bottom': '1px solid rgba(35, 43, 40, 0.06)',
            'children': {
                '.brand-crest': {
                    'selector': '.brand-crest',
                    'font_family': "'Italiana', serif",
                    'font_size': '2rem',
                    'font_weight': '400',
                    'text_transform': 'uppercase',
                    'letter_spacing': '-1px',
                    'cursor': 'pointer'
                },
                '.nav-actions-cluster': {
                    'selector': '.nav-actions-cluster',
                    'display': 'flex',
                    'gap': '15px',
                    'align_items': 'center'
                },
                '.pill-action-btn': {
                    'selector': '.pill-action-btn',
                    'bg': 'transparent',
                    'border': '1px solid #232b28',
                    'padding': '12px 24px',
                    'border_radius': '30px',
                    'font_size': '0.85rem',
                    'font_weight': '600',
                    'text_transform': 'uppercase',
                    'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                    'cursor': 'pointer',
                    'display': 'flex',
                    'align_items': 'center',
                    'gap': '8px'
                },
                '.pill-action-btn:hover': {
                    'bg': '#232b28',
                    'color': '#fcf8f4'
                },
                '.counter-dot': {
                    'selector': '.counter-dot',
                    'bg': '#df9f8c',
                    'color': 'white',
                    'padding': '2px 8px',
                    'border_radius': '20px',
                    'font_size': '0.75rem'
                },
                '.account-dropdown-wrapper': {
                    'selector': '.account-dropdown-wrapper',
                    'position': 'relative',
                    'display': 'inline-block'
                },
                '.account-dropdown-btn': {
                    'selector': '.account-dropdown-btn',
                    'bg': 'transparent',
                    'border': '1px solid #232b28',
                    'padding': '10px 16px',
                    'border_radius': '30px',
                    'font_size': '1rem',
                    'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                    'cursor': 'pointer',
                    'display': 'flex',
                    'align_items': 'center',
                    'gap': '6px'
                },
                '.account-dropdown-btn:hover': {
                    'bg': '#232b28',
                    'color': '#fcf8f4'
                },
                '.account-dropdown-menu': {
                    'selector': '.account-dropdown-menu',
                    'position': 'absolute',
                    'top': '100%',
                    'right': '0',
                    'min_width': '200px',
                    'bg': '#fcf8f4',
                    'border': '1px solid #232b28',
                    'border_radius': '20px',
                    'padding': '10px 0',
                    'margin_top': '10px',
                    'opacity': '0',
                    'visibility': 'hidden',
                    'transform': 'translateY(10px)',
                    'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                    'z_index': '110',
                    'box_shadow': '0 20px 40px rgba(0,0,0,0.08)'
                },
                '.account-dropdown-wrapper:hover .account-dropdown-menu': {
                    'opacity': '1',
                    'visibility': 'visible',
                    'transform': 'translateY(0)'
                },
                '.account-dropdown-menu a': {
                    'selector': '.account-dropdown-menu a',
                    'display': 'block',
                    'padding': '12px 24px',
                    'font_size': '0.85rem',
                    'color': '#232b28',
                    'text_decoration': 'none',
                    'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                    'border_bottom': '1px solid rgba(35, 43, 40, 0.05)'
                },
                '.account-dropdown-menu a:hover': {
                    'bg': '#f5ede4',
                    'color': '#df9f8c'
                },
                '.account-dropdown-menu .logout-link': {
                    'selector': '.account-dropdown-menu .logout-link',
                    'color': '#b04141'
                },
                '.account-dropdown-menu .logout-link:hover': {
                    'bg': '#fde8e8'
                }
            },
            'responsive': {
                'max_width_768': {
                    '.organic-nav': {
                        'padding': '20px 4%',
                        'flex_direction': 'column',
                        'gap': '15px'
                    },
                    '.nav-actions-cluster': {
                        'gap': '10px',
                        'flex_wrap': 'wrap',
                        'justify_content': 'center'
                    },
                    '.pill-action-btn': {
                        'padding': '8px 16px',
                        'font_size': '0.75rem'
                    },
                    '.brand-crest': {
                        'font_size': '1.5rem'
                    }
                }
            }
        },
        
        # ============================================
        # HERO (Sections 11-15)
        # ============================================
        'hero': {
            'ids': ['11', '12', '13', '14', '15'],
            'container': '.cozy-intro-canopy',
            'max_width': '1400px',
            'margin': '40px auto 80px',
            'padding': '0 4%',
            'display': 'grid',
            'grid_template_columns': '1.2fr 0.8fr',
            'gap': '40px',
            'align_items': 'center',
            'position': 'relative',
            'children': {
                '.intro-statement': {
                    'selector': '.intro-statement',
                    'font_family': "'Italiana', serif",
                    'font_size': 'clamp(2.8rem, 5vw, 5.5rem)',
                    'line_height': '1.05'
                },
                '.intro-statement em': {
                    'selector': '.intro-statement em',
                    'color': '#df9f8c',
                    'font_style': 'italic'
                },
                '.intro-context-box': {
                    'selector': '.intro-context-box',
                    'bg': '#f5ede4',
                    'padding': '40px',
                    'border_radius': '40px 10px 40px 40px',
                    'border': '1px solid rgba(35, 43, 40, 0.1)'
                }
            },
            'responsive': {
                'max_width_900': {
                    '.cozy-intro-canopy': {
                        'grid_template_columns': '1fr',
                        'margin_bottom': '40px'
                    }
                },
                'max_width_768': {
                    '.intro-context-box': {
                        'padding': '25px'
                    }
                }
            }
        },
        
        # ============================================
        # PRODUCTS SECTION (Sections 16-24)
        # ============================================
        'products_section': {
            'ids': ['16', '17', '18', '19', '20', '21', '22', '23', '24'],
            'container': '.chambers-grid-title, .chambers-container-matrix',
            'description': 'Products section with grid layout. Includes section title and product grid.',
            'children': {
                '.chambers-grid-title': {
                    'selector': '.chambers-grid-title',
                    'font_family': "'Italiana', serif",
                    'font_size': 'clamp(2rem, 4vw, 3.5rem)',
                    'max_width': '1400px',
                    'margin': '0 auto 40px',
                    'padding': '0 4%'
                },
                '.chambers-container-matrix': {
                    'selector': '.chambers-container-matrix',
                    'max_width': '1400px',
                    'margin': '0 auto 100px',
                    'padding': '0 4%',
                    'display': 'grid',
                    'grid_template_columns': 'repeat(auto-fit, minmax(320px, 1fr))',
                    'gap': '50px'
                }
            },
            'responsive': {
                'max_width_768': {
                    '.chambers-container-matrix': {
                        'grid_template_columns': '1fr',
                        'gap': '30px'
                    }
                }
            }
        },
        
        # ============================================
        # PRODUCT CARDS (Sections 100-111)
        # ============================================
        'product_cards': {
            'ids': ['100', '101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111'],
            'container': '.chamber-card-node',
            'description': 'Product cards in a grid layout. Each card has an image circle, tag label, title, price, and bookmark button.',
            'bg': '#f5ede4',
            'border_radius': '40px',
            'padding': '30px',
            'display': 'flex',
            'flex_direction': 'column',
            'align_items': 'center',
            'text_align': 'center',
            'border': '1px solid transparent',
            'transition': 'all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)',
            'cursor': 'pointer',
            'position': 'relative',
            'children': {
                '.chamber-card-node:hover': {
                    'selector': '.chamber-card-node:hover',
                    'transform': 'translateY(-10px) scale(1.02)',
                    'border_color': '#df9f8c',
                    'bg': 'white',
                    'box_shadow': '0 30px 60px rgba(223,159,140,0.12)'
                },
                '.chamber-portal-circle': {
                    'selector': '.chamber-portal-circle',
                    'width': '240px',
                    'height': '240px',
                    'border_radius': '50%',
                    'overflow': 'hidden',
                    'margin_bottom': '25px',
                    'border': '1px solid #232b28',
                    'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)'
                },
                '.chamber-card-node:hover .chamber-portal-circle': {
                    'transform': 'rotate(3deg) scale(1.05)'
                },
                '.chamber-portal-circle img': {
                    'selector': '.chamber-portal-circle img',
                    'width': '100%',
                    'height': '100%',
                    'object_fit': 'cover'
                },
                '.chamber-tag': {
                    'selector': '.chamber-tag',
                    'font_size': '0.75rem',
                    'font_weight': '700',
                    'text_transform': 'uppercase',
                    'letter_spacing': '2px',
                    'color': '#8fa89b',
                    'margin_bottom': '8px'
                },
                '.chamber-title': {
                    'selector': '.chamber-title',
                    'font_family': "'Italiana', serif",
                    'font_size': '1.8rem',
                    'line_height': '1.2',
                    'margin_bottom': '12px'
                },
                '.chamber-price': {
                    'selector': '.chamber-price',
                    'font_size': '1.25rem',
                    'font_weight': '700',
                    'color': '#232b28'
                },
                '.chamber-save-bookmark': {
                    'selector': '.chamber-save-bookmark',
                    'position': 'absolute',
                    'top': '25px',
                    'right': '25px',
                    'bg': 'white',
                    'border': '1px solid #232b28',
                    'width': '40px',
                    'height': '40px',
                    'border_radius': '50%',
                    'display': 'flex',
                    'align_items': 'center',
                    'justify_content': 'center',
                    'cursor': 'pointer',
                    'transition': '0.3s',
                    'z_index': '5'
                },
                '.chamber-save-bookmark:hover': {
                    'bg': '#df9f8c',
                    'color': 'white',
                    'border_color': '#df9f8c'
                }
            },
            'responsive': {
                'max_width_768': {
                    '.chamber-card-node': {
                        'padding': '20px'
                    },
                    '.chamber-portal-circle': {
                        'width': '180px',
                        'height': '180px'
                    },
                    '.chamber-title': {
                        'font_size': '1.4rem'
                    }
                }
            }
        },
        
        # ============================================
        # FAQ (Sections 25-32)
        # ============================================
        'faq': {
            'ids': ['25', '26', '27', '28', '29', '30', '31', '32'],
            'container': '.reassurance-envelope',
            'max_width': '900px',
            'margin': '80px auto',
            'padding': '0 4%',
            'children': {
                '.reassurance-node': {
                    'selector': '.reassurance-node',
                    'border_bottom': '1px solid #232b28'
                },
                '.reassurance-header-btn': {
                    'selector': '.reassurance-header-btn',
                    'width': '100%',
                    'padding': '24px 0',
                    'bg': 'none',
                    'border': 'none',
                    'text_align': 'left',
                    'font_family': "'Italiana', serif",
                    'font_size': '1.4rem',
                    'display': 'flex',
                    'justify_content': 'space-between',
                    'align_items': 'center',
                    'cursor': 'pointer'
                },
                '.reassurance-body-drawer': {
                    'selector': '.reassurance-body-drawer',
                    'max_height': '0',
                    'overflow': 'hidden',
                    'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                    'color': '#4b5451',
                    'font_size': '0.95rem'
                }
            }
        },
        
        # ============================================
        # DRAWERS (Sections 33-36)
        # ============================================
        'drawers': {
            'ids': ['33', '34', '35', '36'],
            'container': '.chambers-drawer',
            'position': 'fixed',
            'top': '0',
            'right': '-460px',
            'width': '440px',
            'height': '100%',
            'bg': '#fcf8f4',
            'border_left': '1px solid #232b28',
            'z_index': '210',
            'display': 'flex',
            'flex_direction': 'column',
            'padding': '40px',
            'transition': 'right 0.5s cubic-bezier(0.16, 1, 0.3, 1)',
            'children': {
                '.drawer-shield-shade': {
                    'selector': '.drawer-shield-shade',
                    'position': 'fixed',
                    'top': '0',
                    'left': '0',
                    'right': '0',
                    'bottom': '0',
                    'bg': 'rgba(35, 43, 40, 0.25)',
                    'backdrop_filter': 'blur(10px)',
                    'z_index': '200',
                    'display': 'none'
                },
                '.drawer-title-row': {
                    'selector': '.drawer-title-row',
                    'font_family': "'Italiana', serif",
                    'font_size': '2.2rem',
                    'display': 'flex',
                    'justify_content': 'space-between',
                    'align_items': 'center',
                    'margin_bottom': '35px',
                    'text_transform': 'uppercase'
                },
                '.drawer-scroll-pool': {
                    'selector': '.drawer-scroll-pool',
                    'flex': '1',
                    'overflow_y': 'auto',
                    'display': 'flex',
                    'flex_direction': 'column',
                    'gap': '20px'
                },
                '.drawer-item-node': {
                    'selector': '.drawer-item-node',
                    'display': 'flex',
                    'gap': '15px',
                    'align_items': 'center',
                    'bg': 'white',
                    'padding': '15px',
                    'border_radius': '20px',
                    'border': '1px solid rgba(35, 43, 40, 0.05)',
                    'position': 'relative'
                },
                '.drawer-node-thumb': {
                    'selector': '.drawer-node-thumb',
                    'width': '70px',
                    'height': '70px',
                    'border_radius': '50%',
                    'object_fit': 'cover',
                    'border': '1px solid #232b28'
                },
                '.drawer-node-trash': {
                    'selector': '.drawer-node-trash',
                    'position': 'absolute',
                    'top': '15px',
                    'right': '15px',
                    'bg': 'none',
                    'border': 'none',
                    'color': '#df9f8c',
                    'cursor': 'pointer'
                }
            },
            'responsive': {
                'max_width_460': {
                    '.chambers-drawer': {
                        'width': '100%',
                        'right': '-100%',
                        'padding': '20px'
                    }
                }
            }
        },
        
        # ============================================
        # STICKY CART (Sections 37-38)
        # ============================================
        'sticky_cart': {
            'ids': ['37', '38'],
            'container': '.sticky-cart-bar',
            'position': 'fixed',
            'bottom': '-100px',
            'left': '0',
            'width': '100%',
            'bg': 'rgba(252, 248, 244, 0.95)',
            'backdrop_filter': 'blur(12px)',
            'border_top': '1px solid rgba(35, 43, 40, 0.08)',
            'padding': '16px 24px',
            'z_index': '90',
            'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
            'box_shadow': '0 -10px 30px rgba(0,0,0,0.04)',
            'children': {
                '.sticky-cart-bar.active': {
                    'selector': '.sticky-cart-bar.active',
                    'bottom': '0'
                },
                '.sticky-cart-layout': {
                    'selector': '.sticky-cart-layout',
                    'max_width': '1400px',
                    'margin': '0 auto',
                    'display': 'flex',
                    'justify_content': 'space-between',
                    'align_items': 'center',
                    'gap': '20px',
                    'flex_wrap': 'wrap'
                },
                '.sticky-cart-summary': {
                    'selector': '.sticky-cart-summary',
                    'display': 'flex',
                    'align_items': 'center',
                    'gap': '16px'
                },
                '.sticky-cart-icon-box': {
                    'selector': '.sticky-cart-icon-box',
                    'position': 'relative',
                    'font_size': '20px',
                    'color': '#232b28',
                    'bg': 'white',
                    'width': '48px',
                    'height': '48px',
                    'display': 'flex',
                    'align_items': 'center',
                    'justify_content': 'center',
                    'border_radius': '50%',
                    'border': '1px solid rgba(35, 43, 40, 0.08)'
                },
                '.sticky-cart-count': {
                    'selector': '.sticky-cart-count',
                    'font_weight': '700',
                    'color': '#232b28'
                },
                '.sticky-cart-total': {
                    'selector': '.sticky-cart-total',
                    'font_weight': '800',
                    'color': '#df9f8c',
                    'font_size': '16px'
                },
                '.sticky-cart-actions': {
                    'selector': '.sticky-cart-actions',
                    'display': 'flex',
                    'gap': '12px'
                },
                '.sticky-view-bag-btn': {
                    'selector': '.sticky-view-bag-btn',
                    'border': '1px solid #232b28',
                    'color': '#232b28',
                    'padding': '12px 24px',
                    'font_weight': '700',
                    'font_size': '13px',
                    'text_transform': 'uppercase',
                    'border_radius': '30px',
                    'bg': 'transparent',
                    'cursor': 'pointer',
                    'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)'
                },
                '.sticky-view-bag-btn:hover': {
                    'bg': '#232b28',
                    'color': '#fcf8f4'
                },
                '.sticky-checkout-btn': {
                    'selector': '.sticky-checkout-btn',
                    'bg': '#df9f8c',
                    'color': '#FFFFFF',
                    'padding': '12px 32px',
                    'font_weight': '700',
                    'font_size': '13px',
                    'text_transform': 'uppercase',
                    'border_radius': '30px',
                    'border': 'none',
                    'cursor': 'pointer',
                    'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                    'display': 'flex',
                    'align_items': 'center',
                    'gap': '8px'
                },
                '.sticky-checkout-btn:hover': {
                    'bg': '#232b28'
                }
            },
            'responsive': {
                'max_width_768': {
                    '.sticky-cart-layout': {
                        'flex_direction': 'column',
                        'align_items': 'stretch'
                    },
                    '.sticky-cart-summary': {
                        'justify_content': 'center'
                    },
                    '.sticky-cart-actions': {
                        'justify_content': 'center'
                    }
                }
            }
        },
        
        # ============================================
        # CONTACT (Sections 40-53)
        # ============================================
        'contact': {
            'ids': ['40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53'],
            'container': '.contact-canvas',
            'padding': '100px 4%',
            'max_width': '1200px',
            'margin': '0 auto',
            'children': {
                '.contact-card-box': {
                    'selector': '.contact-card-box',
                    'display': 'grid',
                    'grid_template_columns': '0.8fr 1.2fr',
                    'border': '1px solid rgba(35, 43, 40, 0.08)',
                    'bg': 'white',
                    'border_radius': '40px',
                    'box_shadow': '0 40px 80px rgba(35, 43, 40, 0.03)',
                    'overflow': 'hidden'
                },
                '.contact-aesthetic-sidebar': {
                    'selector': '.contact-aesthetic-sidebar',
                    'padding': '50px',
                    'border_right': '1px solid rgba(35, 43, 40, 0.08)',
                    'display': 'flex',
                    'flex_direction': 'column',
                    'justify_content': 'space-between',
                    'bg': '#f5ede4'
                },
                '.contact-aesthetic-sidebar h3': {
                    'selector': '.contact-aesthetic-sidebar h3',
                    'font_family': "'Italiana', serif",
                    'font_size': '2.2rem',
                    'line_height': '1.1',
                    'font_weight': '400'
                },
                '.studio-coordinates': {
                    'selector': '.studio-coordinates',
                    'font_size': '0.85rem',
                    'line_height': '2',
                    'color': '#5c6260'
                },
                '.contact-form-pane': {
                    'selector': '.contact-form-pane',
                    'padding': '50px'
                },
                '.art-form-group': {
                    'selector': '.art-form-group',
                    'position': 'relative',
                    'margin_bottom': '35px'
                },
                '.art-form-group input, .art-form-group textarea': {
                    'selector': '.art-form-group input, .art-form-group textarea',
                    'width': '100%',
                    'bg': 'none',
                    'border': 'none',
                    'border_bottom': '1px solid rgba(35, 43, 40, 0.15)',
                    'padding': '12px 0',
                    'font_size': '0.95rem',
                    'color': '#232b28',
                    'outline': 'none',
                    'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)'
                },
                '.art-form-group label': {
                    'selector': '.art-form-group label',
                    'position': 'absolute',
                    'left': '0',
                    'top': '12px',
                    'font_size': '0.8rem',
                    'color': '#8a908e',
                    'text_transform': 'uppercase',
                    'letter_spacing': '1px',
                    'pointer_events': 'none',
                    'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)'
                },
                '.art-form-group input:focus ~ label, .art-form-group input:not(:placeholder-shown) ~ label, .art-form-group textarea:focus ~ label, .art-form-group textarea:not(:placeholder-shown) ~ label': {
                    'selector': '.art-form-group input:focus ~ label, .art-form-group input:not(:placeholder-shown) ~ label, .art-form-group textarea:focus ~ label, .art-form-group textarea:not(:placeholder-shown) ~ label',
                    'top': '-20px',
                    'font_size': '0.7rem',
                    'color': '#df9f8c'
                },
                '.art-form-group input:focus, .art-form-group textarea:focus': {
                    'selector': '.art-form-group input:focus, .art-form-group textarea:focus',
                    'border_bottom_color': '#df9f8c'
                },
                '.art-submit-btn': {
                    'selector': '.art-submit-btn',
                    'bg': '#232b28',
                    'color': '#fcf8f4',
                    'border': 'none',
                    'padding': '18px 45px',
                    'font_size': '0.8rem',
                    'text_transform': 'uppercase',
                    'letter_spacing': '2px',
                    'font_weight': '600',
                    'cursor': 'pointer',
                    'border_radius': '30px',
                    'transition': 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)'
                },
                '.art-submit-btn:hover': {
                    'bg': '#df9f8c',
                    'color': 'white',
                    'transform': 'translateY(-2px)'
                }
            },
            'responsive': {
                'max_width_850': {
                    '.contact-card-box': {
                        'grid_template_columns': '1fr'
                    },
                    '.contact-aesthetic-sidebar': {
                        'border_right': 'none',
                        'border_bottom': '1px solid rgba(35,43,40,0.08)'
                    }
                },
                'max_width_768': {
                    '.contact-aesthetic-sidebar': {
                        'padding': '30px'
                    },
                    '.contact-form-pane': {
                        'padding': '30px'
                    }
                }
            }
        },
        
        # ============================================
        # FOOTER (Sections 54-62)
        # ============================================
        'footer': {
            'ids': ['54', '55', '56', '57', '58', '59', '60', '61', '62'],
            'container': 'footer',
            'bg': '#232b28',
            'color': '#fcf8f4',
            'padding': '80px 4% 40px',
            'border_radius': '40px 40px 0 0',
            'margin_top': '0',
            'children': {
                '.footer-inner-alignment': {
                    'selector': '.footer-inner-alignment',
                    'max_width': '1400px',
                    'margin': '0 auto',
                    'display': 'grid',
                    'grid_template_columns': 'repeat(auto-fit, minmax(260px, 1fr))',
                    'gap': '50px',
                    'border_bottom': '1px solid rgba(252,248,244,0.1)',
                    'padding_bottom': '50px'
                },
                '.footer-logo': {
                    'selector': '.footer-logo',
                    'font_family': "'Italiana', serif",
                    'font_size': '2.2rem',
                    'color': '#df9f8c',
                    'margin_bottom': '15px'
                },
                '.footer-inner-alignment p': {
                    'selector': '.footer-inner-alignment p',
                    'opacity': '0.6',
                    'font_size': '0.9rem'
                },
                '.footer-inner-alignment h4': {
                    'selector': '.footer-inner-alignment h4',
                    'font_size': '0.8rem',
                    'text_transform': 'uppercase',
                    'letter_spacing': '2px',
                    'margin_bottom': '20px',
                    'color': '#8fa89b'
                },
                '.footer-inner-alignment a': {
                    'selector': '.footer-inner-alignment a',
                    'font_size': '0.9rem',
                    'opacity': '0.7',
                    'cursor': 'pointer'
                }
            },
            'responsive': {
                'max_width_768': {
                    'footer': {
                        'padding': '60px 4% 30px'
                    },
                    '.footer-inner-alignment': {
                        'grid_template_columns': '1fr',
                        'gap': '30px'
                    }
                }
            }
        }
    },
    
    # ============================================
    # SPACING RULES
    # ============================================
    'spacing_rules': {
        'section_gap': '0px',
        'container_padding': '0 4%',
        'mobile_padding': '0 20px',
        'desktop_padding': '0 4%',
        'section_margin': '0 auto',
        'max_width': '1400px'
    },
    
    # ============================================
    # RESPONSIVE BREAKPOINTS
    # ============================================
    'responsive_breakpoints': {
        'mobile': '320px - 768px',
        'tablet': '769px - 1024px',
        'desktop': '1025px+'
    }
}


# ============================================
# COLOR PALETTES
# ============================================

COLOR_PALETTES = {
    'food_beverage': {
        'food_warm': {'primary': '#232b28', 'secondary': '#8fa89b', 'accent': '#df9f8c', 'bg': '#fcf8f4', 'bg_alt': '#f5ede4', 'text': '#232b28'},
        'food_fresh': {'primary': '#2E7D32', 'secondary': '#43A047', 'accent': '#FFD54F', 'bg': '#FFFDE7', 'bg_alt': '#F5F5E0', 'text': '#232b28'},
        'food_coffee': {'primary': '#3D1F0A', 'secondary': '#6B3A1A', 'accent': '#C49A6C', 'bg': '#FFF5E6', 'bg_alt': '#F0E8D5', 'text': '#232b28'},
        'food_modern': {'primary': '#1a1a2e', 'secondary': '#2d2d44', 'accent': '#e94560', 'bg': '#ffffff', 'bg_alt': '#f5f5f5', 'text': '#1a1a2e'},
    }
}

# ============================================
# INDUSTRY CONTENT
# ============================================

INDUSTRY_CONTENT = {
    'food_beverage': {
        'subtitle': 'CRAFT. FLAVOR. PASSION.',
        'desc': 'Artisanal food and beverages crafted with love and the finest ingredients.',
        'collection': '✦ Specialties',
        'p1': 'SIGNATURE|Artisan Coffee|$28|Ethically sourced, small-batch roasted coffee.',
        'p2': 'HERITAGE|Craft Chocolate|$35|Bean-to-bar chocolate from rare cacao varieties.',
        'p3': 'PURE|Cold Pressed Juice|$18|Nutrient-rich cold-pressed juices from organic produce.',
        'footer': 'Celebrating the art of food. Quality, sustainability, and exceptional taste.',
        'f1': 'What makes this unique?|We source directly from producers who share our commitment to quality.',
        'f2': 'Shipping policy?|Complimentary shipping on all orders.'
    }
}

# ============================================
# CREATIVE THEMES
# ============================================

CREATIVE_THEMES = {
    'playful_whimsical': {
        'name': 'Playful & Whimsical',
        'description': 'Fun, creative, approachable. Pastels, bright colors, rounded everything.',
        'color_palette': {
            'primary': '#232b28',
            'secondary': '#8fa89b',
            'accent': '#df9f8c',
            'bg': '#fcf8f4',
            'bg_alt': '#f5ede4',
            'text': '#232b28'
        },
        'fonts': {
            'display': "'Italiana', serif",
            'body': "'Plus Jakarta Sans', sans-serif"
        },
        'design_philosophy': 'Delight and surprise. Use bright colors, bouncy animations, and playful details.',
        'complex_css': [
            'bouncy animations with cubic-bezier',
            'rounded corners throughout',
            'soft shadows and warm tones',
            'playful hover effects'
        ]
    }
}

# ============================================
# COPYWRITING STYLES
# ============================================

COPYWRITING_STYLES = {
    'playful_fun': {
        'name': 'Playful & Fun',
        'description': 'Quirky, memorable, engaging. Use wordplay and personality.',
        'examples': {
            'headline': 'Good things come in beautiful packages.',
            'subtitle': 'We make stuff. Good stuff.',
            'description': 'Life is too short for boring things.'
        }
    }
}

# ============================================
# COLOR PALETTES DEFINITION
# ============================================

COLOR_PALETTES = {
    'fashion': {
        'fashion_luxury': {'primary': '#0a0a0a', 'secondary': '#1a1a1a', 'accent': '#c9a959', 'bg': '#f5f0e8', 'bg_alt': '#e8e0d5'},
        'fashion_modern': {'primary': '#1a1a2e', 'secondary': '#16213e', 'accent': '#e94560', 'bg': '#ffffff', 'bg_alt': '#f5f5f5'},
        'fashion_bold': {'primary': '#0d0d0d', 'secondary': '#1a1a2e', 'accent': '#ff006e', 'bg': '#fcf7f8', 'bg_alt': '#f0e8ea'},
        'fashion_elegant': {'primary': '#2d1b1b', 'secondary': '#4a2c2c', 'accent': '#d4a373', 'bg': '#faf6f0', 'bg_alt': '#f0ece4'},
    },
    'technology': {
        'tech_dark': {'primary': '#0a0a0a', 'secondary': '#1a1a2e', 'accent': '#4cc9f0', 'bg': '#0d0d0d', 'bg_alt': '#1a1a2e'},
        'tech_modern': {'primary': '#1e3a5f', 'secondary': '#2d5a7a', 'accent': '#4a7a9a', 'bg': '#f5f8fa', 'bg_alt': '#e8eef2'},
        'tech_neon': {'primary': '#0d0d0d', 'secondary': '#1a1a2e', 'accent': '#ff006e', 'bg': '#0d0d0d', 'bg_alt': '#1a1a2e'},
        'tech_clean': {'primary': '#1a1a2e', 'secondary': '#4361ee', 'accent': '#4361ee', 'bg': '#ffffff', 'bg_alt': '#f0f4f8'},
    },
    'home_decor': {
        'decor_organic': {'primary': '#2d5a27', 'secondary': '#4a7a44', 'accent': '#c9b99a', 'bg': '#f5f0e8', 'bg_alt': '#e8e5d5'},
        'decor_warm': {'primary': '#8B5A2B', 'secondary': '#A67B5B', 'accent': '#D4A373', 'bg': '#F5EDE4', 'bg_alt': '#EDE0D0'},
        'decor_nature': {'primary': '#2E4A35', 'secondary': '#5A7A6A', 'accent': '#C4A882', 'bg': '#F5F0E8', 'bg_alt': '#E8E0D5'},
        'decor_modern': {'primary': '#2d2d2d', 'secondary': '#4a4a4a', 'accent': '#8fa89b', 'bg': '#f5f0e8', 'bg_alt': '#e8e0d5'},
    },
    'health_wellness': {
        'wellness_calm': {'primary': '#2d5a27', 'secondary': '#4a7a44', 'accent': '#8fa89b', 'bg': '#f5f0e8', 'bg_alt': '#e8e5d5'},
        'wellness_spa': {'primary': '#1a3a2a', 'secondary': '#2d5a4a', 'accent': '#a8d5c8', 'bg': '#f5f5f0', 'bg_alt': '#e8e8e0'},
        'wellness_zen': {'primary': '#3a3a2a', 'secondary': '#5a5a4a', 'accent': '#d4c8a8', 'bg': '#f5f0e8', 'bg_alt': '#e8e0d5'},
        'wellness_clean': {'primary': '#1a3a4a', 'secondary': '#2d5a6a', 'accent': '#8fc8d5', 'bg': '#f0f5f8', 'bg_alt': '#e0e8ec'},
    },
    'food_beverage': {
        'food_warm': {'primary': '#8B4513', 'secondary': '#D2691E', 'accent': '#F4A460', 'bg': '#FFF8F0', 'bg_alt': '#F5EDE0'},
        'food_fresh': {'primary': '#2E7D32', 'secondary': '#43A047', 'accent': '#FFD54F', 'bg': '#FFFDE7', 'bg_alt': '#F5F5E0'},
        'food_coffee': {'primary': '#3D1F0A', 'secondary': '#6B3A1A', 'accent': '#C49A6C', 'bg': '#FFF5E6', 'bg_alt': '#F0E8D5'},
        'food_modern': {'primary': '#1a1a2e', 'secondary': '#2d2d44', 'accent': '#e94560', 'bg': '#ffffff', 'bg_alt': '#f5f5f5'},
    },
    'beauty': {
        'beauty_pink': {'primary': '#2d1a2a', 'secondary': '#4a2a4a', 'accent': '#e8a0b0', 'bg': '#f5f0f5', 'bg_alt': '#e8e0e8'},
        'beauty_elegant': {'primary': '#1a1a2e', 'secondary': '#2d2d4a', 'accent': '#d4a0b0', 'bg': '#f5f0f5', 'bg_alt': '#e8e0e8'},
        'beauty_glow': {'primary': '#2d1a1a', 'secondary': '#4a2a2a', 'accent': '#f0c0a0', 'bg': '#faf5f0', 'bg_alt': '#f0ece4'},
        'beauty_clean': {'primary': '#1a2a2a', 'secondary': '#2d4a4a', 'accent': '#a0d4d4', 'bg': '#f0f5f5', 'bg_alt': '#e0e8e8'},
    },
    'sports': {
        'sports_energetic': {'primary': '#1a1a2e', 'secondary': '#2d1a2e', 'accent': '#ff6b35', 'bg': '#f5f0f5', 'bg_alt': '#e8e0e8'},
        'sports_fresh': {'primary': '#1a2e1a', 'secondary': '#2d4a2d', 'accent': '#4ade80', 'bg': '#f0f5f0', 'bg_alt': '#e0e8e0'},
        'sports_bold': {'primary': '#2e1a1a', 'secondary': '#4a2d1a', 'accent': '#ff4444', 'bg': '#f5f0f0', 'bg_alt': '#e8e0e0'},
        'sports_modern': {'primary': '#0a0a0a', 'secondary': '#1a1a2e', 'accent': '#4cc9f0', 'bg': '#0d0d0d', 'bg_alt': '#1a1a2e'},
    },
    'education': {
        'edu_classic': {'primary': '#1a2a3a', 'secondary': '#2d4a5a', 'accent': '#c9a959', 'bg': '#f5f0e8', 'bg_alt': '#e8e0d5'},
        'edu_modern': {'primary': '#1e3a5f', 'secondary': '#2d5a7a', 'accent': '#4a7a9a', 'bg': '#f5f8fa', 'bg_alt': '#e8eef2'},
        'edu_fresh': {'primary': '#2d5a27', 'secondary': '#4a7a44', 'accent': '#8fa89b', 'bg': '#f5f0e8', 'bg_alt': '#e8e5d5'},
        'edu_playful': {'primary': '#2d1a2e', 'secondary': '#4a2d4a', 'accent': '#e8a0b0', 'bg': '#f5f0f5', 'bg_alt': '#e8e0e8'},
    },
    'other': {
        'default_corporate': {'primary': '#1e3a5f', 'secondary': '#2d5a7a', 'accent': '#4a7a9a', 'bg': '#f5f8fa', 'bg_alt': '#e8eef2'},
        'default_modern': {'primary': '#1a1a2e', 'secondary': '#16213e', 'accent': '#e94560', 'bg': '#ffffff', 'bg_alt': '#f5f5f5'},
        'default_warm': {'primary': '#8B5A2B', 'secondary': '#A67B5B', 'accent': '#D4A373', 'bg': '#F5EDE4', 'bg_alt': '#EDE0D0'},
        'default_dark': {'primary': '#0a0a0a', 'secondary': '#1a1a2e', 'accent': '#4cc9f0', 'bg': '#0d0d0d', 'bg_alt': '#1a1a2e'},
    }
}

# ============================================
# INDUSTRY CONTENT
# ============================================

INDUSTRY_CONTENT = {
    'fashion': {
        'subtitle': 'TIMELESS ELEGANCE. MODERN LUXURY.',
        'desc': 'Discover our curated collection of premium fashion pieces, designed for those who appreciate the finer things in life.',
        'collection': '✦ Collections',
        'p1': 'ICONIC|Signature Blazer|$450|A masterfully crafted blazer in premium wool.',
        'p2': 'ESSENTIAL|Classic Trench|$350|Timeless elegance meets modern functionality.',
        'p3': 'BASIC|Essential Shirt|$150|The perfect foundation piece, crafted from the finest cotton.',
        'footer': 'Redefining fashion excellence with curated collections that blend quality and style.',
        'f1': 'What makes this unique?|Every piece is crafted with premium materials and attention to detail.',
        'f2': 'Shipping policy?|Fast tracked shipping with orders arriving in 3-5 business days.'
    },
    'technology': {
        'subtitle': 'INNOVATION. SIMPLIFIED.',
        'desc': 'Experience the future of technology with our thoughtfully designed products.',
        'collection': '✦ Innovations',
        'p1': 'PRO|Nova Pro Laptop|$1,299|Ultra-powerful performance in an impossibly thin design.',
        'p2': 'AIR|Nova Air Tablet|$799|The thinnest, lightest tablet ever.',
        'p3': 'MINI|Nova Mini Speaker|$299|Room-filling sound from a speaker small enough to fit in your palm.',
        'footer': 'Pushing the boundaries of what\'s possible through thoughtful design.',
        'f1': 'What makes this unique?|Innovation-driven design with uncompromising attention to detail.',
        'f2': 'Shipping policy?|Free express shipping on all orders. Delivery in 2-4 business days.'
    },
    'beauty': {
        'subtitle': 'RADIANT YOU. NATURAL GLOW.',
        'desc': 'Discover skincare and cosmetics that celebrate your natural beauty.',
        'collection': '✦ Essentials',
        'p1': 'GLOW|Illuminating Serum|$89|Light-reflecting formula that instantly brightens.',
        'p2': 'PURE|Gentle Cleanser|$45|A soothing, non-stripping cleanser.',
        'p3': 'RADIANT|Daily Moisturizer|$67|Luxurious hydration that leaves skin plump and dewy.',
        'footer': 'Clean beauty for the modern individual. Ethics, sustainability, and results.',
        'f1': 'What makes this unique?|Our formulations combine cutting-edge science with natural ingredients.',
        'f2': 'Shipping policy?|Complimentary shipping on orders over $50.'
    },
    'home_decor': {
        'subtitle': 'NATURAL LIVING. BEAUTIFUL SPACES.',
        'desc': 'Transform your home with our sustainable, handcrafted pieces.',
        'collection': '✦ Collections',
        'p1': 'HERITAGE|Handwoven Rug|$380|Artisan-crafted rug with intricate patterns.',
        'p2': 'EARTH|Ceramic Vase|$145|Minimalist elegance meets organic form.',
        'p3': 'PURE|Organic Cotton Throw|$95|The epitome of comfort. Handwoven from organic cotton.',
        'footer': 'Curating a collection of sustainable, artisanal pieces.',
        'f1': 'What makes this unique?|Every piece is ethically sourced and crafted with sustainable materials.',
        'f2': 'Shipping policy?|Free home delivery on all orders.'
    },
    'health_wellness': {
        'subtitle': 'WELLNESS. REDEFINED.',
        'desc': 'Holistic wellness products designed to nurture your body, mind, and spirit.',
        'collection': '✦ Wellness',
        'p1': 'ZEN|Meditation Cushion|$78|Ergonomically designed for ultimate comfort.',
        'p2': 'PURE|Essential Oil Set|$56|Therapeutic-grade oils for relaxation and focus.',
        'p3': 'CORE|Resistance Bands|$45|Premium resistance bands for a full-body workout.',
        'footer': 'Empowering you to live your healthiest life.',
        'f1': 'What makes this unique?|Each product is carefully selected for quality and efficacy.',
        'f2': 'Shipping policy?|Free shipping on wellness sets.'
    },
    'food_beverage': {
        'subtitle': 'CRAFT. FLAVOR. PASSION.',
        'desc': 'Artisanal food and beverages crafted with love and the finest ingredients.',
        'collection': '✦ Specialties',
        'p1': 'SIGNATURE|Artisan Coffee|$28|Ethically sourced, small-batch roasted coffee.',
        'p2': 'HERITAGE|Craft Chocolate|$35|Bean-to-bar chocolate from rare cacao varieties.',
        'p3': 'PURE|Cold Pressed Juice|$18|Nutrient-rich cold-pressed juices from organic produce.',
        'footer': 'Celebrating the art of food. Quality, sustainability, and exceptional taste.',
        'f1': 'What makes this unique?|We source directly from producers who share our commitment to quality.',
        'f2': 'Shipping policy?|Complimentary shipping on all orders.'
    },
    'sports': {
        'subtitle': 'PUSH YOUR LIMITS.',
        'desc': 'Premium sports equipment and apparel designed for peak performance.',
        'collection': '✦ Performance',
        'p1': 'ELITE|Pro Training Shoes|$199|Engineered for maximum performance and comfort.',
        'p2': 'CORE|Performance Jersey|$89|Lightweight, breathable fabric for intense workouts.',
        'p3': 'ESSENTIAL|Durable Backpack|$129|Built to withstand the toughest training sessions.',
        'footer': 'Empowering athletes to achieve their best.',
        'f1': 'What makes this unique?|Our products are tested by professional athletes to ensure peak performance.',
        'f2': 'Shipping policy?|Free shipping on orders over $100.'
    },
    'education': {
        'subtitle': 'LEARN. GROW. EXCEL.',
        'desc': 'Educational tools and resources designed to inspire learning.',
        'collection': '✦ Resources',
        'p1': 'PREMIUM|Learning Tablet|$299|Interactive learning for students of all ages.',
        'p2': 'ESSENTIAL|Study Kit|$79|Complete set of tools for effective learning.',
        'p3': 'BASIC|Educational Books|$49|Curated collection of educational materials.',
        'footer': 'Empowering education through quality resources.',
        'f1': 'What makes this unique?|Our resources are developed by educators for educators.',
        'f2': 'Shipping policy?|Free shipping on all educational materials.'
    },
    'other': {
        'subtitle': 'EXCELLENCE. DELIVERED.',
        'desc': 'Discover our curated collection of premium products designed to exceed your expectations.',
        'collection': '✦ Collections',
        'p1': 'PREMIUM|Signature Item|$99|The finest quality, meticulously crafted.',
        'p2': 'ESSENTIAL|Classic Piece|$79|Timeless design that never goes out of style.',
        'p3': 'BASIC|Essential Item|$49|Perfectly executed, sustainably made.',
        'footer': 'Quality, craftsmanship, and integrity in everything we do.',
        'f1': 'What makes this unique?|We are committed to quality, sustainability, and exceptional customer experience.',
        'f2': 'Shipping policy?|Free shipping on all orders.'
    }
}

# ============================================
# ELEMENT REGISTRY
# ============================================

ELEMENT_REGISTRY = {
    'nav': {
        'sections': ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
        'type': 'navigation',
        'css_targets': {
            '.organic-nav': 'Entire navigation container',
            '.brand-crest': 'Brand logo text',
            '.pill-action-btn': 'Action buttons',
            '.account-dropdown-wrapper': 'Dropdown wrapper',
            '.account-dropdown-btn': 'Dropdown trigger',
            '.account-dropdown-menu': 'Dropdown menu',
            '.account-dropdown-menu a': 'Dropdown links',
        }
    },
    'hero': {
        'sections': ['11', '12', '13', '14', '15'],
        'type': 'hero',
        'css_targets': {
            '.cozy-intro-canopy': 'Hero container',
            '.intro-statement': 'Hero main headline',
            '.intro-context-box': 'Hero context box',
            '.intro-context-box h3': 'Hero subtitle',
            '.intro-context-box p': 'Hero description'
        }
    },
    'products_section': {
        'sections': ['16', '17', '18', '19', '20', '21', '22', '23', '24'],
        'type': 'products_section',
        'css_targets': {
            '.chambers-grid-title': 'Section title',
            '.variant-group-headline': 'Variant labels',
            '.telemetry-reviews-dock h4': 'Reviews heading',
            '.telemetry-log-form': 'Review form container',
            '.telemetry-log-form input': 'Form inputs',
            '.telemetry-log-form textarea': 'Form textarea',
        }
    },
    'product_cards': {
        'sections': ['100', '101', '102', '103', '104', '105', '106', '107', '108', '109', '110', '111'],
        'type': 'product_cards',
        'css_targets': {
            '.chamber-card-node': 'Product card',
            '.chamber-portal-circle': 'Product image circle',
            '.chamber-tag': 'Product tag label',
            '.chamber-title': 'Product title',
            '.chamber-price': 'Product price',
            '.chamber-save-bookmark': 'Bookmark button'
        }
    },
    'faq': {
        'sections': ['25', '26', '27', '28', '29', '30', '31', '32'],
        'type': 'faq',
        'css_targets': {
            '.reassurance-envelope': 'FAQ container',
            '.reassurance-header-btn': 'FAQ item header',
            '.reassurance-body-drawer': 'FAQ body'
        }
    },
    'drawers': {
        'sections': ['33', '34', '35', '36'],
        'type': 'drawers',
        'css_targets': {
            '.drawer-shield-shade': 'Drawer overlay',
            '.chambers-drawer': 'Drawer container',
            '.drawer-title-row': 'Drawer title',
            '.drawer-item-node': 'Drawer item'
        }
    },
    'sticky_cart': {
        'sections': ['37', '38'],
        'type': 'sticky_cart',
        'css_targets': {
            '.sticky-cart-bar': 'Sticky cart bar',
            '.sticky-cart-total': 'Total price',
            '.sticky-view-bag-btn': 'View cart button',
            '.sticky-checkout-btn': 'Checkout button'
        }
    },
    'contact': {
        'sections': ['40', '41', '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53'],
        'type': 'contact',
        'css_targets': {
            '.contact-canvas': 'Contact section container',
            '.contact-card-box': 'Contact card',
            '.contact-aesthetic-sidebar': 'Sidebar',
            '.contact-aesthetic-sidebar h3': 'Sidebar heading',
            '.studio-coordinates': 'Address text',
            '.contact-form-pane': 'Form container',
            '.art-form-group input': 'Form input',
            '.art-form-group textarea': 'Form textarea',
            '.art-form-group label': 'Form label',
            '.art-submit-btn': 'Submit button'
        }
    },
    'footer': {
        'sections': ['54', '55', '56', '57', '58', '59', '60', '61', '62'],
        'type': 'footer',
        'css_targets': {
            'footer': 'Footer container',
            '.footer-logo': 'Footer logo',
            '.footer-inner-alignment h4': 'Footer heading',
            '.footer-inner-alignment a': 'Footer links',
        }
    }
}

# ============================================
# CREATIVE THEME DIRECTIONS
# ============================================

CREATIVE_THEMES = {
    'dark_luxury': {
        'name': 'Dark Luxury',
        'description': 'Sophisticated, moody, premium. Deep navies, charcoal, and gold accents. Serif display fonts with elegant spacing. Think: high-end fashion, premium automotive, luxury hotels.',
        'color_palette': {
            'primary': '#0a0a0a',
            'secondary': '#1a1a2e',
            'accent': '#c9a959',
            'bg': '#0d0d0d',
            'bg_alt': '#1a1a1a',
            'text': '#f5f0e8'
        },
        'fonts': {
            'display': "'Playfair Display', serif",
            'body': "'Montserrat', sans-serif"
        },
        'design_philosophy': 'Minimalist luxury with dramatic contrast. Use gold sparingly for maximum impact. Everything should feel expensive and curated.',
        'complex_css': [
            'glassmorphism with rgba backgrounds and backdrop-filter: blur(20px)',
            'text-shadow with gold glow effects',
            'gradient borders on key elements',
            'smooth slide-in animations on scroll',
            'hover scale effects with transition delays'
        ]
    },
    'bold_vibrant': {
        'name': 'Bold & Vibrant',
        'description': 'High-energy, daring, modern. Electric accents on dark or white backgrounds. Playful typography with personality. Think: tech startups, creative agencies, music brands.',
        'color_palette': {
            'primary': '#0d0d0d',
            'secondary': '#1a1a2e',
            'accent': '#ff006e',
            'bg': '#1a1a2e',
            'bg_alt': '#2a2a3a',
            'text': '#ffffff'
        },
        'fonts': {
            'display': "'Poppins', sans-serif",
            'body': "'DM Sans', sans-serif"
        },
        'design_philosophy': 'Make a statement. Use oversized typography, neon accents, and dramatic hover effects. Nothing should be subtle.',
        'complex_css': [
            'animated gradient backgrounds',
            'neon glow box-shadows on hover',
            'pulse animations on CTAs',
            'floating elements with parallax',
            'color-shift transitions on hover'
        ]
    },
    'organic_earthy': {
        'name': 'Organic & Earthy',
        'description': 'Warm, natural, grounded. Terracotta, sage, and cream tones. Rounded corners and flowing layouts. Think: wellness brands, sustainable products, spas.',
        'color_palette': {
            'primary': '#2d5a27',
            'secondary': '#4a7a44',
            'accent': '#d4877a',
            'bg': '#f5ede4',
            'bg_alt': '#e8e0d5',
            'text': '#2d3a2d'
        },
        'fonts': {
            'display': "'Cormorant Garamond', serif",
            'body': "'Inter', sans-serif"
        },
        'design_philosophy': 'Natural and inviting. Use warm tones, soft shadows, and organic shapes. Everything should feel approachable.',
        'complex_css': [
            'soft shadows with warm color tones',
            'organic shape overlays with ::before and ::after',
            'subtle background patterns with gradients',
            'smooth fade-in animations',
            'rounded everything with custom border-radius'
        ]
    },
    'minimalist_architectural': {
        'name': 'Minimalist Architectural',
        'description': 'Clean, sharp, modern. Pure whites, blacks, and muted blues. Geometric layouts with precision. Think: architecture firms, design studios, premium tech.',
        'color_palette': {
            'primary': '#1e3a5f',
            'secondary': '#2d5a7a',
            'accent': '#4a7a9a',
            'bg': '#ffffff',
            'bg_alt': '#f5f8fa',
            'text': '#1a2a3a'
        },
        'fonts': {
            'display': "'Space Grotesk', sans-serif",
            'body': "'Inter', sans-serif"
        },
        'design_philosophy': 'Clean lines, generous whitespace, and perfect typography. Form follows function.',
        'complex_css': [
            'grid-based layouts with perfect alignment',
            'sharp borders with subtle color transitions',
            'monochrome palette with single accent color',
            'clean hover effects with underline animations',
            'geometric shapes with ::before and ::after'
        ]
    },
    'playful_whimsical': {
        'name': 'Playful & Whimsical',
        'description': 'Fun, creative, approachable. Pastels, bright colors, rounded everything. Quirky details and unexpected touches. Think: children\'s brands, creative studios, fun products.',
        'color_palette': {
            'primary': '#ff6b6b',
            'secondary': '#ffd93d',
            'accent': '#6bcb77',
            'bg': '#fff5f5',
            'bg_alt': '#ffe8e8',
            'text': '#2d2d2d'
        },
        'fonts': {
            'display': "'Quicksand', sans-serif",
            'body': "'Nunito', sans-serif"
        },
        'design_philosophy': 'Delight and surprise. Use bright colors, bouncy animations, and playful details. Nothing is too serious.',
        'complex_css': [
            'bouncy animations with cubic-bezier',
            'rainbow gradients on hover',
            'floating bubbles with animations',
            'rounded everything with large border-radius',
            'wiggle and bounce hover effects'
        ]
    }
}

# ============================================
# COPYWRITING STYLES
# ============================================

COPYWRITING_STYLES = {
    'poetic': {
        'name': 'Poetic & Evocative',
        'description': 'Lyrical, emotional, memorable. Use metaphor and vivid imagery.',
        'examples': {
            'headline': 'Where form becomes feeling.',
            'subtitle': 'Architecture for the soul.',
            'description': 'We design objects that hold meaning, not just function.'
        }
    },
    'direct_modern': {
        'name': 'Direct & Modern',
        'description': 'Bold, confident, clear. Short sentences. Strong verbs.',
        'examples': {
            'headline': 'Better design. Better life.',
            'subtitle': 'Products that perform.',
            'description': 'We make things that work beautifully.'
        }
    },
    'warm_welcoming': {
        'name': 'Warm & Welcoming',
        'description': 'Friendly, approachable, human. Use "you" and "we".',
        'examples': {
            'headline': 'We make beautiful things for beautiful homes.',
            'subtitle': 'Welcome to our world.',
            'description': 'Everything we create is designed with you in mind.'
        }
    },
    'luxury_premium': {
        'name': 'Luxury & Premium',
        'description': 'Sophisticated, exclusive, aspirational. Use refined language.',
        'examples': {
            'headline': 'The art of living well.',
            'subtitle': 'Craftsmanship redefined.',
            'description': 'Meticulously crafted pieces for the discerning few.'
        }
    },
    'playful_fun': {
        'name': 'Playful & Fun',
        'description': 'Quirky, memorable, engaging. Use wordplay and personality.',
        'examples': {
            'headline': 'Good things come in beautiful packages.',
            'subtitle': 'We make stuff. Good stuff.',
            'description': 'Life is too short for boring things.'
        }
    }
}

# ============================================
# ANIMATION STYLES
# ============================================

ANIMATION_STYLES = {
    'smooth_elegant': {
        'name': 'Smooth & Elegant',
        'transitions': 'all 0.6s cubic-bezier(0.16, 1, 0.3, 1)',
        'description': 'Refined, flowing animations. Nothing jerky or abrupt. Use for luxury and professional brands.',
        'animations': [
            'fadeInUp: opacity 0 → 1, translateY 30px → 0',
            'slideIn: translateX -50px → 0',
            'scaleIn: scale 0.95 → 1, opacity 0 → 1',
            'glowPulse: shadow glow pulsing effect'
        ]
    },
    'bouncy_energetic': {
        'name': 'Bouncy & Energetic',
        'transitions': 'all 0.5s cubic-bezier(0.34, 1.56, 0.64, 1)',
        'description': 'Springy, playful, full of life. Each interaction has personality. Use for creative and youthful brands.',
        'animations': [
            'bounceIn: scale 0.3 → 1 with bounce',
            'wiggle: small rotation back and forth',
            'jump: translateY with bounce',
            'spin: rotation with bounce'
        ]
    },
    'sharp_precision': {
        'name': 'Sharp & Precise',
        'transitions': 'all 0.2s ease-out',
        'description': 'Quick, crisp, responsive. No frills, just performance. Use for tech and professional brands.',
        'animations': [
            'quickFade: opacity 0 → 1 with 0.15s',
            'slideUp: translateY 20px → 0 with 0.2s',
            'scaleQuick: scale 0.98 → 1 with 0.15s',
            'colorShift: color change with 0.2s'
        ]
    },
    'soft_organic': {
        'name': 'Soft & Organic',
        'transitions': 'all 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94)',
        'description': 'Gentle, natural movements. Like leaves rustling in the wind. Use for wellness and nature brands.',
        'animations': [
            'float: gentle up and down movement',
            'fadeInSoft: opacity 0 → 1 with easing',
            'sway: gentle left-right movement',
            'grow: subtle scale with soft easing'
        ]
    }
}

# ============================================
# OPENROUTER CLIENT
# ============================================

class OpenRouterClient:
    """OpenRouter client with failover support"""
    
    def __init__(self):
        api_key = getattr(settings, 'OPENROUTER_API_KEY', None)
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY not found in settings")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
            default_headers={
                "HTTP-Referer": getattr(settings, 'SITE_URL', 'http://localhost:8000'),
                "X-Title": "AI Website Builder"
            }
        )
        
        self.models = [
            "google/gemini-2.5-flash",
            "google/gemini-2.5-pro",
            "meta-llama/llama-3.3-70b-instruct",
            "meta-llama/llama-4-scout",
            "mistralai/mistral-large",
            "deepseek/deepseek-chat",
            "qwen/qwen-2.5-72b-instruct",
            "microsoft/phi-4-mini-instruct",
            "cohere/command-r-plus",
            "anthropic/claude-3-haiku",
        ]
    
    def generate(self, prompt, max_tokens=15000, temperature=0.95):
        """Generate with automatic failover"""
        last_error = None
        
        for model in self.models:
            try:
                print(f"🔄 Trying model: {model}")
                
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an expert web designer. Output only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.9,
                )
                
                response_text = completion.choices[0].message.content
                
                if response_text and len(response_text) > 100:
                    print(f"✅ Model {model} succeeded ({len(response_text)} chars)")
                    return response_text, model
                else:
                    print(f"⚠️ Model {model} returned empty/too short response")
                    continue
                    
            except Exception as e:
                error_msg = str(e).lower()
                print(f"⚠️ Model {model} failed: {error_msg[:100]}")
                
                if "quota" in error_msg or "rate" in error_msg or "limit" in error_msg:
                    print(f"⏳ Quota/rate limit on {model}, trying next...")
                    last_error = error_msg
                    continue
                elif "402" in error_msg or "credits" in error_msg:
                    print(f"💰 Model {model} needs credits, trying next...")
                    last_error = error_msg
                    continue
                
                last_error = error_msg
                continue
        
        raise Exception(f"All models failed. Last error: {last_error}")


# ============================================
# AI DESIGN SERVICE
# ============================================

class AIDesignService:
    """Service for generating AI-powered website customizations"""
    
    def __init__(self, template_name='modernecommerce33'):
        self.template_name = template_name
        self.openrouter = OpenRouterClient()
        self.template_base_path = os.path.join(
            settings.BASE_DIR,
            'builder',
            'public_templates',
            template_name
        )
        self.editable_elements = self._extract_editable_elements()
        
        print(f"🚀 AI Design Service initialized")
        print(f" - Template: {template_name}")
        print(f" - Text elements: {len(self.editable_elements.get('text_keys', []))}")
        print(f" - Sections: {len(self.editable_elements.get('section_keys', []))}")
    
    def _extract_editable_elements(self):
        """Extract all editable elements from the registry"""
        elements = {
            'text_keys': [],
            'section_keys': [],
            'text_contexts': {},
            'section_contexts': {}
        }
        
        # Extract section keys
        for group_name, group_data in ELEMENT_REGISTRY.items():
            sections = group_data.get('sections', [])
            elements['section_keys'].extend(sections)
            for section_id in sections:
                elements['section_contexts'][section_id] = group_data.get('type', '')
        
        # Text elements (1-46, 100-108)
        text_keys = list(range(1, 47)) + list(range(100, 109))
        elements['text_keys'] = [str(k) for k in text_keys]
        
        return elements
    
    def generate_customizations(self, store_name, industry, style, palette):
        """Generate complete page_customizations JSON"""
        prompt = self._build_enhanced_prompt(store_name, industry, style, palette)
        
        try:
            print(f"📝 Prompt size: ~{len(prompt)} chars")
            response_text, used_model = self.openrouter.generate(prompt, max_tokens=15000, temperature=0.95)
            print(f"✅ Response from {used_model} ({len(response_text)} chars)")
            
            customizations = self._parse_response(response_text)
            return self._validate_and_enhance_customizations(customizations)
            
        except Exception as e:
            print(f"⚠️ AI generation failed: {e}")
            return self._get_complete_fallback(store_name, industry, style, palette)
    
    def _build_enhanced_prompt(self, store_name, industry, style, palette):
        """Build the enhanced AI prompt with full template context and professional design requirements"""
        
        # Get style colors
        colors = self._get_style_colors(style)
        
        # Get theme data
        theme = CREATIVE_THEMES.get(style, CREATIVE_THEMES['minimalist_architectural'])
        
        # Get industry content
        industry_content = INDUSTRY_CONTENT.get(industry, INDUSTRY_CONTENT.get('other', {}))
        
        # Get animation style
        animation_style = random.choice(list(ANIMATION_STYLES.values()))
        
        # Get copy style
        copy_style = random.choice(list(COPYWRITING_STYLES.values()))
        
        # Select an SVG pattern for the hero
        svg_name = random.choice(list(SVG_PATTERNS.keys()))
        svg_template = SVG_PATTERNS[svg_name]
        
        # Generate SVG with colors
        svg = svg_template.replace('%COLOR1%', colors.get('accent', '#FF0000'))
        svg = svg.replace('%COLOR2%', colors.get('primary', '#000000'))
        svg = svg.replace('%BGCOLOR%', colors.get('bg', '#FFFFFF'))
        
        # Build the template structure description
        section_details = []
        for section_name, section_data in TEMPLATE_STRUCTURE['sections'].items():
            css_targets = ELEMENT_REGISTRY.get(section_name, {}).get('css_targets', {})
            targets_str = '\n'.join([f'    • {target}: {desc}' for target, desc in css_targets.items()])
            
            section_details.append(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{section_name.upper()} - Sections: {', '.join(section_data['ids'])}
DESCRIPTION: {section_data['description']}

ORIGINAL HTML:
{section_data['html']}

CSS TARGETS (elements you can style):
{targets_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
        
        # Build text elements
        text_elements = {
            '1': 'Brand name',
            '2': 'Bookmarks button',
            '3': 'Cart button',
            '4': 'Sign Up link',
            '5': 'Sign In link',
            '6': 'Orders link',
            '7': 'Logout link',
            '8': 'Hero headline',
            '9': 'Hero subtitle',
            '10': 'Hero description',
            '11': 'Products section title',
            '12': 'Modal size label',
            '13': 'Modal color label',
            '14': 'Reviews section title',
            '15': 'Review form label',
            '16': 'Review author placeholder',
            '17': 'Review rating options',
            '18': 'Review text placeholder',
            '19': 'Submit review button',
            '20': 'FAQ title',
            '21': 'FAQ 1 header',
            '22': 'FAQ 1 body',
            '23': 'FAQ 2 header',
            '24': 'FAQ 2 body',
            '25': 'Cart drawer title',
            '26': 'Cart total label',
            '27': 'Checkout button',
            '28': 'Wishlist drawer title',
            '29': 'Sticky cart view button',
            '30': 'Sticky cart checkout',
            '31': 'Footer brand name',
            '32': 'Footer description',
            '33': 'Footer links heading',
            '34': 'Footer link',
            '35': 'Footer copyright',
            '36': 'Footer engine text',
            '37': 'Contact sidebar label',
            '38': 'Contact sidebar heading',
            '39': 'Contact address',
            '40': 'Contact name placeholder',
            '41': 'Contact name label',
            '42': 'Contact email placeholder',
            '43': 'Contact email label',
            '44': 'Contact message placeholder',
            '45': 'Contact message label',
            '46': 'Contact submit button',
            '100': 'Product 1 tag',
            '101': 'Product 1 title',
            '102': 'Product 1 price',
            '103': 'Product 2 tag',
            '104': 'Product 2 title',
            '105': 'Product 2 price',
            '106': 'Product 3 tag',
            '107': 'Product 3 title',
            '108': 'Product 3 price',
        }
        
        text_elements_str = '\n'.join([f'  "{id}": "{desc}"' for id, desc in text_elements.items()])

        # Build complex CSS techniques list with emphasis on responsive and scroll animations
        complex_css_techniques = [
            "GLASSMORPHISM: backdrop-filter: blur(20px) with rgba backgrounds for cards and overlays",
            "RESPONSIVE TYPOGRAPHY: Use clamp() for ALL font sizes - clamp(1rem, 2.5vw, 3rem)",
            "RESPONSIVE SPACING: Use clamp() for padding and margins",
            "CSS GRID: Use grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)) for product cards",
            "FLEXBOX: Use flex with gap, wrap, and alignment properties",
            "SCROLL-TRIGGERED ANIMATIONS: Use @keyframes with animation-timeline: scroll() or view()",
            "VIEW() FUNCTION: Use animation-timeline: view() for scroll-based reveals",
            "PARALLAX EFFECTS: Use perspective and transform: translateZ() for depth",
            "3D TRANSFORMS: Use rotateX, rotateY, perspective for immersive effects",
            "GRADIENT MESH: Multi-stop gradients with radial and linear combinations",
            "NEON GLOW: Box-shadow with spread and blur for glowing effects",
            "FLOATING ANIMATIONS: @keyframes for subtle floating elements with delays",
            "TEXTURE OVERLAYS: ::before with SVG patterns or gradient overlays",
            "MORPHING BORDERS: border-radius transitions on hover",
            "ANIMATED UNDERLINES: ::after with width transitions on hover",
            "STICKY POSITIONING: position: sticky with z-index layering",
            "CONTAINER QUERIES: Use @container for component-level responsiveness",
            "CUSTOM PROPERTIES: Use CSS variables for consistent theming",
            "HOVER EFFECTS: Complex hover states with transform, opacity, and color shifts",
            "KEYFRAMES: Custom animations with unique names and easing functions"
        ]
        
        # Randomly select techniques to emphasize
        selected_techniques = random.sample(complex_css_techniques, min(12, len(complex_css_techniques)))

        prompt = f"""
YOU ARE A VISIONARY WEB DESIGNER at a Fortune 500 company with 20 years of experience creating award-winning websites for global brands. Your work is known for being groundbreaking, emotionally resonant, and technically flawless.

================================================================================
THE ORIGINAL TEMPLATE - YOU MUST COMPLETELY TRANSFORM THIS
================================================================================

TEMPLATE NAME: modernecommerce33
DESCRIPTION: A modern e-commerce template with a clean, minimalist aesthetic.

{''.join(section_details)}

================================================================================
WHAT YOU MUST CHANGE - COMPLETE TRANSFORMATION REQUIRED
================================================================================

You MUST completely transform EVERY section. The final design should look NOTHING like the original template and feel like it was designed by a top-tier agency.

CRITICAL: Each section's CSS is applied to the section container (the element with the data-section attribute). Your CSS will be applied using the `&` selector which represents the section container.

================================================================================
CREATIVE BRIEF - FORTUNE 500 STANDARD
================================================================================

STORE NAME: {store_name}
INDUSTRY: {industry}
STYLE THEME: {theme['name']}
DESIGN APPROACH: {theme['design_philosophy']}

COLOR PALETTE (Use these as your foundation):
  Primary:    {colors.get('primary', '#000000')}
  Secondary:  {colors.get('secondary', '#333333')}
  Accent:     {colors.get('accent', '#FF0000')}
  Background: {colors.get('bg', '#FFFFFF')}
  Background Alt: {colors.get('bg_alt', '#F5F5F5')}
  Text:       {colors.get('text', '#000000')}

FONTS:
  Display: {theme['fonts']['display']}
  Body: {theme['fonts']['body']}

COPYWRITING STYLE: {copy_style['name']}
{copy_style['description']}
Examples: {copy_style['examples']}

ANIMATION STYLE: {animation_style['name']}
{animation_style['description']}
Transitions: {animation_style['transitions']}

INDUSTRY-SPECIFIC CONTENT (use this for inspiration):
  Subtitle: {industry_content.get('subtitle', '')}
  Description: {industry_content.get('desc', '')}
  Collection: {industry_content.get('collection', '')}
  Footer: {industry_content.get('footer', '')}

================================================================================
RESPONSIVE DESIGN REQUIREMENTS - FORTUNE 500 STANDARD
================================================================================

EVERY design MUST be fully responsive with these breakpoints:

📱 MOBILE (320px - 768px):
  • Single column layouts
  • Font sizes: clamp(1rem, 4vw, 1.5rem)
  • Touch targets: minimum 44px
  • Simplified navigation
  • Full-width buttons

📱 TABLET (769px - 1024px):
  • 2-column grid layouts
  • Font sizes: clamp(1rem, 2vw, 1.8rem)
  • Balanced spacing
  • Maintain readability

🖥️ DESKTOP (1025px+):
  • Multi-column layouts
  • Font sizes: clamp(1rem, 1.5vw, 2.5rem)
  • Generous whitespace
  • Sophisticated hover effects
  • Parallax and 3D effects

USE clamp() FOR ALL FONT SIZES, PADDING, AND MARGINS

================================================================================
SVG BACKGROUND FOR HERO - USE THIS AS INSPIRATION
================================================================================

Here's an SVG background pattern you can adapt for the hero section:

{svg}

Feel free to create your own SVG patterns or use this as a base. The hero should have a visually stunning background that makes it immediately eye-catching.

================================================================================
COMPLEX CSS TECHNIQUES YOU MUST USE
================================================================================

Focus on these techniques to create a Fortune 500-level design:

{chr(10).join([f'  • {t}' for t in selected_techniques])}

ADDITIONAL REQUIREMENTS:
  • Use ::before and ::after for decorative elements
  • Create custom @keyframes animations with unique names
  • Use calc() for dynamic spacing
  • Implement complex hover states with transforms and transitions
  • Use CSS custom properties for theming
  • Add scroll-triggered animations with view() or scroll()
  • Use container queries for component-level responsiveness

================================================================================
EYE-CATCHING HERO REQUIREMENTS
================================================================================

The hero section is the most important part of the page. It must be:
  • Visually stunning with gradient backgrounds or SVG patterns
  • Have floating or animated elements
  • Use large, impactful typography
  • Include a clear call-to-action
  • Feel immersive and engaging
  • Use parallax or 3D effects

================================================================================
TEXT ELEMENTS TO GENERATE - FORTUNE 500 COPY
================================================================================

{text_elements_str}

================================================================================
CRITICAL RULES FOR YOUR custom_css
================================================================================

1. Use `&` as the selector placeholder
2. ALL CSS properties MUST use `!important`
3. COMPLETELY TRANSFORM each section
4. Use clamp() for ALL responsive values
5. Include @keyframes for custom animations (use unique names)
6. Use ::before and ::after for decorative elements
7. Add complex hover states with transforms and transitions
8. Make the design feel COHESIVE across all sections
9. Use CSS variables for consistent theming
10. Add scroll-triggered animations with view() or scroll()

================================================================================
THE FIVE DESIGN PRINCIPLES YOU MUST FOLLOW
================================================================================

1. UNIQUE IDENTITY: Every design should feel completely different
2. VISUAL HIERARCHY: Clear structure that guides the eye
3. EMOTIONAL IMPACT: Design that evokes feeling and connection
4. TECHNICAL EXCELLENCE: Smooth animations, perfect spacing, polished details
5. RESPONSIVE MASTERY: Flawless on all devices

================================================================================
EXAMPLE custom_css FOR A FORTUNE 500 HERO SECTION
================================================================================

"custom_css": "& {{
    /* Fortune 500 Hero Section */
    background: linear-gradient(135deg, {colors.get('primary', '#000000')} 0%, {colors.get('secondary', '#333333')} 50%, {colors.get('primary', '#000000')} 100%) !important;
    padding: clamp(60px, 15vh, 180px) clamp(20px, 5%, 80px) !important;
    min-height: clamp(60vh, 80vh, 90vh) !important;
    display: flex !important;
    align-items: center !important;
    position: relative !important;
    overflow: hidden !important;
    perspective: 1000px !important;
}}

&::before {{
    content: '' !important;
    position: absolute !important;
    top: -20% !important;
    right: -20% !important;
    width: 80% !important;
    height: 150% !important;
    background: radial-gradient(ellipse at 70% 50%, {colors.get('accent', '#FF0000')} 0%, transparent 70%) !important;
    opacity: 0.15 !important;
    animation: heroPulse_{industry[:8]} 15s ease-in-out infinite !important;
}}

&::after {{
    content: '' !important;
    position: absolute !important;
    bottom: -10% !important;
    left: -10% !important;
    width: 60% !important;
    height: 100% !important;
    background: radial-gradient(ellipse at 30% 80%, {colors.get('accent', '#FF0000')} 0%, transparent 60%) !important;
    opacity: 0.1 !important;
    animation: heroFloat_{industry[:8]} 20s ease-in-out infinite !important;
}}

& .intro-statement {{
    font-size: clamp(2.5rem, 8vw, 6rem) !important;
    font-weight: 900 !important;
    color: {colors.get('text', '#FFFFFF')} !important;
    text-shadow: 0 4px 40px rgba(0,0,0,0.3) !important;
    letter-spacing: clamp(-1px, -0.02em, -3px) !important;
    line-height: 1.05 !important;
    position: relative !important;
    z-index: 2 !important;
}}

& .intro-statement em {{
    color: {colors.get('accent', '#FF0000')} !important;
    font-style: normal !important;
    background: linear-gradient(135deg, {colors.get('accent', '#FF0000')}, {colors.get('primary', '#000000')}) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}}

& .intro-context-box {{
    background: rgba(255,255,255,0.08) !important;
    backdrop-filter: blur(20px) !important;
    -webkit-backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: clamp(12px, 2vw, 24px) !important;
    padding: clamp(24px, 4vw, 48px) !important;
    max-width: clamp(400px, 50%, 700px) !important;
    position: relative !important;
    z-index: 2 !important;
    transform: translateZ(50px) !important;
    box-shadow: 0 30px 80px rgba(0,0,0,0.3) !important;
}}

& .intro-context-box h3 {{
    font-size: clamp(1.2rem, 2vw, 2.2rem) !important;
    font-weight: 700 !important;
    color: {colors.get('text', '#FFFFFF')} !important;
    margin-bottom: clamp(8px, 1vw, 16px) !important;
}}

& .intro-context-box p {{
    font-size: clamp(1rem, 1.2vw, 1.4rem) !important;
    color: rgba(255,255,255,0.8) !important;
    line-height: 1.8 !important;
    margin-bottom: clamp(16px, 2vw, 32px) !important;
}}

& .cta-button {{
    background: linear-gradient(135deg, {colors.get('accent', '#FF0000')} 0%, {colors.get('secondary', '#333333')} 100%) !important;
    border: none !important;
    padding: clamp(12px, 1.5vw, 20px) clamp(24px, 3vw, 48px) !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: clamp(1px, 0.1em, 3px) !important;
    font-size: clamp(0.8rem, 1vw, 1.1rem) !important;
    border-radius: clamp(8px, 1vw, 50px) !important;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    box-shadow: 0 4px 20px rgba({colors.get('accent', '#FF0000').replace('#', '')}, 0.4) !important;
    color: #ffffff !important;
    cursor: pointer !important;
}}

& .cta-button:hover {{
    transform: translateY(-4px) scale(1.05) !important;
    box-shadow: 0 12px 40px rgba({colors.get('accent', '#FF0000').replace('#', '')}, 0.6) !important;
    background: linear-gradient(135deg, {colors.get('secondary', '#333333')} 0%, {colors.get('accent', '#FF0000')} 100%) !important;
}}

@keyframes heroPulse_{industry[:8]} {{
    0%, 100% {{ transform: scale(1) rotate(0deg); opacity: 0.15; }}
    50% {{ transform: scale(1.3) rotate(10deg); opacity: 0.25; }}
}}

@keyframes heroFloat_{industry[:8]} {{
    0%, 100% {{ transform: translate(0, 0) rotate(0deg); }}
    33% {{ transform: translate(30px, -30px) rotate(5deg); }}
    66% {{ transform: translate(-20px, 20px) rotate(-5deg); }}
}}"

================================================================================
OUTPUT FORMAT - STRICT JSON - FORTUNE 500 STANDARD
================================================================================

Generate a COMPLETE JSON object with this EXACT structure:

{{
  "home": {{
    "text_contents": {{
      "1": "YOUR CREATIVE BRAND NAME",
      "2": "UNIQUE BOOKMARKS TEXT",
      // ... ALL text elements (1-46, 100-108)
    }},
    "style_customizations": {{
      "1": {{
        "background_color": "{colors.get('primary', '#000000')}",
        "text_color": "{colors.get('text', '#FFFFFF')}",
        "font_family": "{theme['fonts']['display']}",
        "custom_css": "& {{ /* FORTUNE 500 LEVEL CSS */ }}"
      }},
      // ... ALL sections (1-62, 100-111)
    }}
  }}
}}

================================================================================
START YOUR JSON OUTPUT NOW - FORTUNE 500 QUALITY REQUIRED
================================================================================

REMEMBER: Generate ALL sections (1-62, 100-111) with COMPLETE custom_css.
Make the design look like it was created by a top-tier design agency.
Use complex CSS techniques. Be creative. Be bold. Make it stunning.

OUTPUT ONLY VALID JSON. NO EXPLANATIONS.
"""
        
        return prompt
    
    def _get_style_colors(self, style):
        """Get colors for a style"""
        colors = {
            'minimalist_architectural': {
                'primary': '#1e3a5f', 'secondary': '#2d5a7a', 
                'accent': '#4a7a9a', 'bg': '#ffffff', 
                'text': '#1a2a3a', 'bg_alt': '#f5f8fa'
            },
            'dark_luxury': {
                'primary': '#0a0a0a', 'secondary': '#1a1a2e',
                'accent': '#c9a959', 'bg': '#0d0d0d',
                'text': '#f5f0e8', 'bg_alt': '#1a1a1a'
            },
            'bold_vibrant': {
                'primary': '#0d0d0d', 'secondary': '#1a1a2e',
                'accent': '#ff006e', 'bg': '#1a1a2e',
                'text': '#ffffff', 'bg_alt': '#2a2a3a'
            },
            'organic_earthy': {
                'primary': '#2d5a27', 'secondary': '#4a7a44',
                'accent': '#d4877a', 'bg': '#f5ede4',
                'text': '#2d3a2d', 'bg_alt': '#e8e0d5'
            },
            'playful_whimsical': {
                'primary': '#ff6b6b', 'secondary': '#ffd93d',
                'accent': '#6bcb77', 'bg': '#fff5f5',
                'text': '#2d2d2d', 'bg_alt': '#ffe8e8'
            }
        }
        return colors.get(style, colors['minimalist_architectural'])
    
    def _parse_response(self, response_text):
        """Parse the AI response"""
        text = response_text.strip()
        
        # Extract JSON
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0].strip()
        elif '```' in text:
            text = text.split('```')[1].split('```')[0].strip()
        
        return json.loads(text)
    
    def _validate_and_enhance_customizations(self, customizations):
        """Validate and enhance customizations with professional touches"""
        if 'home' not in customizations:
            customizations = {'home': customizations}
        
        if 'text_contents' not in customizations['home']:
            customizations['home']['text_contents'] = {}
        
        if 'style_customizations' not in customizations['home']:
            customizations['home']['style_customizations'] = {}
        
        # Ensure all sections exist
        all_section_ids = []
        for group_data in ELEMENT_REGISTRY.values():
            all_section_ids.extend(group_data.get('sections', []))
        
        for section_id in all_section_ids:
            if section_id not in customizations['home']['style_customizations']:
                customizations['home']['style_customizations'][section_id] = {
                    'background_color': '#ffffff',
                    'text_color': '#000000',
                    'font_family': "'Inter', sans-serif",
                    'custom_css': f"& {{ /* Section {section_id} - Add custom CSS here */ }}"
                }
            elif 'custom_css' not in customizations['home']['style_customizations'][section_id]:
                customizations['home']['style_customizations'][section_id]['custom_css'] = ''
        
        # Ensure all text elements exist
        text_ids = [str(i) for i in list(range(1, 47)) + list(range(100, 109))]
        for text_id in text_ids:
            if text_id not in customizations['home']['text_contents']:
                customizations['home']['text_contents'][text_id] = f'Text {text_id}'
        
        return customizations
    
    def _get_complete_fallback(self, store_name, industry, style, palette):
        """Generate a complete fallback design with professional quality"""
        colors = self._get_style_colors(style)
        theme = CREATIVE_THEMES.get(style, CREATIVE_THEMES['minimalist_architectural'])
        
        # Generate text contents with industry content
        ic = INDUSTRY_CONTENT.get(industry, INDUSTRY_CONTENT.get('other', {}))
        
        text_contents = {
            '1': store_name.upper(),
            '2': '★ SAVE',
            '3': '🛒 CART',
            '4': '→ JOIN',
            '5': '→ LOGIN',
            '6': '📦 ORDERS',
            '7': '🚪 LOGOUT',
            '8': ic.get('subtitle', 'YOUR BRAND. YOUR STORY.'),
            '9': f'THE {store_name.upper()} EXPERIENCE',
            '10': ic.get('desc', 'Discover our curated collection of premium products.'),
            '11': ic.get('collection', '✦ COLLECTIONS'),
            '12': 'SELECT SIZE:',
            '13': 'SELECT COLOR:',
            '14': '★ REVIEWS',
            '15': 'SHARE YOUR THOUGHTS',
            '16': 'Your Name',
            '17': '★★★★★',
            '18': 'Write your review...',
            '19': 'SUBMIT →',
            '20': '⚡ FAQ',
            '21': ic.get('f1', 'What makes this unique?'),
            '22': 'Every piece is crafted with premium materials and attention to detail.',
            '23': ic.get('f2', 'Shipping policy?'),
            '24': 'Fast tracked shipping with orders arriving in 3-5 business days.',
            '25': 'YOUR CART',
            '26': 'TOTAL:',
            '27': 'CHECKOUT →',
            '28': 'SAVED ITEMS',
            '29': 'VIEW CART',
            '30': 'CHECKOUT →',
            '31': store_name.upper(),
            '32': ic.get('footer', 'Quality, craftsmanship, and integrity in everything we do.'),
            '33': 'EXPLORE',
            '34': 'BACK TO TOP ↑',
            '35': f'© 2024 {store_name}. All rights reserved.',
            '36': 'v3.0 | Design Studio',
            '37': 'CONTACT',
            '38': "Let's Connect",
            '39': f'{store_name}\n123 Design District\nNYC 10001\nhello@{store_name.lower().replace(" ", "")}.com',
            '40': 'Full Name',
            '41': 'Full Name',
            '42': 'Email Address',
            '43': 'Email Address',
            '44': 'Your Message',
            '45': 'Your Message',
            '46': 'SEND →',
            '100': ic.get('p1', 'PREMIUM').split('|')[0],
            '101': ic.get('p1', 'Signature Item').split('|')[1],
            '102': ic.get('p1', '$99').split('|')[2],
            '103': ic.get('p2', 'ESSENTIAL').split('|')[0],
            '104': ic.get('p2', 'Classic Piece').split('|')[1],
            '105': ic.get('p2', '$79').split('|')[2],
            '106': ic.get('p3', 'BASIC').split('|')[0],
            '107': ic.get('p3', 'Essential Item').split('|')[1],
            '108': ic.get('p3', '$49').split('|')[2],
        }
        
        # Generate style customizations with professional CSS
        style_customizations = {}
        all_section_ids = []
        for group_data in ELEMENT_REGISTRY.values():
            all_section_ids.extend(group_data.get('sections', []))
        
        # Create a professional base CSS
        base_css = f"""
& {{
    background: {colors.get('bg', '#ffffff')} !important;
    color: {colors.get('text', '#000000')} !important;
    padding: clamp(20px, 4vw, 60px) clamp(16px, 5%, 80px) !important;
    font-family: {theme['fonts']['body']} !important;
    position: relative !important;
}}

& h1, & h2, & h3, & .heading {{
    color: {colors.get('primary', '#000000')} !important;
    font-family: {theme['fonts']['display']} !important;
    font-weight: 700 !important;
}}

& .btn, & button, & [class*="btn"] {{
    background: linear-gradient(135deg, {colors.get('accent', '#FF0000')} 0%, {colors.get('secondary', '#333333')} 100%) !important;
    color: #ffffff !important;
    padding: clamp(10px, 1.2vw, 16px) clamp(20px, 2vw, 40px) !important;
    border: none !important;
    border-radius: clamp(4px, 0.5vw, 8px) !important;
    font-weight: 600 !important;
    transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1) !important;
    cursor: pointer !important;
}}

& .btn:hover, & button:hover, & [class*="btn"]:hover {{
    transform: translateY(-3px) scale(1.02) !important;
    box-shadow: 0 8px 30px rgba({colors.get('accent', '#FF0000').replace('#', '')}, 0.3) !important;
}}
"""
        
        for section_id in all_section_ids:
            style_customizations[section_id] = {
                'background_color': colors.get('bg', '#ffffff'),
                'text_color': colors.get('text', '#000000'),
                'font_family': theme['fonts']['body'],
                'custom_css': base_css
            }
        
        return {
            'home': {
                'text_contents': text_contents,
                'style_customizations': style_customizations
            }
        }