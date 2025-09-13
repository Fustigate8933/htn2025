from spire.presentation import *
from typing import List, Dict, Any
import os
import io
import base64

class PPTProcessor:
    def __init__(self):
        pass

    def extract_slide_image(self, slide, slide_index: int) -> str:
        try:
            print(f"Starting image conversion for slide {slide_index}")
            
            image_stream = slide.SaveAsImage()
            print(f"Image stream created for slide {slide_index}")
            
            image_bytes = image_stream.ToArray()
            print(f"Image bytes extracted for slide {slide_index}, size: {len(image_bytes)}")
            
            img_str = base64.b64encode(image_bytes).decode()
            print(f"Base64 encoding completed for slide {slide_index}")
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error converting slide {slide_index} to image: {e}")
            print(f"Full traceback: {error_details}")
            return ""

    def extract_slides(self, ppt_path: str) -> List[Dict[str, Any]]:
        presentation = None
        try:
            print(f"Loading PPT file: {ppt_path}")
            
            presentation = Presentation()
            presentation.LoadFromFile(ppt_path)
            
            print(f"PPT loaded successfully, {presentation.Slides.Count} slides found")
            
            slides_data = []
            
            for i, slide in enumerate(presentation.Slides):
                print(f"Processing slide {i + 1}...")
                
                slide_content = {
                    'id': i + 1,
                    'title': '',
                    'content': '',
                    'image': '',
                    'shapes': []
                }
                
                for shape in slide.Shapes:
                    try:
                        if hasattr(shape, "TextFrame") and shape.TextFrame is not None:
                            text = shape.TextFrame.Text.strip()
                            if text:
                                if shape.Name and "title" in shape.Name.lower():
                                    slide_content['title'] = text
                                elif not slide_content['title'] and len(text) < 100:
                                    slide_content['title'] = text
                                else:
                                    if slide_content['content']:
                                        slide_content['content'] += "\n" + text
                                    else:
                                        slide_content['content'] = text
                                
                                slide_content['shapes'].append({
                                    'type': 'text',
                                    'text': text,
                                    'name': shape.Name
                                })
                    except Exception as e:
                        print(f"Error processing shape: {e}")
                        continue
                
                # If no title found, use slide number as title
                if not slide_content['title']:
                    slide_content['title'] = f"Slide {i + 1}"
                
                print(f"Slide {i + 1} - Title: '{slide_content['title']}'")
                print(f"Slide {i + 1} - Content: '{slide_content['content']}'")
                print(f"Slide {i + 1} - Shapes: {len(slide_content['shapes'])}")
                
                print(f"Converting slide {i + 1} to image...")
                slide_content['image'] = self.extract_slide_image(slide, i + 1)
                print(f"Slide {i + 1} image conversion completed")
                
                slides_data.append(slide_content)
            
            print(f"Successfully processed {len(slides_data)} slides")
            return slides_data
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error processing PPT file: {e}")
            print(f"Full traceback: {error_details}")
            return []
        finally:
            # Ensure presentation is disposed
            if presentation is not None:
                try:
                    presentation.Dispose()
                    print("Presentation disposed successfully")
                except Exception as e:
                    print(f"Error disposing presentation: {e}")

    def generate_slide_script(self, slide_data: Dict[str, Any], style: str = "professional") -> str:
        title = slide_data.get('title', '')
        content = slide_data.get('content', '')
        
        if style == "professional":
            script = f"Now, let's discuss {title}. "
        elif style == "casual":
            script = f"Alright, so about {title}. "
        elif style == "humorous":
            script = f"Here's the fun part - {title}. "
        else:
            script = f"Moving on to {title}. "
        
        if content:
            sentences = content.split('.')
            for sentence in sentences[:3]:  # Limit to first 3 sentences
                if sentence.strip():
                    script += sentence.strip() + ". "
        
        return script.strip()

    def process_presentation(self, ppt_path: str, style: str = "professional") -> Dict[str, Any]:
        slides_data = self.extract_slides(ppt_path)
        
        if not slides_data:
            return {
                'slides': [],
                'scripts': [],
                'total_slides': 0
            }
        
        scripts = []
        for slide in slides_data:
            script = self.generate_slide_script(slide, style)
            scripts.append(script)
        
        return {
            'slides': slides_data,
            'scripts': scripts,
            'total_slides': len(slides_data)
        }

    def validate_ppt_file(self, ppt_path: str) -> bool:
        presentation = None
        try:
            if not os.path.exists(ppt_path):
                return False
            
            presentation = Presentation()
            presentation.LoadFromFile(ppt_path)
            slide_count = presentation.Slides.Count
            return slide_count > 0
            
        except Exception as e:
            print(f"PPT validation error: {e}")
            return False
        finally:
            if presentation is not None:
                try:
                    presentation.Dispose()
                except Exception as e:
                    print(f"Error disposing presentation in validation: {e}")

